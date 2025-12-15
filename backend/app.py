import os
from flask import Flask
from flask_restful import Api
from flask_jwt_extended import JWTManager
from flask_caching import Cache
from flask_cors import CORS
from werkzeug.security import generate_password_hash
from models import db, User
from controllers import (
    LoginResource, RegisterResource,
    ParkingLotResource, SpotStatusResource, UsersResource, AvailableSpotsResource,
    ReservationEndResource, ReservationStartResource, ReservationListResource,
    ReservationHistoryResource, UserActivateResource, UserDeactivateResource, UserDeleteResource,
)
from controllers import ReportsResource, ReportsExportResource, ReportsStatusResource, ReportsDownloadResource

# --------------------------------------------------------------------- #
#  Config / init
# --------------------------------------------------------------------- #
app = Flask(__name__)

# Core config
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL', 'sqlite:///parking.db'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'change-me')
# Extensions
db.init_app(app)
jwt = JWTManager(app)
# Caching (SimpleCache for dev; in production use RedisCache)
cache = Cache(config={
    'CACHE_TYPE': os.environ.get('FLASK_CACHE_TYPE', 'SimpleCache'),
    'CACHE_DEFAULT_TIMEOUT': int(os.environ.get('CACHE_DEFAULT_TIMEOUT', 60))
})
cache.init_app(app)
api = Api(app)
CORS(app, resources={r"/api/*": {"origins": "*"}})   # dev-friendly CORS

# --------------------------------------------------------------------- #
#  Routes
# --------------------------------------------------------------------- #
# Auth
api.add_resource(LoginResource,    '/api/auth/login')
api.add_resource(RegisterResource, '/api/auth/register')

# Parking lots CRUD
api.add_resource(ParkingLotResource,
                 '/api/lots', '/api/lots/<int:lot_id>')

# Spot status
api.add_resource(SpotStatusResource,
                 '/api/spots', '/api/spots/<int:lot_id>')

# Admin view of users
api.add_resource(UsersResource, '/api/users')
api.add_resource(UserActivateResource, '/api/users/<int:user_id>/activate')
api.add_resource(UserDeactivateResource, '/api/users/<int:user_id>/deactivate')
api.add_resource(UserDeleteResource, '/api/users/<int:user_id>')
api.add_resource(ReportsResource, '/api/reports/bookings')
api.add_resource(ReportsExportResource, '/api/reports/export')
api.add_resource(ReportsStatusResource, '/api/reports/status/<string:task_id>')
api.add_resource(ReportsDownloadResource, '/api/reports/download/<string:filename>')

api.add_resource(
    AvailableSpotsResource,
    "/api/lots/<int:lot_id>/available_spots"
)
api.add_resource(ReservationListResource,  '/api/reservations')
api.add_resource(ReservationStartResource, '/api/reservations/<int:reservation_id>/start')
api.add_resource(ReservationEndResource,   '/api/reservations/<int:reservation_id>/end')
api.add_resource(ReservationHistoryResource, "/api/reservations")

# --------------------------------------------------------------------- #
#  CLI / main
# --------------------------------------------------------------------- #
def seed_admin():
    """Create default admin if not present."""
    admin = User.query.filter_by(email='admin@mad2.com').first()
    if not admin:
        admin = User(
            email='admin@mad2.com',
            name='Admin',
            password=generate_password_hash('12345678'),
            role='admin'
        )
        db.session.add(admin)
        db.session.commit()
        print('Admin created — email: admin@mad2.com  |  password: 12345678')

def seed_demo_users():
    """Optional demo users — comment out if not needed."""
    if not User.query.filter_by(role='user').first():
        demo_users = [
            User(email=f'user{i}@mad2.com',
                 name=f'User{i}',
                 password=generate_password_hash('12345678'))
            for i in range(4)
        ]
        db.session.add_all(demo_users)
        db.session.commit()
        print('Demo users created.')

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        seed_admin()
        # seed_demo_users()   # uncomment if you want sample users
        # Scheduler is now handled externally via Celery + Celery Beat

    app.run(debug=True)
