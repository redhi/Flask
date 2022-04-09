import datetime

from dateutil.relativedelta import relativedelta
from flask import Blueprint, Flask, flash, render_template, session, url_for
from models import *
from werkzeug.utils import redirect, secure_filename

bp = Blueprint("mypage", __name__, url_prefix="/")


# 예약한 책 목록
@bp.route("/reservation")
def reservationbook():
    reservationbook_list = ReservationBook.query.filter_by(
        user_id=session["email"]
    ).all()
    rentbook_list = CheckOutBook.query.filter_by(user_id=session["email"]).all()
    rentbooknum = CheckOutBook.query.filter_by(user_id=session["email"]).count()

    count = 0  # 연체반납한 책이 2권 이상일 때 flash가 두번이상 넘어가는거 방지
    for rentbook in rentbook_list:
        now = datetime.datetime.now()
        datenow = datetime.date(now.year, now.month, now.day)
        leftover = rentbook.end_date - datenow

        if leftover.days < 0:
            count += 1
    if count > 0:  # count가 한번이라도 일어나면
        flash("연체반납이 일어나 대기순번이 넘어갈 수 있습니다.")

    if rentbooknum > 4:  # 최대 5권 빌릴 수 있다고 가정
        flash("빌릴 수 있는 권수를 초과하여 대기순번이 넘어갈 수 있습니다.")
    return render_template("MyPage.html", reservationbook_list=reservationbook_list)


# 탈퇴하기
@bp.route("/withdraw", methods=("POST",))
def withdraw():
    user_review = (
        BookReview.query.filter_by(user_id=session["email"])
        .order_by(BookReview.book_id.asc())
        .all()
    )
    print(user_review)
    print(session["email"])
    # 리뷰 삭제

    for review in user_review:
        print(review.book_id)
        rate = Book.query.filter_by(id=review.book_id).first()
        ratenum = BookReview.query.filter_by(book_id=review.book_id).count()
        nowrate = rate.rating * ratenum - review.rating
        print(review.rating)
        if ratenum == 1:
            rate.rating = 0
        else:
            rate.rating = round(nowrate / (ratenum - 1), 1)
        print(rate.rating)
        CheckOutBook.query.filter_by(book_id=review.book_id).update(
            {"rating": rate.rating}
        )
        TotalCheckOutBook.query.filter_by(book_id=review.book_id).update(
            {"rating": rate.rating}
        )
        print(rate)
        db.session.delete(review)
        db.session.commit()
    # 대여한 책 삭제
    user_checkout = CheckOutBook.query.filter_by(user_id=session["email"]).all()
    print(user_checkout)

    for user in user_checkout:
        findbook = Book.query.filter_by(id=user.book_id).first()
        findbook.stock += 1
        db.session.commit()
        db.session.delete(user)
        db.session.commit()
        print(user)

    # 예약한 책 삭제
    user_reversation = ReservationBook.query.filter_by(user_id=session["email"]).all()
    print(user_reversation)

    for user in user_reversation:
        print("예약한 책 삭제")
        print(user)
        db.session.delete(user)
        db.session.commit()

    # 총 대여한 책 삭제
    user_totalcheckout = TotalCheckOutBook.query.filter_by(
        user_id=session["email"]
    ).all()
    print(user_totalcheckout)

    for user in user_totalcheckout:
        print("총 대여한 책")
        print(user)
        db.session.delete(user)
        db.session.commit()

    # 사용자 정보 삭제
    user = LibraryUser.query.filter_by(email=session["email"]).first()  # 조건 체크
    db.session.delete(user)
    db.session.commit()
    session.clear()
    flash("탈퇴되었습니다.")
    return redirect(url_for("main.home"))
