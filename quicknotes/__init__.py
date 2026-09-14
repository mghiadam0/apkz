from pathlib import Path
from datetime import timezone
from zoneinfo import ZoneInfo
from flask import Flask,session,request
from .extensions import db,csrf
from .i18n import TEXT
from .models import Category
DEFAULTS=[('شخصي','📌'),('عمل','💼'),('دراسة','📚'),('مشتريات','🛒'),('صحة','🏥'),('مالية','💰'),('اتصالات','📞'),('مهم','⭐')]
def create_app(test_config=None):
    app=Flask(__name__,instance_relative_config=True); app.config.from_object('config.Config')
    if test_config:app.config.update(test_config)
    Path(app.instance_path).mkdir(parents=True,exist_ok=True); db.init_app(app); csrf.init_app(app)
    from .routes.main import bp as main; from .routes.notes import bp as notes; from .routes.reminders import bp as reminders; from .routes.data import bp as data
    for b in (main,notes,reminders,data):app.register_blueprint(b)
    @app.template_filter('localdt')
    def localdt(value,fmt='%d/%m/%Y %H:%M'):
        if not value:return ''
        value=value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value
        return value.astimezone(ZoneInfo(app.config['APP_TIMEZONE'])).strftime(fmt)
    @app.context_processor
    def ctx():
        lang=session.get('lang','ar'); return {'lang':lang,'dir':'rtl' if lang=='ar' else 'ltr','t':lambda k:TEXT.get(lang,TEXT['ar']).get(k,k)}
    @app.post('/preferences/language')
    def language():
        lang=(request.get_json() or {}).get('language','ar'); session['lang']=lang if lang in TEXT else 'ar'; return ('',204)
    with app.app_context():
        db.create_all()
        if not Category.query.first(): db.session.add_all([Category(name=n,icon=i) for n,i in DEFAULTS]); db.session.commit()
    if app.config.get('ENABLE_SCHEDULER') and not app.testing:
        from .services.reminder_service import start_scheduler
        app.extensions['reminder_scheduler']=start_scheduler(app)
    return app
