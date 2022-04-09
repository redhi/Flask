from flask import Blueprint, render_template, session
from models import *

bp = Blueprint("total", __name__, url_prefix="/total")

# 대여기록 목록
@bp.route("/checkout")
def checkout():
    totalrentbook_list = TotalCheckOutBook.query.filter_by(
        user_id=session["email"]
    ).all()
    return render_template("TotalCheckOut.html", totalrentbook_list=totalrentbook_list)
