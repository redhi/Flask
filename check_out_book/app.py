"""
설명...
:create_app() : :초기 flask 서버 실행 코드
"""
from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

import config

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)

    app.config.from_object(config)  # config 에서 가져온 파일을 사용합니다.

    db.init_app(app)  # SQLAlchemy 객체를 app 객체와 이어줍니다.
    Migrate().init_app(app, db)

    import models
    from views import (
        detail_view,
        libraryinfo_view,
        main_view,
        mypage_view,
        returnbook_view,
        totalcheckout_view,
        user_view,
    )

    app.register_blueprint(main_view.bp)
    app.register_blueprint(detail_view.bp)
    app.register_blueprint(totalcheckout_view.bp)
    app.register_blueprint(returnbook_view.bp)
    app.register_blueprint(libraryinfo_view.bp)
    app.register_blueprint(user_view.bp)
    app.register_blueprint(mypage_view.bp)
    # 비밀번호 암호화
    app.secret_key = "afsfsa"
    # 세션 일정시간 서버 저장파일
    app.config["SESSION_TYPE"] = "filesystem"

    return app


if __name__ == "__main__":
    create_app().run(debug=True)
