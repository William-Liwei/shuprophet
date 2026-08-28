import os
import secrets
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy

load_dotenv()

db = SQLAlchemy()

SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or secrets.token_urlsafe(32)

# 数据库连接：配置 DATABASE_URL 时使用指定数据库，否则使用默认数据库文件。
DATABASE_URL = os.environ.get('DATABASE_URL', None)
if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

# 管理员密码：通过环境变量设置，源码里不存明文
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', None)
