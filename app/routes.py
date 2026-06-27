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

#admin dashboard
@main.route('/admin_dashboard')
@login_as_admin
def admin_dashboard():
    total_treks=Trek.query.filter(Trek.status!="cancelled").count()
    total_users=User.query.filter_by(role='trekker',is_blacklisted=False).count()
    total_bookings=Booking.query.filter(Booking.status!='cancelled').count()
    total_staff=User.query.filter_by(role='staff',is_blacklisted=False,is_approved=True).count()
    recent_bookings=Booking.query.filter(Booking.status!='cancelled').order_by(Booking.booking_date.desc()).limit(5).all()
    # Filter cancelled out, then order by start_date descending
    recent_treks=Trek.query.filter(Trek.status!='cancelled').order_by(Trek.start_date.desc()).limit(5).all()
    recent_pending_staff=User.query.filter_by(role='staff',is_approved=False).limit(5).all()
    return render_template("admin_dashboard.html",total_treks=total_treks,total_users=total_users,
                           total_bookings=total_bookings,total_staff=total_staff,recent_bookings=recent_bookings
                           ,recent_treks=recent_treks,recent_pending_staff=recent_pending_staff)

#admin sees all bookings
@main.route("/admin_dashboard/all_bookings")
@login_as_admin
def all_bookings():
    search=request.args.get('search','')
    query=Booking.query.join(User).filter(Booking.status!='cancelled')
    if search:
        query=query.filter(User.name.ilike(f'%{search}%'))
    all_bookings=query.all()
    return render_template("all_bookings.html",all_bookings=all_bookings)
    
#admin sees all cancelled bookings
@main.route("/admin_dashboard/cancelled_bookings")
@login_as_admin
def cancelled_bookings():
    search=request.args.get('search', '')
    query=Booking.query.join(User).filter(Booking.status=='cancelled')
    if search:
        query=query.filter(User.name.ilike(f'%{search}%'))
    cancelled_bookings=query.all()
    return render_template("cancelled_bookings.html",cancelled_bookings=cancelled_bookings)

#admin sees all treks
@main.route("/admin_dashboard/all_treks")
@login_as_admin
def all_treks():
    search=request.args.get('search','')
    query=Trek.query.filter(Trek.status!='cancelled')
    if search:
        query=query.filter(Trek.name.ilike(f'%{search}%'))
    all_treks=query.all()
    return render_template("all_treks.html",all_treks=all_treks)

#admin sees all cancelled treks
@main.route('/admin_dashboard/cancelled_treks')
@login_as_admin
def cancelled_treks():
    search=request.args.get('search', '')
    cancelled_treks=Trek.query.filter_by(status='cancelled').all()
    return render_template("cancelled_treks.html",cancelled_treks=cancelled_treks)

#admin creates trek
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
    staff_list=User.query.filter_by(role='staff',is_approved=True,is_blacklisted=False).all()
    return render_template('create_trek.html',staff_list=staff_list) #get to create trek form 

#admin edits trek
@main.route('/admin_dashboard/edit_trek/<int:trek_id>',methods=['GET','POST'])
@login_as_admin
def edit_trek(trek_id):
    trek=Trek.query.get_or_404(trek_id)
    if request.method=='POST':
        trek.name=request.form.get('name')
        trek.location=request.form.get('location')
        trek.difficulty=request.form.get('difficulty')
        trek.start_date=datetime.strptime(request.form['start_date'],"%Y-%m-%d")
        trek.end_date=datetime.strptime(request.form['end_date'],"%Y-%m-%d")
        booked_count=trek.total_slots-trek.available_slots
        trek.total_slots=int(request.form.get("total_slots"))
        trek.available_slots=trek.total_slots-booked_count
        trek.duration=(trek.end_date-trek.start_date).days+1
        trek.description=request.form.get('description')
        trek.status=request.form.get('status')
        trek.assigned_staff_id=request.form.get('assigned_staff_id')
        trek.assigned_staff_id=int(trek.assigned_staff_id) if trek.assigned_staff_id else None
        db.session.commit()
        flash("Trek Changes have been made")
        return redirect(url_for("main.all_treks"))
    staff_list=User.query.filter_by(role='staff',is_approved=True,is_blacklisted=False).all()
    return render_template("modify_trek.html",trek=trek,staff_list=staff_list)

#admin deletes a trek
@main.route('/admin_dashboard/delete_trek/<int:trek_id>',methods=['POST'])
@login_as_admin
def delete_trek(trek_id):
    trek=Trek.query.get_or_404(trek_id)
    #all treks that have bookings as well as were completed or ongoing
    if trek.bookings and trek.status in ['completed','ongoing']:
        flash("Cannot delete treks that are completed or ongoing!")
        return redirect(url_for("main.all_treks"))
    #if trek had bookings but status is pending/open/closed then cancel trek
    if trek.bookings:
        for booking in trek.bookings:
            booking.status='cancelled'
        trek.status='cancelled'
        db.session.commit()
        flash("Trek had existing Bookings. All Bookings cancelled and trek marked as Cancelled.")
        return redirect(url_for("main.all_treks"))
    #if trek has no bookings
    trek.status='cancelled'
    db.session.commit()
    flash('Trek Marked as Cancelled Successfully!')
    return redirect(url_for("main.all_treks"))

#admin blacklist a user
@main.route("/admin_dashboard/blacklist_trekker/<int:user_id>",methods=['POST'])
@login_as_admin
def blacklist_trekker(user_id):
    user=User.query.get_or_404(user_id)
    user.is_blacklisted=not user.is_blacklisted
    db.session.commit()
    status="Blacklisted" if user.is_blacklisted else "Removed from blacklist"
    flash(f"{status} successfully")
    if status=='Blacklisted':
        return redirect(url_for("main.all_trekkers"))
    else:
        return redirect(url_for("main.blacklisted_trekkers"))

#admin view all blacklisted trekkers
@main.route("/admin_dashboard/blacklisted_trekkers")
@login_as_admin
def blacklisted_trekkers():
    search=request.args.get('search', '')
    query=User.query.filter(User.role=='trekker').filter(User.is_blacklisted==True)
    if search:
        query=query.filter(User.name.ilike(f'%{search}%'))
    blacklisted_trekker_list=query.all()
    return render_template("blacklisted_trekkers.html",blacklisted_trekker_list=blacklisted_trekker_list)

#admin view trekkers list
@main.route("/admin_dashboard/all_trekkers")
@login_as_admin
def all_trekkers():
    search=request.args.get('search','')
    query=User.query.filter(User.role=='trekker').filter(User.is_blacklisted==False)
    if search:
        query=query.filter(User.name.ilike(f'%{search}%'))
    trekker_list=query.all()
    return render_template("all_trekkers.html",trekker_list=trekker_list)

#admin can view staff
@main.route("/admin_dashboard/all_staff")
@login_as_admin
def all_staffs():
    search=request.args.get('search','')
    query=User.query.filter_by(role='staff',is_blacklisted=False,is_approved=True)
    if search:
        query=query.filter(User.name.ilike(f"%{search}%"))
    staff_list=query.all()
    return render_template("all_staff.html",staff_list=staff_list)

#admin blacklist a staff
@main.route("/admin_dashboard/blacklist_staff/<int:user_id>",methods=['POST'])
@login_as_admin
def blacklist_staff(user_id):
    user=User.query.get_or_404(user_id)
    user.is_blacklisted=not user.is_blacklisted
    db.session.commit()
    status="Blacklisted" if user.is_blacklisted else "Removed from blacklist"
    flash(f"{status} successfully")
    if status=='Blacklisted':
        return redirect(url_for("main.all_staffs"))
    else:
        return redirect(url_for("main.blacklisted_staff_list"))

#admin can view all blacklisted staff
@main.route("/admin_dashboard/blacklisted_staff")
@login_as_admin
def blacklisted_staff_list():
    query=User.query.filter_by(role='staff',is_blacklisted=True)
    search=request.args.get('search','')
    if search:
        query=query.filter(User.name.ilike(f"%{search}%"))
    blacklisted_staff_list=query.all()
    return render_template("blacklisted_staff.html",blacklisted_staff_list=blacklisted_staff_list)

#admin can view all pending staff
@main.route("/admin_dashboard/pending_staff")
@login_as_admin
def pending_staff_list():
    query=User.query.filter_by(role='staff',is_approved=False)
    search=request.args.get('search','')
    if search:
        query=query.filter(User.name.ilike(f"%{search}%"))
    pending_staff_list=query.all()
    return render_template("pending_staff.html",pending_staff_list=pending_staff_list)

#admin approves pending staff
@main.route("/admin_dashboard/approve_staff/<int:user_id>",methods=['POST'])
@login_as_admin
def approve_staff(user_id):
    user=User.query.get_or_404(user_id)
    user.is_approved=True
    db.session.commit()
    flash("Staff approved successfully")
    return redirect(url_for("main.pending_staff_list"))

#admin rejects staff
@main.route("/admin_dashboard/reject_staff/<int:user_id>",methods=['POST'])
@login_as_admin
def reject_staff(user_id):
    user=User.query.get_or_404(user_id)
    if user.role=='staff' and user.is_approved==False:
        db.session.delete(user)
        db.session.commit()
        flash("Staff application rejected and removed.")
        return redirect(url_for("main.pending_staff_list"))
    else:
        flash("This user is not a pending staff applicant.")
        return redirect(url_for("main.pending_staff_list"))
    
#admin can view per user trekking history
@main.route("/admin_dashboard/trekker_history/<int:user_id>")
@login_as_admin
def trekker_history(user_id):
    user=User.query.get_or_404(user_id)
    # All bookings for this user, completed treks
    history=Booking.query.join(Trek).filter(Booking.user_id==user_id,
            Trek.status=='completed').order_by(Trek.end_date.desc()).all()
    return render_template("trekker_history.html",user=user,history=history)

#admin can view staff trekking history where they have guided
@main.route("/admin_dashboard/staff_history/<int:user_id>")
@login_as_admin
def staff_history(user_id):
    user=User.query.get_or_404(user_id)
    # Treks where this staff was assigned and completed
    guided_treks = Trek.query.filter(
        Trek.assigned_staff_id == user_id,
        Trek.status.in_(['completed', 'ongoing', 'closed'])
    ).order_by(Trek.start_date.desc()).all()
    return render_template("staff_history.html", user=user, guided_treks=guided_treks)


@main.route('/staff_dashboard')
@login_as_staff
def staff_dashboard():
    return render_template("staff_dashboard.html")

@main.route('/trekker_dashboard')
@login_as_trekker
def trekker_dashboard():
    return render_template("trekker_dashboard.html")
