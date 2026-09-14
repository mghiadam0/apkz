from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from ..extensions import db

def utcnow(): return datetime.now(timezone.utc)
note_tags=db.Table('note_tags',db.Column('note_id',db.Integer,db.ForeignKey('notes.id',ondelete='CASCADE'),primary_key=True),db.Column('tag_id',db.Integer,db.ForeignKey('tags.id',ondelete='CASCADE'),primary_key=True))
class User(db.Model):
    __tablename__='users'; id=db.Column(db.Integer,primary_key=True); email=db.Column(db.String(255),unique=True,index=True); password_hash=db.Column(db.String(255)); locale=db.Column(db.String(5),default='ar'); created_at=db.Column(db.DateTime(timezone=True),default=utcnow)
    def set_password(self,p): self.password_hash=generate_password_hash(p)
    def check_password(self,p): return bool(self.password_hash and check_password_hash(self.password_hash,p))
class Category(db.Model):
    __tablename__='categories'; id=db.Column(db.Integer,primary_key=True); name=db.Column(db.String(80),nullable=False,unique=True,index=True); icon=db.Column(db.String(8),default='📌'); color=db.Column(db.String(16),default='#2783DE')
class Tag(db.Model):
    __tablename__='tags'; id=db.Column(db.Integer,primary_key=True); name=db.Column(db.String(50),nullable=False,unique=True,index=True)
class Note(db.Model):
    __tablename__='notes'; id=db.Column(db.Integer,primary_key=True); title=db.Column(db.String(180),nullable=False,index=True); content=db.Column(db.Text,default=''); color=db.Column(db.String(16),default='#ffffff'); is_completed=db.Column(db.Boolean,default=False,index=True); is_pinned=db.Column(db.Boolean,default=False,index=True); is_archived=db.Column(db.Boolean,default=False,index=True); is_important=db.Column(db.Boolean,default=False,index=True); deleted_at=db.Column(db.DateTime(timezone=True),index=True); sort_order=db.Column(db.Integer,default=0,index=True); category_id=db.Column(db.Integer,db.ForeignKey('categories.id'),index=True); created_at=db.Column(db.DateTime(timezone=True),default=utcnow,index=True); updated_at=db.Column(db.DateTime(timezone=True),default=utcnow,onupdate=utcnow,index=True)
    category=db.relationship('Category',lazy='joined'); tags=db.relationship('Tag',secondary=note_tags,lazy='selectin'); reminder=db.relationship('Reminder',back_populates='note',uselist=False,cascade='all,delete-orphan')
class Reminder(db.Model):
    __tablename__='reminders'; id=db.Column(db.Integer,primary_key=True); note_id=db.Column(db.Integer,db.ForeignKey('notes.id',ondelete='CASCADE'),nullable=False,unique=True,index=True); reminder_datetime=db.Column(db.DateTime(timezone=True),nullable=False,index=True); repeat_type=db.Column(db.String(20),default='none'); repeat_interval=db.Column(db.Integer,default=1); is_active=db.Column(db.Boolean,default=True,index=True); snooze_until=db.Column(db.DateTime(timezone=True),index=True); last_triggered=db.Column(db.DateTime(timezone=True)); created_at=db.Column(db.DateTime(timezone=True),default=utcnow)
    note=db.relationship('Note',back_populates='reminder')
    @property
    def effective_at(self): return self.snooze_until or self.reminder_datetime
class NotificationLog(db.Model):
    __tablename__='notification_logs'; id=db.Column(db.Integer,primary_key=True); reminder_id=db.Column(db.Integer,db.ForeignKey('reminders.id',ondelete='CASCADE'),nullable=False,index=True); occurrence_key=db.Column(db.String(90),nullable=False); status=db.Column(db.String(20),default='pending',index=True); triggered_at=db.Column(db.DateTime(timezone=True),default=utcnow,index=True); read_at=db.Column(db.DateTime(timezone=True));
    reminder=db.relationship('Reminder',backref=db.backref('notification_logs',cascade='all,delete-orphan'))
    __table_args__=(db.UniqueConstraint('reminder_id','occurrence_key',name='uq_reminder_occurrence'),)
