import csv
from datetime import date, datetime
from flask import session
#from check_out_book.models import bookInfo
from check_out_book import db, create_app
from check_out_book.models import *

create_app()
with open('library.csv', 'r', encoding="cp949") as f:
    reader = csv.DictReader(f)

    for row in reader:
        published_at = datetime.strptime(
						row['publication_date'], '%Y-%m-%d').date()
        image_path = f"static/image/{row['id']}"
        try:
            open(f'{image_path}.png')
            image_path += '.png'
        except:
            image_path += '.jpg'
        
        #print(int(row['id']),",\"",row['book_name'],"\",\"", row['publisher'],"\",\"",row['author'],"\",\"",published_at,"\",",int(row['pages']),",\"",row['isbn'],"\",\"",row['description'],"\",\"",image_path,"\",",5,",",0)
        print("\"",image_path,"\"")
        book = bookInfo(id=int(row['id']), 
			book_name=row['book_name'], 
			publisher=row['publisher'],
            author=row['author'], 
			publication_date=published_at, 
			pages=int(row['pages']),
            isbn=row['isbn'], 
			description=row['description'], 
			link=image_path,
            stock=5,
			rating=0
        )
        db.session.add(book)
    db.session.commit()