from flask_sqlalchemy import SQLAlchemy

_connection = None
_app = None


def init_app(app):
    global _app
    if _app is None:
        _app = app


def get_db():
    global _connection
    global _app
    if _connection is None:
        if _app is not None:
            _connection = SQLAlchemy(_app)
        else:
            raise TypeError("Horrible situation: app not initialized in db connector")
    return _connection
