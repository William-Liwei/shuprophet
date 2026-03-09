from datetime import datetime
from flask import Blueprint, request, jsonify, g
from extensions import db
from models.db_models import User, RedeemCode, DailyUsage, CreditLog
from utils.auth_utils import login_required

credits_bp = Blueprint('credits', __name__, url_prefix='/api/credits')

FREE_DAILY_LIMIT = 10
CREDIT_PER_CHAT = 1
TASK_REWARDS = {
    'share_website': 5,
}


def _calculate_level(total_credits):
    """根据累计积分计算等级（不会降级）"""
    if total_credits < 100:
        return 1
    elif total_credits < 500:
        return 2
    elif total_credits < 1500:
        return 3
    elif total_credits < 3000:
        return 4
    else:
        return 5


def _update_user_level(user):
    """更新用户等级，如果升级则给予奖励"""
    old_level = user.level
    new_level = _calculate_level(user.total_credits)
    if new_level > old_level:
        user.level = new_level
        # 升级奖励
        bonus = new_level * 10
        user.credits += bonus
        user.total_credits += bonus
        log = CreditLog(
            user_id=user.id,
            amount=bonus,
            type='level_up',
            description=f'升级到 Lv.{new_level}，获得奖励'
        )
        db.session.add(log)


def _get_today():
    return datetime.utcnow().strftime('%Y-%m-%d')


def _get_daily_usage(user_id):
    today = _get_today()
    usage = DailyUsage.query.filter_by(user_id=user_id, date=today).first()
    if not usage:
        usage = DailyUsage(user_id=user_id, date=today, chat_count=0)
        db.session.add(usage)
        db.session.commit()
    return usage


@credits_bp.route('/info', methods=['GET'])
@login_required
def credits_info():
    """获取用户积分信息和今日用量。"""
    user = User.query.get(g.user_id)
    usage = _get_daily_usage(g.user_id)
    free_remaining = max(0, FREE_DAILY_LIMIT - usage.chat_count)
    return jsonify({
        'credits': user.credits,
        'today_used': usage.chat_count,
        'free_remaining': free_remaining,
        'free_limit': FREE_DAILY_LIMIT,
        'credit_per_chat': CREDIT_PER_CHAT,
    })


@credits_bp.route('/redeem', methods=['POST'])
@login_required
def redeem_code():
    """兑换码充值积分。"""
    data = request.json or {}
    code_str = data.get('code', '').strip()
    if not code_str:
        return jsonify({'error': '请输入兑换码'}), 400

    code = RedeemCode.query.filter_by(code=code_str).first()
    if not code:
        return jsonify({'error': '兑换码不存在'}), 404
    if code.is_used:
        return jsonify({'error': '该兑换码已被使用'}), 400

    user = User.query.get(g.user_id)
    user.credits += code.credits
    user.total_credits += code.credits
    code.is_used = True
    code.used_by = g.user_id
    code.used_at = datetime.utcnow()

    log = CreditLog(
        user_id=g.user_id,
        amount=code.credits,
        type='redeem',
        description=f'兑换码充值: {code_str[:8]}...'
    )
    db.session.add(log)
    _update_user_level(user)
    db.session.commit()

    return jsonify({
        'message': f'兑换成功，获得 {code.credits} 积分',
        'credits': user.credits,
    })


@credits_bp.route('/task', methods=['POST'])
@login_required
def complete_task():
    """完成任务获得积分。"""
    data = request.json or {}
    task_type = data.get('task_type', '')
    if task_type not in TASK_REWARDS:
        return jsonify({'error': '未知任务类型'}), 400

    # 每种任务每人只能完成一次
    already = CreditLog.query.filter_by(
        user_id=g.user_id, type='task', description=f'完成任务: {task_type}'
    ).first()
    if already:
        return jsonify({'error': '你已经完成过该任务了'}), 400

    reward = TASK_REWARDS[task_type]
    user = User.query.get(g.user_id)
    user.credits += reward
    user.total_credits += reward

    log = CreditLog(
        user_id=g.user_id,
        amount=reward,
        type='task',
        description=f'完成任务: {task_type}'
    )
    db.session.add(log)
    _update_user_level(user)
    db.session.commit()

    return jsonify({
        'message': f'任务完成，获得 {reward} 积分',
        'credits': user.credits,
    })


@credits_bp.route('/logs', methods=['GET'])
@login_required
def credit_logs():
    """获取积分流水记录。"""
    logs = CreditLog.query.filter_by(user_id=g.user_id)\
        .order_by(CreditLog.created_at.desc()).limit(50).all()
    return jsonify({
        'logs': [{
            'id': l.id,
            'amount': l.amount,
            'type': l.type,
            'description': l.description,
            'created_at': l.created_at.isoformat(),
        } for l in logs]
    })


def check_and_consume_chat(user_id):
    """检查用户是否可以对话，并消耗配额。返回 (可以, 错误信息)。"""
    user = User.query.get(user_id)
    if not user:
        return False, '用户不存在'

    usage = _get_daily_usage(user_id)

    # 免费额度内
    if usage.chat_count < FREE_DAILY_LIMIT:
        usage.chat_count += 1
        db.session.commit()
        return True, None

    # 超出免费额度，消耗积分
    if user.credits < CREDIT_PER_CHAT:
        return False, f'今日免费 {FREE_DAILY_LIMIT} 次对话已用完，积分不足，请充值'

    user.credits -= CREDIT_PER_CHAT
    usage.chat_count += 1
    log = CreditLog(
        user_id=user_id,
        amount=-CREDIT_PER_CHAT,
        type='chat',
        description='智能助理对话消耗'
    )
    db.session.add(log)
    _update_user_level(user)
    db.session.commit()
    return True, None
