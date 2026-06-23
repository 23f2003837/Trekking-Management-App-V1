from flask import Blueprint,render_template,request,redirect,url_for,session,flash
from app.models import User
from app import db
from werkzeug.security import generate_password_hash,check_password_hash
from app.decorators import login_required

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
                        return redirect(url_for("main.dashboard"))#todo--> need to be built
                    elif session['role']=='admin':
                        return redirect(url_for("main.dashboard"))#todo--> need to be built
                    else:
                        return redirect(url_for("main.dashboard"))#todo--> need to be built
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

@main.route('/dashboard')
@login_required
def dashboard():
    return render_template("dashboard.html")