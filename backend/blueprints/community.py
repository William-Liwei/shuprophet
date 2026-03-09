import json
from datetime import datetime
from flask import Blueprint, request, jsonify, g
from extensions import db
from models.db_models import User, Post, Comment, PostLike, CreditLog, DailyUsage
from utils.auth_utils import login_required

community_bp = Blueprint('community', __name__, url_prefix='/api/community')

DAILY_COMMUNITY_LIMIT = 5


def _get_today():
    return datetime.utcnow().strftime('%Y-%m-%d')


def _give_credits(user_id, amount, description):
    """给用户增加积分，检查每日社区积分上限"""
    # 检查今日社区积分
    today = _get_today()
    today_community = db.session.query(db.func.sum(CreditLog.amount)).filter(
        CreditLog.user_id == user_id,
        CreditLog.type == 'community',
        db.func.date(CreditLog.created_at) == today
    ).scalar() or 0

    if today_community >= DAILY_COMMUNITY_LIMIT:
        return False

    # 限制不超过每日上限
    actual_amount = min(amount, DAILY_COMMUNITY_LIMIT - today_community)
    if actual_amount <= 0:
        return False

    user = User.query.get(user_id)
    if user:
        user.credits += actual_amount
        user.total_credits += actual_amount
        log = CreditLog(user_id=user_id, amount=actual_amount, type='community', description=description)
        db.session.add(log)
        # 更新等级
        from blueprints.credits import _update_user_level
        _update_user_level(user)
        return True
    return False


@community_bp.route('/posts', methods=['GET'])
def list_posts():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    sort = request.args.get('sort', 'latest')
    per_page = min(per_page, 50)

    if sort == 'hot':
        # 热门排序：按点赞数+评论数排序
        all_posts = Post.query.all()
        posts_with_score = []
        for p in all_posts:
            score = PostLike.query.filter_by(post_id=p.id).count() * 2 + p.comments.count()
            posts_with_score.append((p, score))
        posts_with_score.sort(key=lambda x: x[1], reverse=True)

        total = len(posts_with_score)
        start = (page - 1) * per_page
        end = start + per_page
        items = [p for p, _ in posts_with_score[start:end]]
        pages = (total + per_page - 1) // per_page

        posts = [_post_brief(p) for p in items]
        return jsonify({'posts': posts, 'total': total, 'page': page, 'pages': pages})
    else:
        # 最新排序
        pagination = Post.query.order_by(Post.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        posts = [_post_brief(p) for p in pagination.items]
        return jsonify({
            'posts': posts,
            'total': pagination.total,
            'page': page,
            'pages': pagination.pages
        })


@community_bp.route('/posts', methods=['POST'])
@login_required
def create_post():
    data = request.json or {}
    content = data.get('content', '').strip()
    if not content:
        return jsonify({'error': '内容不能为空'}), 400

    post = Post(user_id=g.user_id, content=content)
    db.session.add(post)
    _give_credits(g.user_id, 2, '发布帖子')
    db.session.commit()
    return jsonify({'post': _post_brief(post)}), 201


@community_bp.route('/posts/<int:post_id>', methods=['GET'])
def get_post(post_id):
    post = Post.query.get(post_id)
    if not post:
        return jsonify({'error': '帖子不存在'}), 404

    comments = []
    for c in post.comments.order_by(Comment.created_at.asc()).all():
        author = User.query.get(c.user_id)
        comments.append({
            'id': c.id,
            'content': c.content,
            'created_at': c.created_at.isoformat(),
            'author': {
                'id': author.id,
                'nickname': author.nickname,
                'avatar_url': author.avatar_url
            } if author else None
        })

    result = _post_brief(post)
    result['comments'] = comments
    if post.conversation_json:
        result['conversation'] = json.loads(post.conversation_json)
    return jsonify({'post': result})


@community_bp.route('/posts/<int:post_id>', methods=['DELETE'])
@login_required
def delete_post(post_id):
    post = Post.query.get(post_id)
    if not post:
        return jsonify({'error': '帖子不存在'}), 404
    if post.user_id != g.user_id:
        return jsonify({'error': '无权删除'}), 403
    db.session.delete(post)
    db.session.commit()
    return jsonify({'message': '已删除'})


@community_bp.route('/posts/<int:post_id>/comments', methods=['POST'])
@login_required
def add_comment(post_id):
    post = Post.query.get(post_id)
    if not post:
        return jsonify({'error': '帖子不存在'}), 404
    data = request.json or {}
    content = data.get('content', '').strip()
    if not content:
        return jsonify({'error': '评论不能为空'}), 400

    comment = Comment(post_id=post_id, user_id=g.user_id, content=content)
    db.session.add(comment)
    _give_credits(g.user_id, 1, '发表评论')
    db.session.commit()

    author = User.query.get(g.user_id)
    return jsonify({'comment': {
        'id': comment.id,
        'content': comment.content,
        'created_at': comment.created_at.isoformat(),
        'author': {
            'id': author.id,
            'nickname': author.nickname,
            'avatar_url': author.avatar_url
        }
    }}), 201


@community_bp.route('/comments/<int:comment_id>', methods=['DELETE'])
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get(comment_id)
    if not comment:
        return jsonify({'error': '评论不存在'}), 404
    if comment.user_id != g.user_id:
        return jsonify({'error': '无权删除'}), 403
    db.session.delete(comment)
    db.session.commit()
    return jsonify({'message': '已删除'})


@community_bp.route('/posts/<int:post_id>/like', methods=['POST'])
@login_required
def toggle_like(post_id):
    post = Post.query.get(post_id)
    if not post:
        return jsonify({'error': '帖子不存在'}), 404

    existing = PostLike.query.filter_by(
        post_id=post_id, user_id=g.user_id
    ).first()

    if existing:
        db.session.delete(existing)
        db.session.commit()
        liked = False
    else:
        like = PostLike(post_id=post_id, user_id=g.user_id)
        db.session.add(like)
        db.session.commit()
        liked = True

    count = PostLike.query.filter_by(post_id=post_id).count()
    return jsonify({'liked': liked, 'like_count': count})


@community_bp.route('/share-conversation', methods=['POST'])
@login_required
def share_conversation():
    data = request.json or {}
    content = data.get('content', '').strip()
    conversation = data.get('conversation', [])

    if not content:
        content = '分享了一段AI对话'

    post = Post(
        user_id=g.user_id,
        content=content,
        conversation_json=json.dumps(conversation, ensure_ascii=False)
    )
    db.session.add(post)
    db.session.commit()
    return jsonify({'post': _post_brief(post)}), 201


def _post_brief(post):
    author = User.query.get(post.user_id)
    like_count = PostLike.query.filter_by(post_id=post.id).count()
    comment_count = post.comments.count()
    return {
        'id': post.id,
        'content': post.content,
        'has_conversation': post.conversation_json is not None,
        'like_count': like_count,
        'comment_count': comment_count,
        'created_at': post.created_at.isoformat(),
        'author': {
            'id': author.id,
            'nickname': author.nickname,
            'avatar_url': author.avatar_url
        } if author else None
    }


@community_bp.route('/stats', methods=['GET'])
def get_stats():
    """获取社区统计数据"""
    post_count = Post.query.count()
    comment_count = Comment.query.count()
    return jsonify({
        'posts': post_count,
        'comments': comment_count,
        'total': post_count + comment_count
    })
