from datetime import datetime,timezone,timedelta
from flask import Blueprint,render_template,jsonify,request,abort
from ..extensions import db
from ..models import Reminder,NotificationLog,Note
bp=Blueprint('reminders',__name__,url_prefix='/reminders')
@bp.get('/')
def index():
    now=datetime.now(timezone.utc); rs=Reminder.query.join(Note).filter(Note.deleted_at.is_(None)).order_by(Reminder.reminder_datetime).all(); return render_template('reminders.html',reminders=rs,now=now)
@bp.get('/notifications')
def notifications():
    logs=NotificationLog.query.join(Reminder).join(Note).filter(NotificationLog.status=='pending').order_by(NotificationLog.triggered_at).limit(20).all()
    return jsonify([{'id':x.id,'reminder_id':x.reminder_id,'note_id':x.reminder.note_id,'title':x.reminder.note.title,'content':x.reminder.note.content[:120],'at':x.triggered_at.isoformat()} for x in logs])
@bp.post('/notifications/<int:lid>/done')
def done(lid):
    x=NotificationLog.query.get_or_404(lid); x.status='done'; x.read_at=datetime.now(timezone.utc); x.reminder.note.is_completed=True; db.session.commit(); return '',204
@bp.post('/notifications/<int:lid>/snooze')
def snooze(lid):
    x=NotificationLog.query.get_or_404(lid); mins=request.get_json(silent=True) or {}; mins=int(mins.get('minutes',10));
    if mins not in (5,10,15,30,60):abort(400)
    x.status='snoozed'; x.read_at=datetime.now(timezone.utc); x.reminder.snooze_until=datetime.now(timezone.utc)+timedelta(minutes=mins); x.reminder.is_active=True; db.session.commit(); return '',204
@bp.patch('/<int:rid>')
def update(rid):
    r=Reminder.query.get_or_404(rid); d=request.get_json() or {}
    if 'is_active' in d:r.is_active=bool(d['is_active'])
    db.session.commit(); return jsonify({'id':r.id,'is_active':r.is_active})
@bp.delete('/<int:rid>')
def delete(rid): db.session.delete(Reminder.query.get_or_404(rid)); db.session.commit(); return '',204
