from flask import Blueprint, render_template, request, url_for, session, flash
from check_out_book.models import *
from werkzeug.utils import redirect

bp = Blueprint('return', __name__, url_prefix='/return')


@bp.route('/booklist')
def returnbooklist():
    rentbook_list = CheckOutBook.query.filter_by(
        user_id=session['email']).all()
    return render_template('ReturnBook.html', rentbook_list=rentbook_list)


@bp.route('/<int:pid>', methods=('POST',))
def returnbook(pid):
    print(pid)
    book = CheckOutBook.query.filter_by(id=pid).first()
    print(book)
    findbook = Book.query.filter_by(id=book.book_id).first()
    findbook.stock += 1
    db.session.commit()

    totalcheck_out = TotalCheckOutBook(book_id=book.book_id, user_id=session['email'],
                                       book_name=book.book_name, book_link=findbook.link,
                                       start_date=book.start_date, end_date=book.end_date,
                                       rating=book.rating)
    db.session.add(totalcheck_out)
    db.session.delete(book)
    db.session.commit()
    flash("반납되었습니다")
    return redirect(url_for('return.returnbooklist'))  # 함수명!!! main.함수명
