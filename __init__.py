import os  # 新增这行导入语句
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from syno_manager.config import Config


# 初始化数据库
db = SQLAlchemy()


def create_app(config_class=Config):
    # 创建Flask应用
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)

    # 确保instance文件夹存在
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # 确保上传文件夹存在
    try:
        os.makedirs(app.config['UPLOAD_FOLDER'])
    except OSError:
        pass

    # 初始化扩展
    db.init_app(app)

    # 注册蓝图
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.routes import bp as main_bp
    app.register_blueprint(main_bp)

    # 创建数据库表
    with app.app_context():
        db.create_all()

    return app
