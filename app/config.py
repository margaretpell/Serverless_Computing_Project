class Config(object):
    SECRET_KEY = 'asdfg'
    # SQLALCHEMY_ECHO = False
    # SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif'}
    MAX_CONTENT_LENGTH = 16 * 1000 * 1000
    S3BUCKET = 'ece1779a3bucket1'
    FRONTEND_PORT= 5000

