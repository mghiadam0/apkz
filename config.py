import os
from pathlib import Path
BASE_DIR=Path(__file__).resolve().parent
class Config:
    SECRET_KEY=os.getenv('SECRET_KEY','dev-only-change-me')
    SQLALCHEMY_DATABASE_URI=os.getenv('DATABASE_URL',f"sqlite:///{BASE_DIR/'instance'/'notes.db'}").replace('postgres://','postgresql+psycopg://',1)
    SQLALCHEMY_TRACK_MODIFICATIONS=False
    SQLALCHEMY_ENGINE_OPTIONS={'pool_pre_ping':True}
    APP_TIMEZONE=os.getenv('APP_TIMEZONE','Africa/Casablanca')
    AUTH_ENABLED=os.getenv('AUTH_ENABLED','false').lower()=='true'
    ENABLE_SCHEDULER=os.getenv('ENABLE_SCHEDULER','true').lower()=='true'
    WTF_CSRF_TIME_LIMIT=None
    SESSION_COOKIE_HTTPONLY=True
    SESSION_COOKIE_SAMESITE='Lax'
    SESSION_COOKIE_SECURE=os.getenv('SESSION_COOKIE_SECURE','false').lower()=='true'
    MAX_CONTENT_LENGTH=2*1024*1024
