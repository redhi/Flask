import datetime
import urllib.parse
from flask import Blueprint, render_template, request, url_for, session, flash
from check_out_book.models import *
from werkzeug.utils import redirect, secure_filename
from dateutil.relativedelta import relativedelta

bp = Blueprint('detail', __name__, url_prefix='/detail')


@bp.route('/book/<int:book_id>/<string:photolink>')
def book_detail(book_id, photolink):
    print(book_id)
    print(photolink)
    book_info = Book.query.filter_by(id=book_id).first()
    bookreview = BookReview.query.filter_by(book_id=book_id).order_by(
        BookReview.id.desc()).all()  # 최신순 정렬

    return render_template('BookDetail.html', book_info=book_info, review_info=bookreview, photolink=photolink)


@bp.route('/writereview/<int:book_id>/<string:photolink>', methods=('POST',))
def create_review(book_id, photolink):
    print(photolink)
    if request.method == 'POST':

        if 'rating' in request.form and request.form['review']:
            user = LibraryUser.query.filter_by(email=session['email']).first()
            possible = BookReview.query.filter_by(
                user_id=session['email'], book_id=book_id).first()
            if possible:
                flash("리뷰는 한 번만 작성 가능합니다.")
                return redirect(url_for('detail.book_detail', book_id=book_id, photolink=photolink))

            now = datetime.datetime.now()
            create_time = datetime.date(now.year, now.month, now.day)
            review = BookReview(user_id=session['email'], user_name=user.name, book_id=book_id,
                                rating=int(request.form['rating']), content=request.form['review'],
                                create_time=create_time, imagelink=photolink)
            # request.form['name명!!!!']
            rate = Book.query.filter_by(id=book_id).first()
            ratenum = BookReview.query.filter_by(book_id=book_id).count()
            nowrate = rate.rating*ratenum+int(request.form['rating'])
            rate.rating = round(nowrate/(ratenum+1), 1)
            checkout_info = CheckOutBook.query.filter_by(book_id=book_id).update(
                {'rating': round(nowrate/(ratenum+1), 1)})
            Totalcheckout_info = TotalCheckOutBook.query.filter_by(
                book_id=book_id).update({'rating': round(nowrate/(ratenum+1), 1)})
            print(rate)
            db.session.add(review)
            db.session.commit()
            photolink = 12398978982

            flash("리뷰가 성공적으로 작성되었습니다.")
            return redirect(url_for('detail.book_detail', book_id=book_id, photolink=photolink))

        flash("모두 작성하세요.")
        return redirect(url_for('detail.book_detail', book_id=book_id, photolink=photolink))
    return redirect(url_for('detail.book_detail', book_id=book_id, photolink=photolink))


@bp.route('/deletereview/<int:book_id>/<int:review_id>')
def delete_review(book_id, review_id):
    photolink = 12398978982
    review_info = BookReview.query.filter_by(id=review_id).first()
    rate = Book.query.filter_by(id=book_id).first()
    ratenum = BookReview.query.filter_by(book_id=book_id).count()

    if review_info.user_id != session['email']:
        flash("삭제할 권한이 없습니다.")
        return redirect(url_for('detail.book_detail', book_id=book_id, photolink=photolink))

    nowrate = rate.rating*ratenum-review_info.rating
    print(ratenum)

    if ratenum == 1:
        rate.rating = 0
    else:
        rate.rating = round(nowrate/(ratenum-1), 1)
    print(rate.rating)
    CheckOutBook.query.filter_by(book_id=book_id).update(
        {'rating': rate.rating})
    TotalCheckOutBook.query.filter_by(
        book_id=book_id).update({'rating': rate.rating})
    print(rate)

    db.session.delete(review_info)
    db.session.commit()
    flash("삭제가 완료되었습니다.")
    return redirect(url_for('detail.book_detail', book_id=book_id, photolink=photolink))

# %23말고 #으로 전달하는 방법


# +int(str('#'))+'modiphoto'
@bp.route('/modifyreview/<int:book_id>/<int:review_id>/<string:photolink>')
def modify_review(book_id, review_id, photolink):
    print(photolink)
    print(book_id)
    print(review_id)
    review_info = BookReview.query.filter_by(
        id=review_id).first()  # 해당하는 리뷰 찾음
    rate = Book.query.filter_by(id=book_id).first()  # 해당하는 책의 점수를 찾아옴
    ratenum = BookReview.query.filter_by(
        book_id=book_id).count()  # 해당하는 책의 리뷰수를 찾아옴(현재 내꺼까지 포함)
    book_info = Book.query.filter_by(id=book_id).first()
    bookreview = BookReview.query.filter_by(book_id=book_id).order_by(
        BookReview.id.desc()).all()  # 최신순 정렬

    if review_info.user_id != session['email']:
        flash("수정할 권한이 없습니다.")
        return redirect(url_for('detail.book_detail'))

    # 현재 총점을 계산함(수정하기 전 미리 내 점수 빼놓자)
    nowrate = rate.rating*ratenum-review_info.rating

    return render_template('ModifyReview.html', book_info=book_info, review_info=bookreview,
                           book_id=book_id, review_id=review_id,
                           nowrate=nowrate, ratenum=ratenum,
                           book=review_info, photolink=photolink)


@bp.route('/modifyreview2/<int:book_id>/<int:review_id>/<int:nowrate>/<int:ratenum>/<string:photolink>',
          methods=('POST',))
def modify_review2(book_id, review_id, nowrate, ratenum, photolink):
    if request.method == 'POST':
        print(book_id)
        if 'rating' in request.form and request.form['review']:
            now = datetime.datetime.now()
            create_time = datetime.date(now.year, now.month, now.day)
            print(request.form['rating'])
            rate = Book.query.filter_by(id=book_id).first()  # 해당하는 책 찾음
            review = BookReview.query.filter_by(id=review_id).update({'rating': int(
                request.form['rating']), 'content': request.form['review'],
                'create_time': create_time, 'imagelink': photolink})
            # request.form['name명!!!!']
            nowrate = nowrate+int(request.form['rating'])
            print(nowrate)
            rate.rating = round(nowrate/(ratenum), 1)  # 해당하는 책에 별점 업데이트

            CheckOutBook.query.filter_by(
                book_id=book_id).update({'rating': round(nowrate/(ratenum), 1)})
            TotalCheckOutBook.query.filter_by(
                book_id=book_id).update({'rating': round(nowrate/(ratenum), 1)})
            print(rate)

            db.session.commit()
            flash("리뷰가 성공적으로 수정되었습니다.")
            photolink = 12398978982
            return redirect(url_for('detail.book_detail', book_id=book_id, photolink=photolink))
        flash("모두 작성하세요.")
        return redirect(url_for('detail.book_detail', book_id=book_id, photolink=photolink))
    return redirect(url_for('detail.book_detail', book_id=book_id, photolink=photolink))


@bp.route('/upload')
def render_file():
    return render_template('upload.html')


@bp.route('/fileUpload/<int:book_id>', methods=('POST',))
def upload_file(book_id):
    if request.method == 'POST':
        f = request.files['file']
        f.save('/home/redhi/minji/ELICEWEBPROJECT/check_out_book/static/uploads/' +
               f.filename)
        photolink = f.filename
        finalphotolink = 'static/uploads/'+f.filename

        flash("업로드 성공")
        return redirect("/../detail/book/"+str(book_id)+"/"+photolink+"#"+"photo")
        # return redirect(url_for('detail.book_detail2', book_id=book_id, photolink=photolink))
    return '실패'


@bp.route('/modifileUpload/<int:book_id>/<int:review_id>', methods=('POST',))
def modiupload_file(book_id, review_id):
    print(review_id)
    if request.method == 'POST':
        f = request.files['file']
        f.save('/home/redhi/minji/ELICEWEBPROJECT/check_out_book/static/uploads/' +
               f.filename)
        photolink = f.filename
        finalphotolink = 'static/uploads/'+f.filename

        flash("업로드 성공")
        # return redirect("/../detail/modifyreview/"+str(book_id)+"/"+str(review_id)+"/"+photolink+"#"+"photo")

    return redirect(url_for('detail.modify_review', book_id=book_id, review_id=review_id, photolink=photolink))
    return '실패'
