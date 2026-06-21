from flask import Blueprint,render_template,request,redirect,url_for,session,flash
from app.models import User
from app import db
from werkzeug.security import generate_password_hash,check_password_hash
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
                flash("Successfully Login")
                session['user_id']=existing_user.id
                session['role']=existing_user.role
                return redirect(url_for("main.home"))
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
        existing_user=User.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already registered, Please Login")
            return redirect(url_for("main.login"))
        
        hashed_password=generate_password_hash(password)
        new_user=User(name=name,email=email,password=hashed_password,role='trekker')
        db.session.add(new_user)
        db.session.commit()
        flash("Registration successful! Please Login")
        return redirect(url_for("main.login"))
    return render_template('register.html')