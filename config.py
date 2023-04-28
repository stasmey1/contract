class Config:
    TESTING = True
    SECRET_KEY = 'SECRET_KEY'
    STATIC_FOLDER = 'static'
    TEMPLATES_FOLDER = 'templates'

    # Database
    SQLALCHEMY_DATABASE_URI = "postgresql://postgres:1234@localhost:5432/contract"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
