import os
class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY=os.environ.get("SECRET_KEY")
    SESSION_PERMANENT = False
    SESSION_TYPE = "filesystem"
    DATABASE_URL = os.environ.get("DATABASE_URL")

class ProductionConfig(Config):
    DEBUG = False
    
class DevelopmentConfig(Config):
    ENV = "development"
    DEVELOPMENT = True
    DEBUG = os.environ.get("DEBUG")