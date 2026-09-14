from datetime import datetime, timezone, timedelta
from dateutil.relativedelta import relativedelta
from sqlalchemy.exc import IntegrityError
from ..extensions import db
from ..models import Reminder, NotificationLog

def aware(v):
    if v is None:return None
    return v.replace(tzinfo=timezone.utc) if v.tzinfo is None else v.astimezone(timezone.utc)
def next_occurrence(dt,kind,interval=1):
    dt=aware(dt); interval=max(1,int(interval or 1))
    return {'daily':dt+timedelta(days=interval),'weekly':dt+timedelta(weeks=interval),'monthly':dt+relativedelta(months=interval),'yearly':dt+relativedelta(years=interval),'custom':dt+timedelta(days=interval)}.get(kind)
def process_due(app):
    with app.app_context():
        now=datetime.now(timezone.utc)
        due=Reminder.query.filter(Reminder.is_active.is_(True)).filter(db.func.coalesce(Reminder.snooze_until,Reminder.reminder_datetime)<=now).limit(100).all()
        for r in due:
            when=aware(r.effective_at); key=when.isoformat()
            try:
                with db.session.begin_nested(): db.session.add(NotificationLog(reminder_id=r.id,occurrence_key=key,status='pending',triggered_at=now)); db.session.flush()
            except IntegrityError:
                continue
            r.last_triggered=now; r.snooze_until=None
            nxt=next_occurrence(r.reminder_datetime,r.repeat_type,r.repeat_interval)
            if nxt:
                while nxt<=now: nxt=next_occurrence(nxt,r.repeat_type,r.repeat_interval)
                r.reminder_datetime=nxt
            else:r.is_active=False
        db.session.commit()
def start_scheduler(app):
    from apscheduler.schedulers.background import BackgroundScheduler
    s=BackgroundScheduler(timezone='UTC',daemon=True); s.add_job(process_due,'interval',seconds=15,args=[app],id='due-reminders',max_instances=1,coalesce=True,misfire_grace_time=300); s.start(); return s
