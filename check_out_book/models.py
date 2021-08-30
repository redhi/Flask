from check_out_book import db


class Book(db.Model):

    __tablename__ = 'BOOK'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    book_name = db.Column(db.String(100), nullable=False)
    publisher = db.Column(db.String(60), nullable=False)
    author = db.Column(db.String(30))
    publication_date = db.Column(db.Date)
    pages = db.Column(db.Integer)
    isbn = db.Column(db.String(50))
    description = db.Column(db.String(255))
    link = db.Column(db.String(255))
    stock = db.Column(db.Integer)
    rating = db.Column(db.Integer, db.ForeignKey('BOOK_REVIEW.id'))

    def __init__(self, id, book_name, publisher,
                 author, publication_date, pages, isbn, description, link, stock, rating):
        self.id = id
        self.book_name = book_name
        self.publisher = publisher
        self.author = author
        self.publication_date = publication_date
        self.pages = pages
        self.isbn = isbn
        self.description = description
        self.link = link
        self.stock = stock
        self.rating = 0


class LibraryUser(db.Model):

    __tablename__ = 'LIBRARY_USER'

    email = db.Column(db.String(70), primary_key=True, nullable=False)
    name = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(50))


class CheckOutBook(db.Model):

    __tablename__ = 'CHECK_OUT_BOOK'

    id = db.Column(db.Integer, primary_key=True,
                   nullable=False, autoincrement=True)
    book_id = db.Column(db.String(100), db.ForeignKey(
        'BOOK.id'), nullable=False)
    book_name = db.Column(db.String(100), nullable=False)
    book_link = db.Column(db.String(255))
    user_id = db.Column(db.String(70), db.ForeignKey('LIBRARY_USER.email'))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    rating = db.Column(db.Integer, db.ForeignKey('BOOK_REVIEW.id'))
    # rating 유의해서 짜자


class ReservationBook(db.Model):

    __tablename__ = 'RESERVATION_BOOK'

    id = db.Column(db.Integer, primary_key=True,
                   nullable=False, autoincrement=True)
    book_id = db.Column(db.String(100), db.ForeignKey(
        'BOOK.id'), nullable=False)
    book_name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.String(70), db.ForeignKey('LIBRARY_USER.email'))
    create_time = db.Column(db.Date)
    book_link = db.Column(db.String(255))
    book_num = db.Column(db.Integer)


class TotalCheckOutBook(db.Model):

    __tablename__ = 'TOTAL_CHECK_OUT_BOOK'

    id = db.Column(db.Integer, primary_key=True,
                   nullable=False, autoincrement=True)
    book_id = db.Column(db.String(100), db.ForeignKey(
        'BOOK.id'), nullable=False)
    book_name = db.Column(db.String(100), nullable=False)
    book_link = db.Column(db.String(255))
    user_id = db.Column(db.String(70), db.ForeignKey('LIBRARY_USER.email'))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    rating = db.Column(db.Integer, db.ForeignKey('BOOK_REVIEW.id'))
    # rating 유의해서 짜자


class BookReview(db.Model):

    __tablename__ = 'BOOK_REVIEW'

    id = db.Column(db.Integer, primary_key=True,
                   nullable=False, autoincrement=True)
    book_id = db.Column(db.String(100), db.ForeignKey(
        'BOOK.id'), nullable=False)
    user_name = db.Column(db.String(20), nullable=False)
    user_id = db.Column(db.String(70), db.ForeignKey('LIBRARY_USER.email'))
    rating = db.Column(db.Float)
    content = db.Column(db.Text())
    create_time = db.Column(db.Date)
    imagelink = db.Column(db.String(225))
