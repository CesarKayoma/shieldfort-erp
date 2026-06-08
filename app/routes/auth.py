from flask import Blueprint, render_template, redirect, url_for

bp = Blueprint('auth', __name__)

@bp.route('/login')
def login():
    return render_template('auth/login.html')

@bp.route('/logout')
def logout():
    return redirect(url_for('auth.login'))