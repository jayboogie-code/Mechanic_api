class DevelopmentConfig:
    DEBUG = True
    TESTING = False
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root:09122020@localhost/mechanic_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = "your_secret_key"
    CACHE_TYPE = "SimpleCache"
    
class TestingConfig:
    DEBUG = True
    TESTING = False
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root:09122020@localhost/mechanic_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = "your_secret_key"
    CACHE_TYPE = "SimpleCache"

class ProductionConfig:
    DEBUG = False
    TESTING = False
    DATABASE_URI = 'mysql+mysqlconnector://root:09122020@localhost/mechanic_db'