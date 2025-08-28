import os
from pathlib import Path


class Config:
    # 获取项目根目录
    BASE_DIR = Path(__file__).parent

    # 数据库配置
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{BASE_DIR}/instance/disk_arrays.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 密钥配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard-to-guess-string'

    # 更新登录配置
    LOGIN_USERNAME = 'adminzyab'  # 改为新账号
    LOGIN_PASSWORD = 'Admin@123'  # 改为新密码

    # 新增文件上传配置
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'app/static/uploads')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
