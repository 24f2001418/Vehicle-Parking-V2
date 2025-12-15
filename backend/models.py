from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# ------------------------------------------------------------------- #
#  Users
# ------------------------------------------------------------------- #
class User(db.Model):
    id       = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name     = db.Column(db.String(80),  nullable=False)
    email    = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)      # store HASH!
    role     = db.Column(db.String(50),  default='user', nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    reservations = db.relationship('Reservation', backref='user', lazy=True)

    def to_dict(self):
        return {
            'id':   self.id,
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'is_active': self.is_active
        }

# ------------------------------------------------------------------- #
#  Parking lots
# ------------------------------------------------------------------- #
class ParkingLot(db.Model):
    id               = db.Column(db.Integer, primary_key=True)
    name             = db.Column(db.String(100), nullable=False)        # “prime_location_name”
    price            = db.Column(db.Float, nullable=False)              # per-hour price
    address          = db.Column(db.String(255))
    pin_code         = db.Column(db.String(10))
    number_of_spots  = db.Column(db.Integer, nullable=False)

    spots = db.relationship(
        'ParkingSpot',
        backref='lot',
        cascade='all, delete-orphan',
        lazy=True
    )

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'price': self.price,
            'address': self.address,
            'pin_code': self.pin_code,
            'number_of_spots': self.number_of_spots
        }

# ------------------------------------------------------------------- #
#  Individual parking spots
# ------------------------------------------------------------------- #
class ParkingSpot(db.Model):
    id     = db.Column(db.Integer, primary_key=True)
    lot_id = db.Column(db.Integer, db.ForeignKey('parking_lot.id'), nullable=False)
    number = db.Column(db.Integer, nullable=False)            # 1…N inside the lot
    status = db.Column(db.String(1), default='A')             # A=Available, O=Occupied

    reservations = db.relationship('Reservation', backref='spot', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'lot_id': self.lot_id,
            'number': self.number,
            'status': self.status
        }

# ------------------------------------------------------------------- #
#  Reservations
# ------------------------------------------------------------------- #
class Reservation(db.Model):
    id            = db.Column(db.Integer, primary_key=True)
    spot_id       = db.Column(db.Integer, db.ForeignKey('parking_spot.id'), nullable=False)
    user_id       = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name         = db.Column(db.String(80), nullable=False)  # reserved by user
    vehicle_plate = db.Column(db.String(20), nullable=True)
    parked_at     = db.Column(db.DateTime, default=datetime.utcnow)
    left_at       = db.Column(db.DateTime, nullable=True)
    cost          = db.Column(db.Float, nullable=True)
    remarks       = db.Column(db.String(255), nullable=True)

    def to_dict(self):
     return {
        "id": self.id,
        "spot_number": self.spot.number if self.spot else None,
        "lot_name": self.spot.lot.name if self.spot and self.spot.lot else None,
        "lot_address": self.spot.lot.address if self.spot and self.spot.lot else None,
        "parked_at": self.parked_at.isoformat() if self.parked_at else None,
        "left_at": self.left_at.isoformat() if self.left_at else None,
        "cost": self.cost,
    }