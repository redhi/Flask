import datetime
from flask import Blueprint, render_template, request, url_for, session, flash
from flask.helpers import stream_with_context
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

            if 0 <= leftover.days <= 3:  # 일단 확인하기 위해 대출기한 전체로 잡음 3일내로 들어왔을 때
                flash(rentbook.book_name+"의 반납 기간이 " +
                      str(leftover.days)+"일 남았습니다")

            if leftover.days < 0:  # 원래는 leftover.days<0: 확인위해 바꿈
                flash(rentbook.book_name+"의 반납 기간이 지났습니다. 도서관으로 방문해서 반납해주세요!")

        return render_template('Main.html', book_list=book_list, rentbook_list=rentbook_list)
    return render_template('Main.html', book_list=book_list)


@bp.route('/check_out/<int:book_id>', methods=('POST',))
def check_check_out(book_id):
    now = datetime.datetime.now()

    if request.method == 'POST':
        book = Book.query.filter_by(id=book_id).first()

        if 'email' not in session:
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

        datenow = datetime.date(now.year, now.month, now.day)
        rentbooklist = CheckOutBook.query.filter_by(
            user_id=session['email']).all()
        count = 0
        stopdate = 0

        for rentbook in rentbooklist:
            leftover = rentbook.end_date - datenow
            print(leftover.days)
            if leftover.days < 0:
                print(leftover.days)
                stopdate += abs(leftover.days)
                print(stopdate)
                count += 1
        finalstopdate = stopdate * count

        if finalstopdate > 0:
            flash("연체반납이 일어나 "+str(finalstopdate) +
                  "일만큼 대출정지가 발생했습니다. 도서관 이용안내를 참고해주세요!")
            return redirect(url_for('main.home'))
        reservationbook = ReservationBook.query.filter_by(
            user_id=session['email'], book_id=book_id).first()
        # 예약된 책이 있으면 - 만약 대출정지나 권수 초과로 대기순번 넘어가 있다가 나중에 빌릴때
        print("예약된 책있냐!!!")
        print(reservationbook)
        if reservationbook is not None:
            flash("예약된 책이 대여되었습니다.")
            db.session.delete(reservationbook)
            db.session.commit()

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
        return redirect("/../../"+"#"+str(book_id))

    return redirect(url_for('main.home'))
# 만들어 놓긴 하는데 좋은 기능은 아닌것같다


@bp.route('/reservation/<int:book_id>', methods=('POST',))
def reservation(book_id):
    now = datetime.datetime.now()

    if request.method == 'POST':
        book = Book.query.filter_by(id=book_id).first()

        if 'email' not in session:
            flash("로그인 하십시오.")
            return redirect(url_for('main.home'))

        samerentbooknum = CheckOutBook.query.filter_by(
            user_id=session['email'], book_id=book.id).count()
        reservationbooknum = ReservationBook.query.filter_by(
            user_id=session['email']).count()
        samereservationbooknum = ReservationBook.query.filter_by(
            book_id=book.id, user_id=session['email']).count()

        if samerentbooknum > 0:
            flash("이미 빌린 책입니다.")
            return redirect(url_for('main.home'))

        if samereservationbooknum > 0:
            flash("이미 예약한 책입니다.")
            return redirect(url_for('main.home'))

        if reservationbooknum > 1:  # 최대 2권 예약할 수 있다고 가정
            flash("예약할 수 있는 권수를 초과하였습니다")
            return redirect(url_for('main.home'))
        booknum = ReservationBook.query.filter_by(book_id=book_id).count()
        booknum += 1
        reservationbook = ReservationBook(book_id=book_id, book_name=book.book_name,
                                          user_id=session['email'], create_time=datetime.date(
                                              now.year, now.month, now.day), book_link=book.link, book_num=booknum)
        db.session.add(reservationbook)
        db.session.commit()

        flash(str(booknum)+"번 째로 예약되었습니다.")

    return redirect(url_for('main.home'))


@bp.route('/search', methods=('POST',))
def searchbook():
    book_name = request.form['keyword']
    print(book_name)
    search = "%{}%".format(book_name)
    print(search)
    searchbooklist = Book.query.filter(Book.book_name.like(search)).all()

    return render_template('SearchBookDetail.html', searchbooklist=searchbooklist)
# 회원탈퇴 - 대여기록, 댓글 모두 삭제
# 댓글 작성 - 이미지... 첨부 파일.......... 불러올 때는.....
# 예약하기 - 반납을 하면 바로 넘어가게
# 발표할 때 로직위주로
