import re
from flask import Blueprint, render_template, request, url_for, session, flash
from check_out_book.models import *
from werkzeug.utils import redirect
from bcrypt import hashpw, checkpw, gensalt

bp = Blueprint('user', __name__, url_prefix='/')

# 회원가입 폼
@bp.route('/register')
def join():
    return render_template('Register.html')

# 회원가입 처리
@bp.route('/register', methods=('POST',))
def register():
    if request.method == 'POST':
        user = LibraryUser.query.filter_by(
            email=request.form['email_id']).first()

        if not (request.form['email_id'] or request.form['password2'] or request.form['password'] or request.form['name']):
            flash("모든 입력창을 채우세요")
            return redirect(url_for('user.register'))

        if not user:
            reg = re.compile("^[ㄱ-ㅎ|가-힣|a-z|A-Z|]+$")
            correctname = reg.match(request.form['name'])

            if correctname is None:
                flash("이름은 한글 또는 영어만 입력할 수 있습니다.")
                return redirect(url_for('user.register'))

            if request.form['password2'] != request.form['password']:
                flash("비밀번호가 일치하지 않습니다")
                return redirect(url_for('user.register'))
                # \d = 숫자
            reg2 = re.compile(
                "^(?=.*[A-Za-z])(?=.*\d)(?=.*[$@$!%*#?&])[A-Za-z\d$@$!%*#?&]{8,}$")
            correctpw = reg2.match(request.form['password'])

            if correctpw is None:
                flash("비밀번호는 영문자, 숫자, 특수문자가 각각 한 개 이상, 총 8자리 이상이여야 합니다.")
                return redirect(url_for('user.register'))

            password = hashpw(
                request.form['password'].encode('utf-8'), gensalt())
            user = LibraryUser(email=request.form['email_id'], password=password,
                               name=request.form['name'])
            db.session.add(user)
            db.session.commit()
            flash("회원가입에 성공했습니다.")
            return redirect(url_for('main.home'))

        flash("이미 가입된 아이디입니다.")
        return redirect(url_for('user.register'))

    return redirect(url_for('user.register'))

# 로그인 폼
@bp.route('/login', methods=('GET',))
def login_try():
    return render_template('Login.html')

# 로그인 처리
@bp.route('/login', methods=('POST',))
def login():
    email = request.form['email']
    password = request.form['password']
    user_data = LibraryUser.query.filter_by(email=email).first()  # 조건 체크

    if not user_data:
        flash("존재하지 않는 아이디입니다.")
        return redirect(url_for('user.login_try'))

    if not checkpw(password.encode("utf-8"), user_data.password):
        flash("아이디와 비밀번호가 일치하지 않습니다.")
        return redirect(url_for('user.login_try'))

    if len(request.form['password']) < 7:
        flash("비밀번호는 최소 8자리 이상 입력해야 합니다.")
        return redirect(url_for('user.login_try'))

    session.clear()
    session['email'] = email
    session['name'] = user_data.name
    flash("안녕하세요, {}님!".format(user_data.name))
    return redirect(url_for('main.home'))

# 로그아웃 처리
@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.home'))
