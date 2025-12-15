from flask import current_app
from datetime import datetime, timedelta, date
from models import db, Reservation, User, ParkingSpot, ParkingLot
import os
import csv
from io import BytesIO, StringIO
import smtplib
from email.message import EmailMessage


def send_email(to_email, subject, body, attachments=None):
    # attachments: list of tuples (filename, bytes, mime)
    # Default to MailHog for local dev if no SMTP env is provided
    smtp_host = os.environ.get('SMTP_HOST', 'localhost')
    smtp_port = int(os.environ.get('SMTP_PORT', 1025))
    smtp_user = os.environ.get('SMTP_USER')
    smtp_pass = os.environ.get('SMTP_PASS')
    sender = smtp_user or os.environ.get('SMTP_FROM', 'no-reply@parkease.local')

    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = to_email
    msg.set_content(body)

    if attachments:
        for filename, data, mime in attachments:
            maintype, subtype = mime.split('/', 1)
            msg.add_attachment(data, maintype=maintype, subtype=subtype, filename=filename)

    try:
        with smtplib.SMTP(smtp_host, smtp_port) as s:
            # For MailHog (local dev) there's no TLS/auth; attempt starttls only if server supports it
            try:
                s.starttls()
            except Exception:
                pass
            # If credentials provided, try to login
            if smtp_user and smtp_pass:
                try:
                    s.login(smtp_user, smtp_pass)
                except Exception:
                    current_app.logger.warning('SMTP login failed; continuing without auth')
            s.send_message(msg)
        current_app.logger.info(f"Sent email to {to_email}: {subject} via {smtp_host}:{smtp_port}")
        return True
    except Exception as e:
        current_app.logger.error(f"Failed to send email to {to_email}: {e}")
        return False


def reservations_for_user_month(user_id, year, month):
    start = datetime(year, month, 1)
    if month == 12:
        end = datetime(year + 1, 1, 1)
    else:
        end = datetime(year, month + 1, 1)

    q = (
        Reservation.query
        .filter(Reservation.user_id == user_id)
        .filter(
            ((Reservation.parked_at >= start) & (Reservation.parked_at < end))
            | (((Reservation.left_at != None) & (Reservation.left_at >= start) & (Reservation.left_at < end)))
        )
        .order_by(Reservation.parked_at.desc())
    )
    return q.all()


def make_csv_for_reservations(reservations):
    out = StringIO()
    writer = csv.writer(out)
    writer.writerow(['Reservation ID', 'Lot', 'Spot Number', 'Name', 'Vehicle Plate', 'Parked At', 'Left At', 'Cost', 'Remarks'])
    for r in reservations:
        writer.writerow([
            r.id,
            r.spot.lot.name if r.spot and r.spot.lot else '',
            r.spot.number if r.spot else '',
            r.name,
            r.vehicle_plate or '',
            r.parked_at.isoformat() if r.parked_at else '',
            r.left_at.isoformat() if r.left_at else '',
            r.cost if r.cost is not None else '',
            r.remarks or ''
        ])
    return out.getvalue().encode('utf-8')


def make_pdf_for_reservations(reservations):
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
    except Exception:
        try:
            current_app.logger.warning('reportlab not installed; PDF generation skipped')
        except Exception:
            pass
        return b''

    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    width, height = letter
    y = height - 40
    c.setFont('Helvetica-Bold', 14)
    c.drawString(40, y, 'Monthly Reservations Report')
    y -= 30
    c.setFont('Helvetica', 10)
    for r in reservations:
        line = f"#{r.id} - Lot: {r.spot.lot.name if r.spot and r.spot.lot else '-'} | Spot: {r.spot.number if r.spot else '-'} | Name: {r.name} | Vehicle: {r.vehicle_plate or '-'} | Parked: {r.parked_at.isoformat() if r.parked_at else '-'} | Left: {r.left_at.isoformat() if r.left_at else '-'} | Cost: {r.cost if r.cost is not None else '-'}"
        c.drawString(40, y, line[:120])
        y -= 14
        if y < 60:
            c.showPage()
            y = height - 40
    c.save()
    buf.seek(0)
    return buf.read()


def daily_reminder_job():
    # Remind users with active reservations (parked_at set, left_at is None)
    with current_app.app_context():
        now = datetime.utcnow()
        active = Reservation.query.filter(Reservation.parked_at != None, Reservation.left_at == None).all()
        for r in active:
            try:
                user = r.user
                spot = r.spot
                lot = spot.lot if spot else None
                subject = 'Parking Reminder: Active Reservation'
                body = f"Hi {user.name},\n\nYou have an active parking at {lot.name if lot else 'Unknown lot'} - spot {spot.number if spot else 'N/A'}.\nPlease remember to release the spot when done.\n\nStarted at: {r.parked_at.isoformat() if r.parked_at else 'N/A'}\n\nThanks." 
                send_email(user.email, subject, body)
            except Exception as e:
                current_app.logger.error(f"Error sending reminder for reservation {r.id}: {e}")


def monthly_report_job():
    # Generate CSV/PDF monthly reports for each user for the previous month
    with current_app.app_context():
        today = date.today()
        # previous month
        first_of_this_month = date(today.year, today.month, 1)
        prev_month_last_day = first_of_this_month - timedelta(days=1)
        year = prev_month_last_day.year
        month = prev_month_last_day.month

        reports_dir = os.path.join(current_app.root_path, 'reports')
        os.makedirs(reports_dir, exist_ok=True)

        users = User.query.all()
        for u in users:
            try:
                reservations = reservations_for_user_month(u.id, year, month)
                if not reservations:
                    continue
                csv_bytes = make_csv_for_reservations(reservations)
                pdf_bytes = make_pdf_for_reservations(reservations)
                csv_name = f"bookings_{u.id}_{year:04d}-{month:02d}.csv"
                pdf_name = f"bookings_{u.id}_{year:04d}-{month:02d}.pdf"
                with open(os.path.join(reports_dir, csv_name), 'wb') as f:
                    f.write(csv_bytes)
                with open(os.path.join(reports_dir, pdf_name), 'wb') as f:
                    f.write(pdf_bytes)
                # try emailing report to user
                subject = f"Your bookings for {year}-{month:02d}"
                body = f"Hi {u.name},\n\nAttached are your bookings for {year}-{month:02d}.\n\nRegards."
                send_email(u.email, subject, body, attachments=[(csv_name, csv_bytes, 'text/csv'), (pdf_name, pdf_bytes, 'application/pdf')])
            except Exception as e:
                current_app.logger.error(f"Error creating report for user {u.id}: {e}")


# Note: scheduling is handled by Celery + Celery Beat (or external scheduler).
# Keep the job functions (`daily_reminder_job`, `monthly_report_job`) here so
# Celery tasks can import and call them within an application context.
