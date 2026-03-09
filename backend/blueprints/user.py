import os
import base64
from flask import Blueprint, request, jsonify, g, send_from_directory, Response
from werkzeug.utils import secure_filename
from extensions import db
from models.db_models import User
from utils.auth_utils import login_required

user_bp = Blueprint('user', __name__, url_prefix='/api/user')

AVATARS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'avatars')
if not os.path.exists(AVATARS_DIR):
    os.makedirs(AVATARS_DIR)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}


def _calculate_level(credits):
    """根据积分计算用户等级"""
    if credits < 100:
        return 1
    elif credits < 500:
        return 2
    elif credits < 1500:
        return 3
    elif credits < 3000:
        return 4
    else:
        return 5


def _update_user_level(user):
    """更新用户等级"""
    new_level = _calculate_level(user.credits)
    if user.level != new_level:
        user.level = new_level
        db.session.commit()


def _allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@user_bp.route('/profile', methods=['PUT'])
@login_required
def update_profile():
    user = User.query.get(g.user_id)
    data = request.json or {}
    if 'nickname' in data:
        user.nickname = data['nickname'].strip()[:80]
    if 'bio' in data:
        user.bio = data['bio'].strip()[:500]
    db.session.commit()
    return jsonify({'user': _pub_user(user)})


@user_bp.route('/avatar', methods=['POST'])
@login_required
def upload_avatar():
    if 'file' not in request.files:
        return jsonify({'error': '未找到文件'}), 400
    file = request.files['file']
    if file.filename == '' or not _allowed_file(file.filename):
        return jsonify({'error': '不支持的文件格式'}), 400

    # 读取文件并转换为Base64
    file_data = file.read()
    base64_data = base64.b64encode(file_data).decode('utf-8')
    ext = file.filename.rsplit('.', 1)[1].lower()

    user = User.query.get(g.user_id)
    user.avatar_data = f'data:image/{ext};base64,{base64_data}'
    user.avatar_url = f'/api/user/avatars/{g.user_id}'
    db.session.commit()
    return jsonify({'avatar_url': user.avatar_url})


@user_bp.route('/avatars/<path:filename>', methods=['GET'])
def serve_avatar(filename):
    # filename可能是user_id或旧的文件名
    if filename == 'default.png':
        # 返回默认头像
        return send_from_directory(AVATARS_DIR, 'default.png')

    # 尝试从数据库获取
    try:
        user_id = int(filename.split('.')[0].replace('avatar_', ''))
        user = User.query.get(user_id)
        if user and user.avatar_data:
            # 解析Base64数据
            if user.avatar_data.startswith('data:image'):
                mime_type, data = user.avatar_data.split(';base64,')
                img_data = base64.b64decode(data)
                return Response(img_data, mimetype=mime_type.split(':')[1])
    except:
        pass

    # 兼容旧的文件系统头像
    if os.path.exists(os.path.join(AVATARS_DIR, filename)):
        return send_from_directory(AVATARS_DIR, filename)

    return send_from_directory(AVATARS_DIR, 'default.png')


@user_bp.route('/<int:user_id>', methods=['GET'])
def get_user_public(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': '用户不存在'}), 404

    # 获取用户发帖历史
    from models.db_models import Post, PostLike
    posts = Post.query.filter_by(user_id=user_id).order_by(Post.created_at.desc()).limit(20).all()
    post_list = []
    for p in posts:
        like_count = PostLike.query.filter_by(post_id=p.id).count()
        comment_count = p.comments.count()
        post_list.append({
            'id': p.id,
            'content': p.content[:100] + ('...' if len(p.content) > 100 else ''),
            'like_count': like_count,
            'comment_count': comment_count,
            'created_at': p.created_at.isoformat()
        })

    user_data = _pub_user(user)
    user_data['level'] = user.level
    user_data['posts'] = post_list
    user_data['post_count'] = Post.query.filter_by(user_id=user_id).count()

    return jsonify({'user': user_data})


def _pub_user(user):
    return {
        'id': user.id,
        'username': user.username,
        'nickname': user.nickname,
        'avatar_url': user.avatar_url,
        'bio': user.bio,
        'created_at': user.created_at.isoformat()
    }
