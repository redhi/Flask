import re
from flask import Blueprint, render_template, request, url_for, session, flash
from check_out_book.models import *
from werkzeug.utils import redirect
from bcrypt import hashpw, checkpw, gensalt

bp = Blueprint('user', __name__, url_prefix='/')


@bp.route('/register')
def join():
    return render_template('Register.html')


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


@bp.route('/login', methods=('GET',))
def login_try():
    return render_template('Login.html')


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


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.home'))


@bp.route('/withdraw')
def withdraw_try():
    return render_template('Withdraw.html')


@bp.route('/withdraw', methods=('POST',))
def withdraw():
    user_review = BookReview.query.filter_by(
        user_id=session['email']).order_by(BookReview.book_id.asc()).all()
    print(user_review)
    for review in user_review:
        print(review.book_id)
        rate = Book.query.filter_by(id=review.book_id).first()
        ratenum = BookReview.query.filter_by(book_id=review.book_id).count()
        nowrate = rate.rating*ratenum-review.rating
        print(review.rating)

        if ratenum == 1:
            rate.rating = 0
        else:
            rate.rating = round(nowrate/(ratenum-1), 1)
        print(rate.rating)
        CheckOutBook.query.filter_by(book_id=review.book_id).update({
            'rating': rate.rating})
        TotalCheckOutBook.query.filter_by(
            book_id=review.book_id).update({'rating': rate.rating})
        print(rate)

        db.session.delete(review)
        db.session.commit()

    user_checkout = CheckOutBook.query.filter_by(
        user_id=session['email']).all()
    if user_checkout != []:
        for user in user_checkout:
            findbook = Book.query.filter_by(id=user.book_id).first()
            findbook.stock += 1
            db.session.commit()
            db.session.delete(user)
            db.session.commit()
            print(user)
    user_reversation = ReservationBook.query.filter_by(
        user_id=session['email']).all()
    if user_reversation != []:
        for user in user_checkout:
            db.session.delete(user)
            db.session.commit()
            print(user)
    user_totalcheckout = TotalCheckOutBook.query.filter_by(
        user_id=session['email']).all()
    if user_totalcheckout != []:
        for user in user_checkout:
            db.session.delete(user)
            db.session.commit()
            print(user)
    user = LibraryUser.query.filter_by(email=session['email']).first()  # 조건 체크

    db.session.delete(user)
    db.session.commit()
    session.clear()
    flash("탈퇴되었습니다")
    return redirect(url_for('main.home'))
