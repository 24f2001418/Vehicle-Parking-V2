#
# Celery & Mailhog Setup
#

## Requirements
- Redis server running (default: redis://localhost:6379/0)
- Mailhog running (default: http://localhost:8025, SMTP on 1025)

## Start Mailhog
```
Mailhog
# or use Docker:
docker run --rm -p 8025:8025 -p 1025:1025 mailhog/mailhog
```
## Start Redis
```
redis-server
# or use Docker:
docker run --rm -p 6379:6379 redis
```

## Start Celery Worker & Beat
```
cd backend
celery -A tasks.celery worker --loglevel=info
celery -A tasks.celery beat --loglevel=info
```

## Test Email
All emails sent by the app will appear in the Mailhog web UI at http://localhost:8025

# Celery and Redis are used for background processing.
# Daily and monthly tasks are scheduled via Celery Beat.

## CSV Export via Celery
- Users can request a CSV export of their reservation history (sent to their email).
- Admins can request a CSV export of all user performance (sent to admin email).
- Both exports are handled asynchronously by Celery and delivered via Mailhog email.

To trigger from Python (example):
```
from export_tasks import export_user_reservation_history_csv, export_admin_user_performance_csv
export_user_reservation_history_csv.delay(user_id, user_email)
export_admin_user_performance_csv.delay(admin_email)
```
All emails will appear in Mailhog (http://localhost:8025).
# Vehicle Parking-V2
Vehicle Parking V2 is a multi-user exam prep app for the MAD II course. Users can register, log in, and reserve spot. The admin manages users, lot, spot status, summary. Features include spot status, reminders, and monthly reports.
