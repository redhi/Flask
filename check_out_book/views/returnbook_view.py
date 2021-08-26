import datetime
from flask import Blueprint, render_template, request, url_for, session, flash
from check_out_book.models import *
from werkzeug.utils import redirect
from dateutil.relativedelta import relativedelta

bp = Blueprint('return', __name__, url_prefix='/return')


@bp.route('/booklist')
def returnbooklist():
    rentbook_list = CheckOutBook.query.filter_by(
        user_id=session['email']).all()
    now = datetime.datetime.now()
    datenow = datetime.date(now.year, now.month, now.day)
    return render_template('ReturnBook.html', rentbook_list=rentbook_list, datenow=datenow)


def reservationreturn(book, findbook):
    now = datetime.datetime.now()
    findwholist = ReservationBook.query.filter_by(book_id=book.book_id).all()
    nowbooknum = 0
    for findwho in findwholist:
        print(findwho)
        rentbooknum = CheckOutBook.query.filter_by(
            user_id=findwho.user_id).count()
        print(rentbooknum)
        if rentbooknum > 4:  # 빌릴 수 있는 책 넘어가면
            continue
            # 다음 순서로 넘어가서 다음 사람 체크해야함ㅠㅠㅠㅠㅠㅠㅠㅠㅠㅠㅠㅠㅠㅠㅠㅠ 함수로 뺴자
            # 대출정지 일어난 사람 체크해서 또 넘어가야해ㅠㅠㅠㅠㅠㅠㅠㅠㅠㅠㅠㅠㅠㅠㅠㅠㅠ
        datenow = datetime.date(now.year, now.month, now.day)  # 현재날짜
        rentbooklist = CheckOutBook.query.filter_by(
            user_id=findwho.user_id).all()
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

        if finalstopdate > 0:  # 연체반납이 일어나면
            continue

        # 여기서 마이너스해도 뒤에서 플러스해줌
        findbook.stock -= 1
        db.session.commit()
        nowbooknum = findwho.book_num

        end_date = now+relativedelta(weeks=2)
        check_out = CheckOutBook(book_id=findbook.id, book_name=book.book_name, book_link=findbook.link,
                                 user_id=findwho.user_id, start_date=datetime.date(
                                     now.year, now.month, now.day),
                                 end_date=datetime.date(
                                     end_date.year, end_date.month, end_date.day),
                                 rating=findbook.rating)

        db.session.delete(findwho)  # 해당하는 사람 지우고
        db.session.add(check_out)
        db.session.commit()
        flash("정상 처리되었습니다.")
        break
    # 대출받은 애빼고 다시 검색
    # 다른 애들 순번 다 마이너스 1해주자~
    print("여기까지 옴")
    findwholist2 = ReservationBook.query.filter_by(
        book_id=book.book_id).all()
    for findwho in findwholist2:
        print("findwho.book_num")
        print(findwho.book_num)
        print(nowbooknum)
        if nowbooknum < findwho.book_num:  # 예약받은 순번이 앞에 순번보다 높으면
            findwho.book_num -= 1  # 빼줌, 아니면 앞에 순번 유지시켜줘야함
            db.session.commit()

    # 대기순번 나머지 1씩 감소
    # findwait = ReservationBook.query.filter_by(book_Id=book.book_id).all()


@bp.route('/<int:pid>', methods=('POST',))
def returnbook(pid):
    print(pid)
    now = datetime.datetime.now()
    datenow = datetime.date(now.year, now.month, now.day)
    book = CheckOutBook.query.filter_by(id=pid).first()
    print(book)
    findbook = Book.query.filter_by(id=book.book_id).first()
    if findbook.stock == 0:
        reservationreturn(book, findbook)

    findbook.stock += 1
    db.session.commit()

    totalcheck_out = TotalCheckOutBook(book_id=book.book_id, user_id=session['email'],
                                       book_name=book.book_name, book_link=findbook.link,
                                       start_date=book.start_date, end_date=datenow,
                                       rating=book.rating)
    db.session.add(totalcheck_out)
    db.session.delete(book)
    db.session.commit()
    flash("반납되었습니다.")
    # return redirect(url_for('total.checkout'))
    # return redirect("/../../"+"#"+str(book.book_id))
    return redirect(url_for('return.returnbooklist'))  # 함수명!!! main.함수명
