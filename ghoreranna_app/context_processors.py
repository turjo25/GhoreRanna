def cart_count(request):
    cart = request.session.get('cart', {})
    count = sum(cart.values()) if cart else 0
    return {'global_cart_count': count}

from .models import Notification

def notifications(request):
    if request.session.get('user_id'):
        user_id = request.session.get('user_id')
        unread_notifications = Notification.objects.filter(user_id=user_id, is_read=False).order_by('-created_at')[:5]
        unread_count = Notification.objects.filter(user_id=user_id, is_read=False).count()
        return {
            'unread_notifications': unread_notifications,
            'unread_notifications_count': unread_count,
        }
    return {}