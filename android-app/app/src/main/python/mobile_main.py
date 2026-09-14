"""
نقطة الدخول التي يستدعيها MainActivity.java عبر Chaquopy.
تشغّل تطبيق Flask محلياً على 127.0.0.1، وتخزّن قاعدة البيانات
داخل مساحة تخزين التطبيق الخاصة على الهاتف (data_dir من Java:
getFilesDir())، وليس على أي سيرفر خارجي.
"""
import os
from pathlib import Path


def start(data_dir):
    instance_path = str(Path(data_dir) / "instance")
    Path(instance_path).mkdir(parents=True, exist_ok=True)

    # يجعل config.py يخزّن قاعدة SQLite داخل مساحة التطبيق على الهاتف
    os.environ["DATABASE_URL"] = f"sqlite:///{instance_path}/notes.db"
    os.environ["ENABLE_SCHEDULER"] = "true"

    from quicknotes import create_app

    app = create_app(instance_path=instance_path)
    app.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False, threaded=True)
