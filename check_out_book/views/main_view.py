import datetime
from flask import Blueprint, render_template, request, url_for, session, flash
from check_out_book.models import *
from werkzeug.utils import redirect
from dateutil.relativedelta import relativedelta


bp = Blueprint('main', __name__, url_prefix='/')


@bp.route('/')
def home():
    book_list = Book.query.order_by(Book.id.asc())

    if '_flashes' in session:
        return render_template('Main.html', book_list=book_list)

    if 'email' in session:
        rentbook_list = CheckOutBook.query.filter_by(
            user_id=session['email']).all()

        for rentbook in rentbook_list:
            now = datetime.datetime.now()
            datenow = datetime.date(now.year, now.month, now.day)
            leftover = rentbook.end_date - datenow

            if leftover.days <= 14:  # 일단 확인하기 위해 대출기한 전체로 잡음
                flash(rentbook.book_name+"의 반납 기간이 " +
                      str(leftover.days)+"일 남았습니다")

            if leftover.days > 0:  # 원래는 leftover.days<0: 확인위해 바꿈
                flash(rentbook.book_name+"의 반납 기간이 지났습니다. 도서관으로 방문해서 반납해주세요!")

        return render_template('Main.html', book_list=book_list, rentbook_list=rentbook_list)
    return render_template('Main.html', book_list=book_list)


@bp.route('/check_out/<int:book_id>', methods=('POST',))
def check_check_out(book_id):
    now = datetime.datetime.now()

    if request.method == 'POST':
        book = Book.query.filter_by(id=book_id).first()

        if not session:
            flash("로그인 하십시오.")
            return redirect(url_for('main.home'))

        if book.stock < 1:
            flash("재고가 부족합니다.")
            return redirect(url_for('main.home'))

        rentbooknum = CheckOutBook.query.filter_by(
            user_id=session['email']).count()
        samerentbooknum = CheckOutBook.query.filter_by(
            book_id=book.id, user_id=session['email']).count()

        if samerentbooknum > 0:
            flash("이미 빌린 책입니다.")
            return redirect(url_for('main.home'))

        if rentbooknum > 4:  # 최대 5권 빌릴 수 있다고 가정
            flash("빌릴 수 있는 권수를 초과하였습니다")
            return redirect(url_for('main.home'))

        book.stock -= 1
        db.session.commit()
        end_date = now+relativedelta(weeks=2)
        check_out = CheckOutBook(book_id=book_id, book_name=book.book_name, book_link=book.link,
                                 user_id=session['email'], start_date=datetime.date(
                                     now.year, now.month, now.day),
                                 end_date=datetime.date(
                                     end_date.year, end_date.month, end_date.day),
                                 rating=book.rating)
        db.session.add(check_out)
        db.session.commit()
        flash("정상 처리되었습니다.")

    return redirect(url_for('main.home'))


@bp.route('/search', methods=('POST',))
def searchbook():
    book_name = request.form['keyword']
    print(book_name)
    search = "%{}%".format(book_name)
    print(search)
    searchbooklist = Book.query.filter(Book.book_name.like(search)).all()

    return render_template('SearchBookDetail.html', searchbooklist=searchbooklist)
