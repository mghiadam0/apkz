from datetime import datetime,timezone
from zoneinfo import ZoneInfo
from flask import Blueprint,render_template,request,jsonify,abort,current_app
from sqlalchemy import or_
from ..extensions import db
from ..models import Note,Category,Tag,Reminder
bp=Blueprint('notes',__name__,url_prefix='/notes')
COLORS={'#ffffff','#e5f2fc','#e8f1ec','#fbebde','#fce9e7','#f3e8ff'}
def parse_dt(d,t):
    if not d or not t:return None
    try:return datetime.fromisoformat(f'{d}T{t}').replace(tzinfo=ZoneInfo(current_app.config['APP_TIMEZONE'])).astimezone(timezone.utc)
    except ValueError:abort(400,'Invalid reminder date')
def payload(note): return {'id':note.id,'title':note.title,'content':note.content,'pinned':note.is_pinned,'completed':note.is_completed,'archived':note.is_archived,'important':note.is_important,'color':note.color}
@bp.get('/')
def index():
    q=request.args.get('q','').strip()[:100]; view=request.args.get('view','all'); sort=request.args.get('sort','newest'); page=max(1,request.args.get('page',1,type=int))
    x=Note.query
    if view=='trash':x=x.filter(Note.deleted_at.is_not(None))
    else:
        x=x.filter(Note.deleted_at.is_(None))
        if view=='archive':x=x.filter_by(is_archived=True)
        else:x=x.filter_by(is_archived=False)
        if view=='important':x=x.filter_by(is_important=True)
        if view=='completed':x=x.filter_by(is_completed=True)
        if view=='open':x=x.filter_by(is_completed=False)
    if q:
        like=f'%{q}%'; x=x.outerjoin(Note.category).outerjoin(Note.tags).filter(or_(Note.title.ilike(like),Note.content.ilike(like),Category.name.ilike(like),Tag.name.ilike(like))).distinct()
    orders={'oldest':[Note.created_at.asc()],'pinned':[Note.is_pinned.desc(),Note.updated_at.desc()],'newest':[Note.is_pinned.desc(),Note.updated_at.desc()]}; x=x.order_by(*orders.get(sort,orders['newest']))
    pager=x.paginate(page=page,per_page=24,error_out=False); return render_template('notes.html',notes=pager.items,pager=pager,categories=Category.query.order_by(Category.name).all(),view=view)
@bp.post('/')
def create():
    data=request.form; title=data.get('title','').strip()[:180]
    if not title:abort(400,'Title required')
    n=Note(title=title,content=data.get('content','').strip()[:20000],color=data.get('color') if data.get('color') in COLORS else '#ffffff',category_id=data.get('category_id',type=int),is_important=data.get('important')=='on')
    tags=[v.strip().lower()[:50] for v in data.get('tags','').split(',') if v.strip()][:12]
    for v in dict.fromkeys(tags): n.tags.append(Tag.query.filter_by(name=v).first() or Tag(name=v))
    if data.get('reminder')=='on':
        dt=parse_dt(data.get('date'),data.get('time'))
        if dt:n.reminder=Reminder(reminder_datetime=dt,repeat_type=data.get('repeat','none'),repeat_interval=max(1,min(365,data.get('repeat_interval',1,type=int))))
    db.session.add(n); db.session.commit(); return jsonify(payload(n)),201
@bp.patch('/<int:nid>')
def update(nid):
    n=Note.query.get_or_404(nid); d=request.get_json() or {}
    for k in ('is_pinned','is_completed','is_archived','is_important'):
        if k in d:setattr(n,k,bool(d[k]))
    if 'title' in d and d['title'].strip():n.title=d['title'].strip()[:180]
    if 'content' in d:n.content=str(d['content'])[:20000]
    db.session.commit(); return jsonify(payload(n))
@bp.delete('/<int:nid>')
def delete(nid):
    n=Note.query.get_or_404(nid); n.deleted_at=datetime.now(timezone.utc); db.session.commit(); return '',204
@bp.post('/<int:nid>/restore')
def restore(nid):
    n=Note.query.get_or_404(nid); n.deleted_at=None; db.session.commit(); return jsonify(payload(n))
@bp.post('/<int:nid>/duplicate')
def duplicate(nid):
    n=Note.query.get_or_404(nid); c=Note(title=n.title+' (copy)',content=n.content,color=n.color,category_id=n.category_id); c.tags=list(n.tags); db.session.add(c); db.session.commit(); return jsonify(payload(c)),201
