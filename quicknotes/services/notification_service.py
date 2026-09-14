from ..models import NotificationLog
def unread_notifications(): return NotificationLog.query.filter_by(status='pending').order_by(NotificationLog.triggered_at.asc()).all()
