# api.py  (or wherever you mount your Api)
from flask_restful import Resource, reqparse
from flask import request, current_app, send_file
from flask_jwt_extended import (
    create_access_token, jwt_required, get_jwt_identity
)
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from models import db, User, ParkingLot, ParkingSpot, Reservation
from tasks import reservations_for_user_month, make_csv_for_reservations, make_pdf_for_reservations


# --------------------------------------------------------------------- #
#  helpers
# --------------------------------------------------------------------- #
def is_admin():
    identity = get_jwt_identity()
    user = User.query.filter_by(email=identity).first()
    return bool(user and user.role == 'admin')


def get_cache():
    """Return the Flask-Caching Cache instance if available, otherwise None.
    Some environments register the cache extension as a dict; handle both cases.
    """
    ext = current_app.extensions.get('cache')
    if not ext:
        return None
    # If extension is a dict (some versions/register patterns), find the Cache instance inside
    if isinstance(ext, dict):
        for v in ext.values():
            if hasattr(v, 'get') and hasattr(v, 'set') and hasattr(v, 'delete'):
                return v
        return None
    # If ext itself looks like a Cache instance
    if hasattr(ext, 'get') and hasattr(ext, 'set'):
        return ext
    return None

# --------------------------------------------------------------------- #
#  Auth
# --------------------------------------------------------------------- #
class LoginResource(Resource):
    def post(self):
        data = request.get_json()
        email = data.get('email', None)
        password = data.get('password', None)

        if not email or not password:
            return {'msg': 'Missing credentials'}, 400

        user = User.query.filter_by(email=email).first()

        if not user or not check_password_hash(user.password, password):
            return {'msg': 'Invalid credentials'}, 400

        token = create_access_token(identity=user.email)

        return {
            'msg': 'Logged in',
            'token': token,
            'user': user.to_dict()
        }, 200


class RegisterResource(Resource):
    def post(self):
        data = request.get_json()
        name = data.get('name')
        email = data.get('email')
        password = data.get('password')

        if not all([name, email, password]):
            return {'msg': 'Missing fields'}, 400

        if User.query.filter_by(email=email).first():
            return {'msg': 'User already exists'}, 400

        # Securely hash the password using scrypt
        hashed_password = generate_password_hash(password, method='scrypt')

        user = User(name=name, email=email, password=hashed_password)
        db.session.add(user)
        db.session.commit()

        return {'msg': 'Registration successful'}, 201

# --------------------------------------------------------------------- #
#  Parking lots (admin CRUD)
# --------------------------------------------------------------------- #
class ParkingLotResource(Resource):
    @jwt_required()
    def get(self, lot_id=None):
        cache = get_cache()
        if lot_id:
            key = f'lot:{lot_id}'
            if cache:
                cached = cache.get(key)
                if cached:
                    return {'lot': cached}
            lot = ParkingLot.query.get(lot_id)
            if not lot:
                return {'msg': 'Lot not found'}, 404
            data = lot.to_dict()
            if cache:
                cache.set(key, data)
            return {'lot': data}
        # list all
        if cache:
            cached = cache.get('lots')
            if cached:
                return {'lots': cached}
        lots = [l.to_dict() for l in ParkingLot.query.all()]
        if cache:
            cache.set('lots', lots)
        return {'lots': lots}

    @jwt_required()
    def post(self):
        if not is_admin():
            return {'msg': 'Not authorized'}, 401

        data = request.get_json()
        name   = data.get('name')
        price  = data.get('price')
        addr   = data.get('address')
        pin    = data.get('pin_code')
        spots  = data.get('number_of_spots')
        if not all([name, price, spots]):
            return {'msg': 'Missing required fields'}, 400

        lot = ParkingLot(name=name, price=price, address=addr,
                         pin_code=pin, number_of_spots=spots)
        db.session.add(lot)
        db.session.flush()

        db.session.add_all([
            ParkingSpot(lot_id=lot.id, number=i, status='A')
            for i in range(1, spots + 1)
        ])
        db.session.commit()
        # invalidate cache
        try:
            cache = get_cache()
            if cache:
                cache.delete('lots')
                cache.delete(f'spots:{lot.id}')
        except Exception:
            pass
        return {'msg': 'Lot created', 'lot': lot.to_dict()}, 201

    @jwt_required()
    def put(self, lot_id):
        if not is_admin():
            return {'msg': 'Not authorized'}, 401
        lot = ParkingLot.query.get(lot_id)
        if not lot:
            return {'msg': 'Lot not found'}, 404

        data = request.get_json()
        lot.name    = data.get('name', lot.name)
        lot.price   = float(data.get('price', lot.price))
        lot.address = data.get('address', lot.address)
        lot.pin_code= data.get('pin_code', lot.pin_code)
        if 'number_of_spots' in data and int(data['number_of_spots']) != lot.number_of_spots:
            return {'msg': 'Updating capacity not supported'}, 400
        db.session.commit()
        # invalidate cache
        try:
            cache = get_cache()
            if cache:
                cache.delete('lots')
                cache.delete(f'spots:{lot.id}')
        except Exception:
            pass
        return {'msg': 'Lot updated', 'lot': lot.to_dict()}, 200

    @jwt_required()
    def delete(self, lot_id):
        if not is_admin():
            return {'msg': 'Not authorized'}, 401

        # Block if any spot is Reserved or Occupied
        active = Reservation.query.join(ParkingSpot).filter(
            ParkingSpot.lot_id == lot_id,
            Reservation.left_at.is_(None)
        ).count()
        if active:
            return {'msg': 'Lot has active reservations; cannot delete'}, 400

        lot = ParkingLot.query.get_or_404(lot_id)
        db.session.delete(lot)
        db.session.commit()
        try:
            cache = get_cache()
            if cache:
                cache.delete('lots')
                cache.delete(f'spots:{lot_id}')
        except Exception:
            pass
        return {'msg': 'Lot deleted'}, 200

# --------------------------------------------------------------------- #
#  Spot status (view only)
# --------------------------------------------------------------------- #
class SpotStatusResource(Resource):
    @jwt_required(optional=True)
    def get(self, lot_id=None):
        cache = get_cache()
        if lot_id and cache:
            key = f'spots:{lot_id}'
            cached = cache.get(key)
            if cached:
                return {'spots': cached}
        q = ParkingSpot.query
        if lot_id:
            q = q.filter_by(lot_id=lot_id)
        spots = q.all()

        def spot_dict(s):
            d = s.to_dict()

            if s.status in ('O', 'R'):  # Reserved or Occupied
               res = Reservation.query.filter_by(spot_id=s.id).order_by(
                     Reservation.parked_at.desc()
                ).first()
               if res and res.user:
                 d.update({
                'user_id': res.user_id,
                'user_name': res.user.name,
                'user_email': res.user.email,
                'vehicle_plate': res.vehicle_plate,
                'parked_at': res.parked_at.isoformat() if res.parked_at else None
                })
            return d

        result = [spot_dict(s) for s in spots]
        if lot_id and cache:
            cache.set(f'spots:{lot_id}', result)
        return {'spots': result}

class AvailableSpotsResource(Resource):
    @jwt_required(optional=True)
    def get(self, lot_id):
        free_spots = (
            ParkingSpot.query
            .filter_by(lot_id=lot_id, status='A')
            .order_by(ParkingSpot.number)
            .all()
        )
        return {
            "spots": [{"id": s.id, "number": s.number} for s in free_spots]
        }, 200

class ReservationListResource(Resource):
    @jwt_required()
    def post(self):
        p = reqparse.RequestParser()
        p.add_argument("lot_id",        type=int,  required=True, location="json")
        # spot_id may be omitted for 'assign-first-available' flows
        p.add_argument("spot_id",       type=int,  required=False, location="json")
        # name and vehicle_plate are optional for auto-book flows; default to user.name / None
        p.add_argument("name",          type=str,  required=False, location="json")
        p.add_argument("vehicle_plate", type=str,  required=False, location="json")
        args = p.parse_args()

        spot = None
        # If spot_id provided, use that spot (validate availability)
        if args.get("spot_id"):
            spot = ParkingSpot.query.get_or_404(args["spot_id"])
            if spot.status != "A":
                return {"msg": "Spot not available"}, 400
        else:
            # find first available spot in the requested lot
            spot = (
                ParkingSpot.query
                .filter_by(lot_id=args["lot_id"], status='A')
                .order_by(ParkingSpot.number)
                .first()
            )
            if not spot:
                return {"msg": "No available spots in this lot"}, 400

        user = User.query.filter_by(email=get_jwt_identity()).first()

        # Use provided name/vehicle_plate if present, otherwise default to user's name / None
        name = args.get("name") or (user.name if user else "Guest")
        vehicle_plate = args.get("vehicle_plate") or None

        res = Reservation(
            user_id=user.id,
            spot_id=spot.id,
            name=name,
            vehicle_plate=vehicle_plate,
            parked_at=None,
            left_at=None,
            cost=None,
            remarks="Reserved",
        )

        spot.status = "R"
        db.session.add(res)
        db.session.commit()

        # Invalidate caches for this lot
        try:
            cache = get_cache()
            if cache:
                cache.delete(f'spots:{spot.lot_id}')
                cache.delete('lots')
        except Exception:
            pass

        return {"reservation": res.to_dict(), "spot": spot.to_dict()}, 201

class ReservationStartResource(Resource):
    @jwt_required()
    def put(self, reservation_id):
        res: Reservation = Reservation.query.get_or_404(reservation_id)
        if res.parked_at:
            return {"msg": "Already started"}, 400

        spot: ParkingSpot = ParkingSpot.query.get_or_404(res.spot_id)

        res.parked_at = datetime.utcnow()
        res.remarks = "Occupied"
        spot.status = "O"

        db.session.commit()

        # invalidate cache
        try:
            cache = get_cache()
            if cache:
                cache.delete(f'spots:{spot.lot_id}')
                cache.delete('lots')
        except Exception:
            pass

        return {
            "reservation": res.to_dict(),
            "spot": spot.to_dict(),
        }, 200

class ReservationEndResource(Resource):
    @jwt_required()
    def put(self, reservation_id):
        res: Reservation = Reservation.query.get_or_404(reservation_id)
        if not res.parked_at or res.left_at:
            return {"msg": "Invalid state"}, 400

        spot: ParkingSpot = ParkingSpot.query.get_or_404(res.spot_id)

        res.left_at = datetime.utcnow()
        duration_mins = (res.left_at - res.parked_at).total_seconds() / 60

        lot: ParkingLot = ParkingLot.query.get_or_404(spot.lot_id)
        res.cost = round((duration_mins / 60) * lot.price, 2)

        res.remarks = "Released"
        spot.status = "A"
        db.session.commit()

        # invalidate cache
        try:
            cache = get_cache()
            if cache:
                cache.delete(f'spots:{spot.lot_id}')
                cache.delete('lots')
        except Exception:
            pass

        return {
            "reservation": res.to_dict(),
            "payment": {
                "amount": res.cost,
                "currency": "INR",
                "methods": ["UPI", "CreditCard", "Cash"]
            }
        }, 200
    
class ReservationHistoryResource(Resource):
    @jwt_required()
    def get(self):
        user = User.query.filter_by(email=get_jwt_identity()).first()
        if not user:
            return {"msg": "Invalid user"}, 401

        reservations = Reservation.query.filter_by(user_id=user.id).order_by(Reservation.parked_at.desc()).all()

        return {
            "reservations": [r.to_dict() for r in reservations]
        }
    
class UsersResource(Resource):
    @jwt_required()
    def get(self):
        if not is_admin():
            return {'msg': 'Not authorized'}, 401
        users = [u.to_dict() for u in User.query.all()]
        return {'users': users}


class ReportsResource(Resource):
    @jwt_required()
    def get(self):
        # Download user's bookings for a month as CSV or PDF
        args = request.args
        month = args.get('month')  # expected YYYY-MM
        fmt = args.get('format', 'csv')
        user_id = args.get('user_id')

        # validate month
        if not month:
            return {'msg': 'Missing month parameter (YYYY-MM)'}, 400
        try:
            year, mon = map(int, month.split('-'))
        except Exception:
            return {'msg': 'Invalid month format; expected YYYY-MM'}, 400

        # determine target user: admin may specify user_id
        if user_id:
            if not is_admin():
                return {'msg': 'Not authorized'}, 401
            target = User.query.get(int(user_id))
            if not target:
                return {'msg': 'User not found'}, 404
        else:
            target = User.query.filter_by(email=get_jwt_identity()).first()
            if not target:
                return {'msg': 'Invalid user'}, 401

        reservations = reservations_for_user_month(target.id, year, mon)

        if fmt == 'csv':
            csv_bytes = make_csv_for_reservations(reservations)
            return (csv_bytes, 200, {
                'Content-Type': 'text/csv',
                'Content-Disposition': f'attachment; filename="bookings_{target.id}_{year:04d}-{mon:02d}.csv"'
            })
        elif fmt == 'pdf':
            pdf_bytes = make_pdf_for_reservations(reservations)
            return (pdf_bytes, 200, {
                'Content-Type': 'application/pdf',
                'Content-Disposition': f'attachment; filename="bookings_{target.id}_{year:04d}-{mon:02d}.pdf"'
            })
        else:
            return {'msg': 'Unsupported format'}, 400


class ReportsExportResource(Resource):
    @jwt_required()
    def post(self):
        # Trigger an async export (CSV/PDF) via Celery
        data = request.get_json() or {}
        month = data.get('month')  # optional YYYY-MM
        fmt = data.get('format', 'csv')
        user_id = data.get('user_id')

        # determine target
        if user_id:
            if not is_admin():
                return {'msg': 'Not authorized'}, 401
            target = User.query.get(int(user_id))
            if not target:
                return {'msg': 'User not found'}, 404
        else:
            target = User.query.filter_by(email=get_jwt_identity()).first()
            if not target:
                return {'msg': 'Invalid user'}, 401

        # enqueue celery task (import locally to avoid circular imports)
        try:
            from celery_tasks import export_user_report_task
            task = export_user_report_task.apply_async(args=(target.id, month, fmt))
            return {'task_id': task.id}, 202
        except Exception as e:
            current_app.logger.error(f"Failed to enqueue export task: {e}")
            return {'msg': 'Failed to start export'}, 500


class ReportsStatusResource(Resource):
    @jwt_required()
    def get(self, task_id):
        # Check Celery task status
        try:
            from celery_tasks import celery
            res = celery.AsyncResult(task_id)
            info = {'state': res.state}
            if res.state == 'SUCCESS':
                result = res.result
                # result should be dict with 'files': [filenames]
                info['result'] = result
                # build download urls
                files = result.get('files') if isinstance(result, dict) else None
                if files:
                    base = request.host_url.rstrip('/')
                    info['download_urls'] = [f"{base}/api/reports/download/{f}" for f in files]
            elif res.state == 'FAILURE':
                info['error'] = str(res.result)
            return info
        except Exception as e:
            current_app.logger.error(f"Error checking task status: {e}")
            return {'msg': 'Error checking task status'}, 500


class ReportsDownloadResource(Resource):
    @jwt_required()
    def get(self, filename):
        # Serve generated report files from reports dir (protected)
        import os, re
        safe = os.path.basename(filename)
        reports_dir = os.path.join(current_app.root_path, 'reports')
        path = os.path.join(reports_dir, safe)
        if not os.path.exists(path):
            return {'msg': 'File not found'}, 404

        # verify user ownership unless admin
        target = User.query.filter_by(email=get_jwt_identity()).first()
        if not target:
            return {'msg': 'Invalid user'}, 401

        m = re.match(r'bookings_(\d+)_', safe)
        if m:
            owner_id = int(m.group(1))
            if owner_id != target.id and not is_admin():
                return {'msg': 'Not authorized'}, 401

        return send_file(path, as_attachment=True)



class UserActivateResource(Resource):
    @jwt_required()
    def put(self, user_id):
        if not is_admin():
            return {'msg': 'Not authorized'}, 401
        
        user = User.query.get(user_id)
        if not user:
            return {'msg': 'User not found'}, 404
        
        if user.role == 'admin':
            return {'msg': 'Cannot activate admin users'}, 400
        
        user.is_active = True
        db.session.commit()
        
        return {'msg': 'User activated', 'user': user.to_dict()}, 200

class UserDeactivateResource(Resource):
    @jwt_required()
    def put(self, user_id):
        if not is_admin():
            return {'msg': 'Not authorized'}, 401
        
        user = User.query.get(user_id)
        if not user:
            return {'msg': 'User not found'}, 404
        
        if user.role == 'admin':
            return {'msg': 'Cannot deactivate admin users'}, 400
        
        user.is_active = False
        db.session.commit()
        
        return {'msg': 'User deactivated', 'user': user.to_dict()}, 200

class UserDeleteResource(Resource):
    @jwt_required()
    def delete(self, user_id):
        if not is_admin():
            return {'msg': 'Not authorized'}, 401
        
        user = User.query.get(user_id)
        if not user:
            return {'msg': 'User not found'}, 404
        
        if user.role == 'admin':
            return {'msg': 'Cannot delete admin users'}, 400
        
        # Delete all reservations related to this user
        Reservation.query.filter_by(user_id=user_id).delete()
        
        db.session.delete(user)
        db.session.commit()
        
        return {'msg': 'User deleted'}, 200