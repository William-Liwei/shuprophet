from flask import Blueprint, request, jsonify, g
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db
from models.db_models import User
from utils.auth_utils import generate_token, login_required

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json or {}
    username = data.get('username', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '')

    if not username or not email or not password:
        return jsonify({'error': '用户名、邮箱和密码不能为空'}), 400
    if len(password) < 6:
        return jsonify({'error': '密码至少6位'}), 400
    if User.query.filter_by(username=username).first():
        return jsonify({'error': '用户名已存在'}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({'error': '邮箱已被注册'}), 400

    user = User(
        username=username,
        email=email,
        password_hash=generate_password_hash(password),
        nickname=username
    )
    db.session.add(user)
    db.session.commit()

    token = generate_token(user.id)
    return jsonify({
        'token': token,
        'user': _user_dict(user)
    }), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json or {}
    username = data.get('username', '').strip()
    password = data.get('password', '')

    if not username or not password:
        return jsonify({'error': '用户名和密码不能为空'}), 400

    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({'error': '用户名或密码错误'}), 401

    token = generate_token(user.id)
    return jsonify({
        'token': token,
        'user': _user_dict(user)
    })


@auth_bp.route('/me', methods=['GET'])
@login_required
def me():
    user = User.query.get(g.user_id)
    if not user:
        return jsonify({'error': '用户不存在'}), 404
    return jsonify({'user': _user_dict(user)})


@auth_bp.route('/verify-admin', methods=['POST'])
@login_required
def verify_admin():
    """验证管理员密码，通过后将当前用户设置为管理员"""
    from extensions import ADMIN_PASSWORD
    if not ADMIN_PASSWORD:
        return jsonify({'error': '管理员功能未启用'}), 403

    data = request.json or {}
    password = data.get('password', '')

    if password != ADMIN_PASSWORD:
        return jsonify({'error': '管理员密码错误'}), 401

    user = User.query.get(g.user_id)
    user.is_admin = True
    db.session.commit()

    return jsonify({
        'message': '已获得管理员权限',
        'user': _user_dict(user)
    })



def _user_dict(user):
    return {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'nickname': user.nickname,
        'avatar_url': user.avatar_url,
        'bio': user.bio,
        'credits': user.credits,
        'level': user.level,
        'is_admin': user.is_admin,
        'created_at': user.created_at.isoformat()
    }
