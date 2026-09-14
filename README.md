# Quick Notes & Reminders — ملاحظاتي السريعة

تطبيق Flask سريع للملاحظات والتنبيهات، يعمل محليًا بعد تثبيت الحزم ويدعم العربية RTL والفرنسية والإنجليزية، الوضع الليلي، التقويم، PWA، الاستيراد/التصدير، الأرشيف وسلة المحذوفات.

## المعمارية
- **Application Factory + Blueprints** لفصل الواجهة، الملاحظات، التنبيهات والنسخ الاحتياطي.
- **SQLAlchemy** مع SQLite افتراضيًا و`DATABASE_URL` للانتقال إلى PostgreSQL.
- **APScheduler** يفحص المواعيد المستحقة كل 15 ثانية. كل occurrence يملك مفتاحًا فريدًا في `notification_logs` لمنع التكرار.
- المواعيد مخزنة UTC. واجهة `<input datetime>` تُحوّل وقت الجهاز إلى UTC.
- Browser Notification + مركز تنبيهات داخل التطبيق. يعمل المجدول ما دام خادم Flask يعمل، حتى مع التنقل بين الصفحات وإعادة تشغيله.

> تنبيه صريح: Service Worker وحده لا يستطيع إيقاظ خادم محلي مغلق أو تنفيذ Web Push حقيقي. للحصول على إشعارات هاتف والخادم/المتصفح مغلقان، يلزم HTTPS وVAPID وخدمة Push عامة. التطبيق لا يدّعي خلاف ذلك؛ البديل المحلي الموثوق هو سجل قاعدة البيانات + APScheduler + polling عند فتح PWA.

## التشغيل
```bash
python -m venv venv
# Linux/macOS
source venv/bin/activate
# Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python app.py
```
ثم افتح http://127.0.0.1:5000

## الاختبارات
```bash
pytest -q
```

## النشر على Render
- Build: `pip install -r requirements.txt`
- Start: `gunicorn --workers 1 --threads 4 app:app`
- عيّن `SECRET_KEY`, `DATABASE_URL`, `APP_TIMEZONE`, `ENABLE_SCHEDULER=true`.
- استخدم عاملاً واحدًا للمجدول. عند التوسع لعدة workers افصل scheduler إلى worker واحد أو استخدم قفلًا موزعًا.

## الأمان
CSRF، ORM، auto-escaping، حدود طول المدخلات وحجم الطلب، cookies HttpOnly/SameSite، hashing جاهز في User model. غيّر `SECRET_KEY` وفعل Secure cookies خلف HTTPS. وضع المستخدم المحلي هو الافتراضي؛ `AUTH_ENABLED` نقطة توسع، ولا تعرض التطبيق للإنترنت متعدد المستخدمين قبل إضافة routes المصادقة والسياسات الخاصة بالملكية.

## النسخ الاحتياطي
`GET /data/export` يصدر JSON. الاستيراد متاح عبر `POST /data/import` باسم حقل `file`، ومحدود إلى 5000 سجل لكل طلب.

## الاختصارات
- `Ctrl/Cmd + N`: ملاحظة جديدة
- `Ctrl/Cmd + K`: البحث
