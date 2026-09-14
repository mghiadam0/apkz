import json
from flask import Blueprint,jsonify,request,Response,abort
from ..extensions import db
from ..models import Note,Category,Tag,Reminder
bp=Blueprint('data',__name__,url_prefix='/data')
@bp.get('/export')
def export():
    rows=[]
    for n in Note.query.filter(Note.deleted_at.is_(None)).all(): rows.append({'title':n.title,'content':n.content,'color':n.color,'pinned':n.is_pinned,'completed':n.is_completed,'important':n.is_important,'category':n.category.name if n.category else None,'tags':[t.name for t in n.tags],'reminder':n.reminder.reminder_datetime.isoformat() if n.reminder else None,'repeat':n.reminder.repeat_type if n.reminder else None})
    return Response(json.dumps({'version':1,'notes':rows},ensure_ascii=False,indent=2),mimetype='application/json',headers={'Content-Disposition':'attachment; filename=quick-notes-backup.json'})
@bp.post('/import')
def import_data():
    f=request.files.get('file');
    if not f:abort(400)
    try:data=json.load(f)
    except Exception:abort(400,'Invalid JSON')
    if not isinstance(data.get('notes'),list) or len(data['notes'])>5000:abort(400)
    for row in data['notes']:
        title=str(row.get('title','')).strip()[:180]
        if title:db.session.add(Note(title=title,content=str(row.get('content',''))[:20000],color=str(row.get('color','#ffffff'))[:16]))
    db.session.commit(); return jsonify({'imported':len(data['notes'])})
