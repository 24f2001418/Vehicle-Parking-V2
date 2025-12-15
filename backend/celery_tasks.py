from celery_app import make_celery
from app import app
from tasks import daily_reminder_job, monthly_report_job
from tasks import reservations_for_user_month, make_csv_for_reservations, make_pdf_for_reservations
from models import Reservation, User, ParkingSpot, ParkingLot
import os
from datetime import datetime

celery = make_celery(app)

# register periodic tasks via beat schedule
celery.conf.beat_schedule = {
    'daily-reminder-09-00-utc': {
        'task': 'celery_tasks.daily_reminder_task',
        'schedule': {
            'type': 'crontab',
            'minute': '0',
            'hour': '9'
        }
    },
    'monthly-report-day-1-00-05-utc': {
        'task': 'celery_tasks.monthly_report_task',
        'schedule': {
            'type': 'crontab',
            'minute': '5',
            'hour': '0',
            'day_of_month': '1'
        }
    }
}

# NOTE: Celery 5 expects entries in beat_schedule to be simple schedules; using dicts above
# provides clarity; if crontab isn't accepted, users can replace with celery.schedules.crontab
from celery.schedules import crontab
celery.conf.beat_schedule = {
    'daily-reminder-09-00-utc': {
        'task': 'celery_tasks.daily_reminder_task',
        'schedule': crontab(minute=0, hour=9),
    },
    'monthly-report-day-1-00-05-utc': {
        'task': 'celery_tasks.monthly_report_task',
        'schedule': crontab(minute=5, hour=0, day_of_month='1'),
    }
}

@celery.task(name='celery_tasks.daily_reminder_task')
def daily_reminder_task():
    # wrapper around the function in tasks.py
    daily_reminder_job()

@celery.task(name='celery_tasks.monthly_report_task')
def monthly_report_task():
    monthly_report_job()


@celery.task(name='celery_tasks.export_user_report_task')
def export_user_report_task(user_id, month=None, fmt='csv'):
    """Generate CSV or PDF for a user. If month is provided (YYYY-MM) use that month, else export all-time."""
    try:
        if month:
            try:
                year, mon = map(int, month.split('-'))
            except Exception:
                year = None
                mon = None
        else:
            year = None
            mon = None

        if year and mon:
            reservations = reservations_for_user_month(user_id, year, mon)
            stamp = f"{year:04d}-{mon:02d}"
        else:
            reservations = (
                Reservation.query
                .filter_by(user_id=user_id)
                .order_by(Reservation.parked_at.desc())
                .all()
            )
            stamp = datetime.utcnow().strftime('%Y%m%dT%H%M%S')

        reports_dir = os.path.join(app.root_path, 'reports')
        os.makedirs(reports_dir, exist_ok=True)

        files = []
        if fmt in ('csv', 'both'):
            csv_bytes = make_csv_for_reservations(reservations)
            csv_name = f"bookings_{user_id}_{stamp}.csv"
            with open(os.path.join(reports_dir, csv_name), 'wb') as f:
                f.write(csv_bytes)
            files.append(csv_name)

        if fmt in ('pdf', 'both'):
            pdf_bytes = make_pdf_for_reservations(reservations)
            pdf_name = f"bookings_{user_id}_{stamp}.pdf"
            with open(os.path.join(reports_dir, pdf_name), 'wb') as f:
                f.write(pdf_bytes)
            files.append(pdf_name)

        return {'files': files}
    except Exception as e:
        # let Celery mark task as failed with exception
        raise


# --- MailHog helper and extra tasks (booking emails, release emails, CSV export)
def send_simple_email(to_email, subject, body, html_body=None, attachment_path=None):
    """Send email via local MailHog (localhost:1025). Returns True/False."""
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    from email.mime.base import MIMEBase
    from email import encoders

    smtp_server = os.environ.get('SMTP_HOST', 'localhost')
    smtp_port = int(os.environ.get('SMTP_PORT', 1025))
    sender = os.environ.get('SMTP_FROM', 'no-reply@parkease.local')

    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body or '', 'plain'))
    if html_body:
        msg.attach(MIMEText(html_body, 'html'))

    if attachment_path and os.path.exists(attachment_path):
        with open(attachment_path, 'rb') as f:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename="{os.path.basename(attachment_path)}"')
        msg.attach(part)

    try:
        s = smtplib.SMTP(smtp_server, smtp_port)
        s.sendmail(sender, [to_email], msg.as_string())
        s.quit()
        print(f"[mail] sent to {to_email} via {smtp_server}:{smtp_port}")
        return True
    except Exception as e:
        print(f"[mail] failed to send to {to_email}: {e}")
        return False


@celery.task(name='celery_tasks.send_booking_confirmation_email')
def send_booking_confirmation_email(reservation_id):
    """Send booking confirmation using current Reservation model."""
    try:
        with app.app_context():
            res = Reservation.query.get(reservation_id)
            if not res:
                return f"Reservation {reservation_id} not found"
            user = res.user
            spot = res.spot
            lot = spot.lot if spot else None

            subject = f"Booking Confirmation - {lot.name if lot else 'Parking'}"
            start = res.parked_at.strftime('%Y-%m-%d %H:%M') if res.parked_at else 'N/A'
            end = res.left_at.strftime('%Y-%m-%d %H:%M') if res.left_at else 'Open'
            cost_text = f"Rs {res.cost:.2f}" if res.cost is not None else 'TBD'

            body = f"Dear {user.name},\n\nYour booking is confirmed.\nLot: {lot.name if lot else 'N/A'}\nSpot: {spot.number if spot else 'N/A'}\nStart: {start}\nEnd: {end}\nCost: {cost_text}\n\nThank you."

            html = f"<p>Dear <strong>{user.name}</strong>,</p>\n<ul>\n<li>Lot: {lot.name if lot else 'N/A'}</li>\n<li>Spot: {spot.number if spot else 'N/A'}</li>\n<li>Start: {start}</li>\n<li>End: {end}</li>\n<li>Cost: {cost_text}</li>\n</ul>\n<p>Thank you.</p>"

            ok = send_simple_email(user.email, subject, body, html)
            return {'sent': ok}
    except Exception as e:
        raise


@celery.task(name='celery_tasks.send_parking_release_email')
def send_parking_release_email(reservation_id):
    try:
        with app.app_context():
            res = Reservation.query.get(reservation_id)
            if not res:
                return f"Reservation {reservation_id} not found"
            user = res.user
            spot = res.spot
            lot = spot.lot if spot else None

            end_time = res.left_at or datetime.utcnow()
            duration_hours = 0
            if res.parked_at:
                duration_hours = (end_time - res.parked_at).total_seconds() / 3600

            subject = f"Parking Released - {lot.name if lot else 'Parking'}"
            body = f"Dear {user.name},\n\nYour parking session has ended.\nLot: {lot.name if lot else 'N/A'}\nSpot: {spot.number if spot else 'N/A'}\nStart: {res.parked_at.strftime('%Y-%m-%d %H:%M') if res.parked_at else 'N/A'}\nEnd: {end_time.strftime('%Y-%m-%d %H:%M')}\nDuration: {duration_hours:.2f} hours\nCost: Rs {res.cost:.2f if res.cost else 0}\n\nThank you."

            html = f"<p>Dear <strong>{user.name}</strong>,</p>\n<p>Your parking session has ended.</p>\n<ul>\n<li>Lot: {lot.name if lot else 'N/A'}</li>\n<li>Spot: {spot.number if spot else 'N/A'}</li>\n<li>Start: {res.parked_at.strftime('%Y-%m-%d %H:%M') if res.parked_at else 'N/A'}</li>\n<li>End: {end_time.strftime('%Y-%m-%d %H:%M')}</li>\n<li>Duration: {duration_hours:.2f} hours</li>\n<li>Cost: Rs {res.cost:.2f if res.cost else 0}</li>\n</ul>"

            ok = send_simple_email(user.email, subject, body, html)
            return {'sent': ok}
    except Exception as e:
        raise


@celery.task(name='celery_tasks.export_user_data_csv')
def export_user_data_csv(user_id):
    """Export user's reservations as CSV, save under app.root_path/reports/exports and email via MailHog."""
    try:
        with app.app_context():
            user = User.query.get(user_id)
            if not user:
                return {'status': 'error', 'message': 'User not found'}

            reservations = Reservation.query.filter_by(user_id=user_id).order_by(Reservation.parked_at.desc()).all()

            headers = ['Reservation ID', 'Lot', 'Spot Number', 'Name', 'Vehicle Plate', 'Start', 'End', 'Cost', 'Remarks']
            rows = []
            for r in reservations:
                rows.append([
                    r.id,
                    r.spot.lot.name if r.spot and r.spot.lot else '',
                    r.spot.number if r.spot else '',
                    r.name,
                    r.vehicle_plate or '',
                    r.parked_at.strftime('%Y-%m-%d %H:%M:%S') if r.parked_at else '',
                    r.left_at.strftime('%Y-%m-%d %H:%M:%S') if r.left_at else '',
                    f"{r.cost:.2f}" if r.cost else '',
                    r.remarks or ''
                ])

            reports_dir = os.path.join(app.root_path, 'reports', 'exports')
            os.makedirs(reports_dir, exist_ok=True)
            stamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            filename = f"parking_history_{user.id}_{stamp}.csv"
            path = os.path.join(reports_dir, filename)

            import csv
            with open(path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(headers)
                writer.writerows(rows)

            # Email to user with attachment
            subject = f"Your Parking History Export - {stamp}"
            body = f"Hi {user.name},\n\nYour parking history export is ready. Attached is the CSV file.\n\nRegards."
            sent = send_simple_email(user.email, subject, body, attachment_path=path)

            return {'status': 'success', 'file': filename, 'path': path, 'emailed': sent}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}
