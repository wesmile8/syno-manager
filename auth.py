from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from functools import wraps
from flask import current_app

bp = Blueprint('auth', __name__)


# 登录装饰器，用于保护需要登录的路由
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session or not session['logged_in']:
            flash('请先登录', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)

    return decorated_function


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # 验证用户名和密码
        if (username == current_app.config['LOGIN_USERNAME'] and
                password == current_app.config['LOGIN_PASSWORD']):
            session['logged_in'] = True
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.index'))
        else:
            flash('用户名或密码错误', 'danger')

    return render_template('login.html')


@bp.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('已成功登出', 'info')
    return redirect(url_for('auth.login'))
