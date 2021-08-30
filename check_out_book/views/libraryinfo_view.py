from flask import Flask, Blueprint, render_template, session

bp = Blueprint('libraryinfo', __name__, url_prefix='/')

# 도서관 소개 html 호출
@bp.route('/libraryinfo')
def libraryinfo():
    return render_template('LibraryInfo.html')
