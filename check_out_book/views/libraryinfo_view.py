from flask import Blueprint, render_template, session

bp = Blueprint('libraryinfo', __name__, url_prefix='/')


@bp.route('/libraryinfo')
def libraryinfo():

    return render_template('LibraryInfo.html')
