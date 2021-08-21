from flask import Blueprint, render_template, request, url_for, session, flash
from check_out_book.models import *
from werkzeug.utils import redirect
from bcrypt import hashpw, checkpw, gensalt
import datetime
from dateutil.relativedelta import relativedelta


bp = Blueprint('main', __name__, url_prefix='/')

@bp.route('/')
def home():
    book_list = Book.query.order_by(Book.id.asc())
    
    if '_flashes' in session:
        return render_template('main.html', book_list=book_list)

    elif session:
        rentbook_list = CheckOutBook.query.filter_by(user_id=session['email']).all()

        for rentbook in rentbook_list:
            now = datetime.datetime.now()
            datenow=datetime.date(now.year,now.month,now.day)
            leftover =rentbook.end_date - datenow

            if leftover.days<=14: # 일단 확인하기 위해 대출기한 전체로 잡음
                flash(rentbook.book_name+"의 반납 기간이 "+str(leftover.days)+"일 남았습니다")
            
            if leftover.days>0: # 원래는 leftover.days<0: 확인위해 바꿈
                flash(rentbook.book_name+"의 반납 기간이 지났습니다. 도서관으로 방문해서 반납해주세요!")

        return render_template('main.html', book_list=book_list, rentbook_list=rentbook_list)
    return render_template('main.html', book_list=book_list)

@bp.route('/book/<int:book_id>/')
def book_detail(book_id):
    book_info = Book.query.filter_by(id=book_id).first()
    bookreview = BookReview.query.filter_by(book_id=book_id).order_by(BookReview.id.desc()).all() # 최신순 정렬
    
    return render_template('book_detail.html', book_info=book_info, review_info=bookreview)

@bp.route('/login', methods=('GET',))
def login_try():
    return render_template('login.html')


@bp.route('/login', methods=('POST',))
def login():
    email = request.form['email']
    password = request.form['password']
    user_data = LibraryUser.query.filter_by(email=email).first() # 조건 체크

    if not user_data:
        flash("존재하지 않는 아이디입니다.")
        return redirect(url_for('main.login_try'))

    if not checkpw(password.encode("utf-8"), user_data.password):
        flash("아이디와 비밀번호가 일치하지 않습니다.")
        return redirect(url_for('main.login_try'))
    
    session.clear()
    session['email'] = email
    session['name'] = user_data.name
    flash("안녕하세요, {}님!".format(user_data.name))
    return redirect(url_for('main.home'))

@bp.route('/register')
def join():
    return render_template('register.html')

@bp.route('/checkout')
def checkout():
    totalRentbook_list = TotalCheckOutBook.query.filter_by(user_id=session['email']).all()
    return render_template('totalCheckout.html', totalRentbook_list=totalRentbook_list)

@bp.route('/returnlist')
def returnbooklist():
    rentbook_list = CheckOutBook.query.filter_by(user_id=session['email']).all()
    return render_template('returnbook.html', rentbook_list=rentbook_list)

@bp.route('/returnbook/<int:pid>', methods=('POST',))
def returnbook(pid):
    book = CheckOutBook.query.filter_by(id=pid).first()
    findbook = Book.query.filter_by(id=book.book_id).first()
    findbook.stock += 1
    db.session.commit()

    Totalcheck_out = TotalCheckOutBook(book_id=book.book_id,user_id=session['email'],book_name=book.book_name,book_link=findbook.link, start_date=book.start_date  , end_date=book.end_date, 
            rating=book.rating)
    db.session.add(Totalcheck_out)
    db.session.delete(book)
    db.session.commit()
    flash("반납되었습니다")
    return redirect(url_for('main.returnbooklist')) ## 함수명!!! main.함수명

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.home'))

@bp.route('/register', methods=('POST',))
def register():
    if request.method == 'POST':
        user = LibraryUser.query.filter_by(email=request.form['email_id']).first()
        
        if not request.form['email_id']  or not request.form['password2'] or not request.form['password'] or not request.form['name']:
            flash("모든 입력창을 채우세요")
            return redirect(url_for('main.register'))
        
        if not user:
            if request.form['password2'] != request.form['password']:
                flash("비밀번호가 일치하지 않습니다")
                return redirect(url_for('main.register'))
            
            password = hashpw(request.form['password'].encode('utf-8'), gensalt())
            user = LibraryUser(email=request.form['email_id'], password=password,
            name=request.form['name'])
            db.session.add(user)
            db.session.commit()
            
        else:
            flash("이미 가입된 아이디입니다.")
            return redirect(url_for('main.register'))
        
        flash("회원가입에 성공했습니다.")
        return redirect(url_for('main.home'))

@bp.route('/writereview/<int:book_id>', methods=('POST',))
def create_review(book_id):
    if request.method == 'POST':
        
        if 'rating' in request.form and request.form['review']:
            User=LibraryUser.query.filter_by(email=session['email']).first()
            now = datetime.datetime.now()
            create_time = datetime.date(now.year,now.month,now.day)
            review = BookReview(user_id=session['email'],user_name=User.name, book_id=book_id, rating=int(request.form['rating']), content=request.form['review'],create_time=create_time)
            # request.form['name명!!!!']
            rate=Book.query.filter_by(id=book_id).first()
            ratenum = BookReview.query.filter_by(book_id=book_id).count()

            nowrate=rate.rating*ratenum+int(request.form['rating'])
            rate.rating = round(nowrate/(ratenum+1), 1)

            checkout_info = CheckOutBook.query.filter_by(book_id=book_id).update({'rating': round(nowrate/(ratenum+1), 1)})
            Totalcheckout_info = TotalCheckOutBook.query.filter_by(book_id=book_id).update({'rating': round(nowrate/(ratenum+1), 1)})
            print(rate)

            db.session.add(review)
            db.session.commit()
            flash("리뷰가 성공적으로 작성되었습니다.")
            return redirect(url_for('main.book_detail', book_id=book_id))
        flash("모두 작성하세요.")
        return redirect(url_for('main.book_detail', book_id=book_id))
        
    

@bp.route('/deletereview/<int:book_id>/<int:review_id>')
def delete_review(book_id, review_id):
    review_info = BookReview.query.filter_by(id=review_id).first()
    rate = Book.query.filter_by(id=book_id).first()
    ratenum = BookReview.query.filter_by(book_id=book_id).count()
    
    if review_info.user_id != session['email']:
        flash("삭제할 권한이 없습니다.")
        return redirect(url_for('main.book_detail', book_id=book_id))
    
    nowrate=rate.rating*ratenum-review_info.rating
    rate.rating = round(nowrate/(ratenum-1), 1)
    
    checkout_info = CheckOutBook.query.filter_by(book_id=book_id).update({'rating': round(nowrate/(ratenum-1), 1)})
    Totalcheckout_info = TotalCheckOutBook.query.filter_by(book_id=book_id).update({'rating':round(nowrate/(ratenum-1), 1)})
    print(rate)
    
    db.session.delete(review_info)
    db.session.commit()
    flash("삭제가 완료되었습니다.")
    return redirect(url_for('main.book_detail', book_id=book_id))

@bp.route('/check_out/<int:book_id>', methods=('POST',))
def check_check_out(book_id):
    now = datetime.datetime.now()
    
    if request.method == 'POST':
        book = Book.query.filter_by(id=book_id).first()
        print(book.stock) # 이런건 어디서 보나요?
        
        if not session:
            flash("로그인 하십시오.")
            return redirect(url_for('main.home'))

        if book.stock < 1:
            flash("재고가 부족합니다.")
            return redirect(url_for('main.home'))
        
        rentbooknum = CheckOutBook.query.filter_by(user_id=session['email']).count()
        samerentbooknum = CheckOutBook.query.filter_by(book_id=book.id, user_id=session['email']).count()
        
        if samerentbooknum > 0:
            flash("이미 빌린 책입니다.")
            return redirect(url_for('main.home'))
        
        if rentbooknum > 4: # 최대 5권 빌릴 수 있다고 가정
            flash("빌릴 수 있는 권수를 초과하였습니다")
            return redirect(url_for('main.home'))
            
        book.stock -= 1
        db.session.commit()
        end_date=now+relativedelta(weeks=2)
        check_out = CheckOutBook(book_id=book_id,book_name=book.book_name,book_link=book.link,user_id=session['email'], start_date=datetime.date(now.year,now.month,now.day)  , end_date=datetime.date(end_date.year,end_date.month,end_date.day), 
        rating=book.rating)
        db.session.add(check_out)
        db.session.commit()
        flash("정상 처리되었습니다.")
        
            
    return redirect(url_for('main.home'))

