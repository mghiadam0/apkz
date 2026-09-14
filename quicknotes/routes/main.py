from datetime import datetime,timezone,timedelta
from zoneinfo import ZoneInfo
from flask import Blueprint,render_template,request,jsonify,current_app
from sqlalchemy import or_
from ..extensions import db
from ..models import Note,Reminder,NotificationLog
bp=Blueprint('main',__name__)
@bp.get('/')
def dashboard():
    active=Note.query.filter(Note.deleted_at.is_(None)); now=datetime.now(timezone.utc); local_now=now.astimezone(ZoneInfo(current_app.config['APP_TIMEZONE'])); local_start=local_now.replace(hour=0,minute=0,second=0,microsecond=0); day_start=local_start.astimezone(timezone.utc); end=(local_start+timedelta(days=1)).astimezone(timezone.utc)
    stats={'all':active.count(),'open':active.filter_by(is_completed=False,is_archived=False).count(),'done':active.filter_by(is_completed=True).count(),'pinned':active.filter_by(is_pinned=True).count(),'archived':active.filter_by(is_archived=True).count(),'today':Reminder.query.filter(Reminder.is_active.is_(True),Reminder.reminder_datetime>=day_start,Reminder.reminder_datetime<end).count()}
    upcoming=Reminder.query.join(Note).filter(Reminder.is_active.is_(True),Note.deleted_at.is_(None)).order_by(Reminder.reminder_datetime).limit(8).all()
    return render_template('dashboard.html',stats=stats,upcoming=upcoming)
@bp.get('/calendar')
def calendar():
    month=request.args.get('month',datetime.now().strftime('%Y-%m')); return render_template('calendar.html',month=month)
@bp.get('/api/calendar')
def calendar_data():
    month=request.args.get('month',datetime.now().strftime('%Y-%m')); start=datetime.strptime(month+'-01','%Y-%m-%d').replace(tzinfo=timezone.utc); end=(start.replace(day=28)+timedelta(days=4)).replace(day=1)
    rs=Reminder.query.join(Note).filter(Reminder.reminder_datetime>=start,Reminder.reminder_datetime<end,Note.deleted_at.is_(None)).all()
    tz=ZoneInfo(current_app.config['APP_TIMEZONE']); return jsonify([{'id':r.note_id,'title':r.note.title,'at':(r.reminder_datetime.replace(tzinfo=timezone.utc) if r.reminder_datetime.tzinfo is None else r.reminder_datetime).astimezone(tz).isoformat()} for r in rs])
