from functools import wraps
from flask import session, redirect, url_for, flash

def login_as_admin(f):
    @wraps(f)
    def decorated_function(*args,**kwargs):
        if 'user_id' not in session:
            flash("Please Login")
            return redirect(url_for("main.login"))
        elif session['role']!='admin':
            flash(f'Access Denied')
            return redirect(url_for(f"main.{session['role']}_dashboard"))
        else:
            return f(*args,**kwargs)
    return decorated_function

def login_as_staff(f):
    @wraps(f)
    def decorated_function(*args,**kwargs):
        if 'user_id' not in session:
            flash("Please Login")
            return redirect(url_for("main.login"))
        elif session['role']!='staff':
            flash(f'Access Denied')
            return redirect(url_for(f"main.{session['role']}_dashboard"))
        else:
            return f(*args,**kwargs)
    return decorated_function

def login_as_trekker(f):
    @wraps(f)
    def decorated_function(*args,**kwargs):
        if 'user_id' not in session:
            flash("Please Login")
            return redirect(url_for("main.login"))
        elif session['role']!='trekker':
            flash(f'Access Denied')
            return redirect(url_for(f"main.{session['role']}_dashboard"))
        else:
            return f(*args,**kwargs)
    return decorated_function

