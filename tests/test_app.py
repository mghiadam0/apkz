from datetime import datetime,timezone,timedelta
from quicknotes.extensions import db
from quicknotes.models import Note,Reminder,NotificationLog
from quicknotes.services.reminder_service import process_due,next_occurrence
def test_create_search_update_delete(client,app):
    r=client.post('/notes/',data={'title':'Doctor','content':'Call at ten','tags':'health'}); assert r.status_code==201; nid=r.json['id']
    assert b'Doctor' in client.get('/notes/?q=Doctor').data
    assert client.patch(f'/notes/{nid}',json={'is_pinned':True,'is_completed':True}).json['pinned']
    assert client.delete(f'/notes/{nid}').status_code==204
    assert client.post(f'/notes/{nid}/restore').status_code==200
def test_reminder_snooze_and_dedup(client,app):
    with app.app_context():
        n=Note(title='Due'); n.reminder=Reminder(reminder_datetime=datetime.now(timezone.utc)-timedelta(seconds=1)); db.session.add(n); db.session.commit(); process_due(app); process_due(app); assert NotificationLog.query.count()==1; lid=NotificationLog.query.first().id
    assert client.post(f'/reminders/notifications/{lid}/snooze',json={'minutes':5}).status_code==204
def test_recurrence():
    d=datetime(2026,1,31,tzinfo=timezone.utc); assert next_occurrence(d,'monthly').month==2; assert next_occurrence(d,'daily')>d
def test_import_export(client):
    import io,json
    data={'notes':[{'title':'Restored','content':'ok'}]}; r=client.post('/data/import',data={'file':(io.BytesIO(json.dumps(data).encode()),'b.json')}); assert r.status_code==200; assert b'Restored' in client.get('/data/export').data
def test_database_integrity(app):
    with app.app_context():
        n=Note(title='x'); n.reminder=Reminder(reminder_datetime=datetime.now(timezone.utc)); db.session.add(n); db.session.commit(); db.session.delete(n); db.session.commit(); assert Reminder.query.count()==0
