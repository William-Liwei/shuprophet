import uuid
import datetime as dt
from datetime import datetime
from flask import Blueprint, request, jsonify
from functools import wraps
from extensions import db, SECRET_KEY, ADMIN_PASSWORD
from models.db_models import RedeemCode
import jwt

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')


def _make_admin_token():
    payload = {
        'role': 'admin',
        'exp': datetime.utcnow() + dt.timedelta(hours=12),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')


def _admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('X-Admin-Token', '')
        if not token:
            return jsonify({'error': '需要管理员权限'}), 401
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            if payload.get('role') != 'admin':
                raise ValueError()
        except Exception:
            return jsonify({'error': '管理员令牌无效或已过期'}), 401
        return f(*args, **kwargs)
    return decorated


@admin_bp.route('/login', methods=['POST'])
def admin_login():
    """管理员登录：验证密码，返回管理员令牌。"""
    if not ADMIN_PASSWORD:
        return jsonify({'error': '管理员功能未启用'}), 403

    data = request.json or {}
    password = data.get('password', '')
    if password != ADMIN_PASSWORD:
        return jsonify({'error': '密码错误'}), 401

    return jsonify({'token': _make_admin_token()})


@admin_bp.route('/codes', methods=['GET'])
@_admin_required
def list_codes():
    """列出所有兑换码。"""
    codes = RedeemCode.query.order_by(RedeemCode.created_at.desc()).all()
    return jsonify({'codes': [{
        'id': c.id,
        'code': c.code,
        'credits': c.credits,
        'is_used': c.is_used,
        'used_by': c.used_by,
        'created_at': c.created_at.isoformat() if c.created_at else None,
        'used_at': c.used_at.isoformat() if c.used_at else None,
    } for c in codes]})


@admin_bp.route('/codes/generate', methods=['POST'])
@_admin_required
def generate_codes():
    """批量生成兑换码。"""
    data = request.json or {}
    count = min(data.get('count', 10), 100)
    credits = data.get('credits', 100)

    if credits <= 0:
        return jsonify({'error': '积分数必须大于0'}), 400

    codes = []
    for _ in range(count):
        code_str = f'SHU-{uuid.uuid4().hex[:12].upper()}'
        c = RedeemCode(code=code_str, credits=credits, created_at=datetime.utcnow())
        db.session.add(c)
        codes.append(code_str)
    db.session.commit()

    return jsonify({
        'message': f'已生成 {count} 个兑换码',
        'codes': codes,
    })


@admin_bp.route('/codes/<int:code_id>', methods=['DELETE'])
@_admin_required
def delete_code(code_id):
    """删除一个兑换码。"""
    c = RedeemCode.query.get(code_id)
    if not c:
        return jsonify({'error': '兑换码不存在'}), 404
    db.session.delete(c)
    db.session.commit()
    return jsonify({'message': '已删除'})


@admin_bp.route('/posts/<int:post_id>', methods=['DELETE'])
@_admin_required
def delete_post(post_id):
    """管理员删除任意帖子。"""
    from models.db_models import Post
    post = Post.query.get(post_id)
    if not post:
        return jsonify({'error': '帖子不存在'}), 404
    db.session.delete(post)
    db.session.commit()
    return jsonify({'message': '已删除'})


@admin_bp.route('/comments/<int:comment_id>', methods=['DELETE'])
@_admin_required
def delete_comment(comment_id):
    """管理员删除任意评论。"""
    from models.db_models import Comment
    comment = Comment.query.get(comment_id)
    if not comment:
        return jsonify({'error': '评论不存在'}), 404
    db.session.delete(comment)
    db.session.commit()
    return jsonify({'message': '已删除'})


# 新增：使用普通用户令牌的管理员删除接口
from utils.auth_utils import login_required
from flask import g

@admin_bp.route('/user/posts/<int:post_id>', methods=['DELETE'])
@login_required
def user_delete_post(post_id):
    """用户管理员删除任意帖子（使用普通令牌）"""
    from models.db_models import User, Post
    user = User.query.get(g.user_id)
    if not user or not user.is_admin:
        return jsonify({'error': '需要管理员权限'}), 403

    post = Post.query.get(post_id)
    if not post:
        return jsonify({'error': '帖子不存在'}), 404
    db.session.delete(post)
    db.session.commit()
    return jsonify({'message': '已删除'})


@admin_bp.route('/user/comments/<int:comment_id>', methods=['DELETE'])
@login_required
def user_delete_comment(comment_id):
    """用户管理员删除任意评论（使用普通令牌）"""
    from models.db_models import User, Comment
    user = User.query.get(g.user_id)
    if not user or not user.is_admin:
        return jsonify({'error': '需要管理员权限'}), 403

    comment = Comment.query.get(comment_id)
    if not comment:
        return jsonify({'error': '评论不存在'}), 404
    db.session.delete(comment)
    db.session.commit()
    return jsonify({'message': '已删除'})
