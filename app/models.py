from app import db
from datetime import datetime
class User(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(100),nullable=False)
    email=db.Column(db.String(100),unique=True,nullable=False)
    password=db.Column(db.String(200),nullable=False)
    role=db.Column(db.String(20),nullable=False,default='Trekker')
    is_active=db.Column(db.Boolean,default=True)
    profile_pic=db.Column(db.String(200),nullable=True,default='default.png')
    bookings=db.relationship('Booking',back_populates='user',lazy=True)
    staff_profile=db.relationship('StaffProfile',back_populates='user',uselist=False)
    
class Trek(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(100),nullable=False)
    location=db.Column(db.String(100),nullable=False)
    difficulty=db.Column(db.String(20),nullable=False,default='Moderate')
    duration=db.Column(db.Integer,nullable=False)
    available_slots=db.Column(db.Integer,nullable=False)
    total_slots=db.Column(db.Integer,nullable=False)
    start_date=db.Column(db.DateTime,nullable=False)
    end_date=db.Column(db.DateTime,nullable=False)
    status=db.Column(db.String(20),nullable=False,default='Pending')
    assigned_staff_id=db.Column(db.Integer,db.ForeignKey("user.id"),nullable=True)
    description=db.Column(db.String(1000),nullable=True)
    bookings=db.relationship('Booking',back_populates='trek',lazy=True)
    assigned_staff=db.relationship('User',foreign_keys=[assigned_staff_id])

class Booking(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    user_id=db.Column(db.Integer,db.ForeignKey("user.id"),nullable=False)
    trek_id=db.Column(db.Integer,db.ForeignKey("trek.id"),nullable=False)
    booking_date=db.Column(db.DateTime,default=datetime.utcnow)
    status=db.Column(db.String(20),default='Booked')
    user=db.relationship('User',back_populates='bookings')
    trek=db.relationship('Trek',back_populates='bookings')
    
class StaffProfile(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    user_id=db.Column(db.Integer,db.ForeignKey("user.id"),nullable=False,unique=True)
    contact=db.Column(db.String(15),nullable=False,unique=True)
    bio=db.Column(db.String(500),nullable=True)
    rating=db.Column(db.Float,default=0.0)
    user=db.relationship('User',back_populates='staff_profile')