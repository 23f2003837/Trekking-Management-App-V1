from flask import Blueprint,render_template,request,redirect,url_for,session,flash
from app.models import User, Trek, Booking, StaffProfile
from app import db
from werkzeug.security import generate_password_hash,check_password_hash
from app.decorators import login_as_admin, login_as_staff, login_as_trekker
from datetime import datetime

main=Blueprint('main',__name__)

@main.route("/")
def home():
    return render_template('home.html')

@main.route("/login",methods=['GET','POST'])
def login():
    if request.method=="POST":
        email=request.form["email"]
        password=request.form["password"]
        existing_user=User.query.filter_by(email=email).first()
        if existing_user:
            password_check=check_password_hash(existing_user.password,password)
            if password_check:
                if existing_user.is_blacklisted:
                    flash("You have been blacklisted by admin, Please contact admin")
                    return redirect(url_for('main.login'))
                elif not existing_user.is_approved and existing_user.role=='staff':
                    flash("Awaiting admin's approval before you can login.")
                    return redirect(url_for('main.login'))
                else:
                    flash("Successfully Login")
                    session['user_id']=existing_user.id
                    session['role']=existing_user.role
                    if session['role']=='staff':
                        return redirect(url_for("main.staff_dashboard"))
                    elif session['role']=='admin':
                        return redirect(url_for("main.admin_dashboard"))
                    else:
                        return redirect(url_for("main.trekker_dashboard"))
            else:
                flash("Incorrect Password")
                return redirect(url_for("main.login"))
        flash("Please register")
        return redirect(url_for("main.register"))
    return render_template("login.html")

@main.route("/register",methods=['GET','POST'])
def register():
    if request.method=='POST':
        name=request.form['name']
        email=request.form['email']
        password=request.form['password']
        if request.form.get('apply_as_staff'):
            role='staff'
            is_approved=False
        else:
            role='trekker'
            is_approved=True
        existing_user=User.query.filter_by(email=email).first()
        if existing_user:
            if existing_user.role =='trekker':    
                flash("Email already registered, Please Login")
            else:
                flash("This email is already registered. Please login or wait for approval.")
            return redirect(url_for("main.login"))
        hashed_password=generate_password_hash(password)
        new_user=User(name=name,email=email,password=hashed_password,role=role,is_approved=is_approved)
        db.session.add(new_user)
        db.session.commit()
        if role=='trekker':
            flash("Registration successful! Please Login")
        else:
            flash("Registration successful! Awaiting admin approval before you can login.")
        return redirect(url_for("main.login"))
    return render_template('register.html')

@main.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out successfully")
    return redirect(url_for("main.home"))

@main.route('/admin_dashboard')
@login_as_admin
def admin_dashboard():
    total_treks=Trek.query.count()
    total_users=User.query.filter_by(role='trekker').count()
    total_bookings=Booking.query.count()
    total_staff=User.query.filter_by(role='staff').count()
    recent_bookings=Booking.query.order_by(Booking.booking_date.desc()).limit(5).all()
    recent_treks=Trek.query.order_by(Trek.start_date.desc()).limit(5).all()
    return render_template("admin_dashboard.html",total_treks=total_treks,total_users=total_users,
                           total_bookings=total_bookings,total_staff=total_staff,recent_bookings=recent_bookings
                           ,recent_treks=recent_treks)
@main.route("/admin_dashboard/all_bookings")
@login_as_admin
def all_bookings():
    all_bookings=Booking.query.all()
    return render_template("all_bookings.html",all_bookings=all_bookings)
@main.route("/admin_dashboard/all_treks")
@login_as_admin
def all_treks():
    search=request.args.get('search','')
    if search:
        all_treks=Trek.query.filter(Trek.name.ilike(f'%{search}%')).all()
    else:
        all_treks=Trek.query.all()
    return render_template("all_treks.html",all_treks=all_treks)
@main.route('/admin_dashboard/create_trek',methods=['GET','POST'])
@login_as_admin
def create_trek():
    if request.method=='POST':
        name=request.form.get('name')
        location=request.form.get('location')
        difficulty=request.form.get('difficulty')
        start_date=datetime.strptime(request.form['start_date'],"%Y-%m-%d")
        end_date=datetime.strptime(request.form['end_date'],"%Y-%m-%d")
        total_slots=int(request.form.get("total_slots"))
        duration=(end_date-start_date).days+1
        description=request.form.get('description')
        status=request.form.get('status')
        assigned_staff_id=request.form.get('assigned_staff_id')
        assigned_staff_id=int(assigned_staff_id) if assigned_staff_id else None
        new_trek=Trek(name=name,location=location,difficulty=difficulty,start_date=start_date,end_date=end_date
                      ,total_slots=total_slots,available_slots=total_slots,duration=duration,description=description,
                      status=status,assigned_staff_id=assigned_staff_id)
        db.session.add(new_trek)
        db.session.commit()
        flash("Trek created successfully!")
        return redirect(url_for("main.all_treks"))
    staff_list=User.query.filter_by(role='staff',is_approved=True).all()
    return render_template('create_trek.html',staff_list=staff_list) #get to create trek form 
@main.route('/staff_dashboard')
@login_as_staff
def staff_dashboard():
    return render_template("staff_dashboard.html")

@main.route('/trekker_dashboard')
@login_as_trekker
def trekker_dashboard():
    return render_template("trekker_dashboard.html")
