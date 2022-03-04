from sql_classes import User
from model.authentication import validate_user
from db import get_db

def get_user(user_id):
    user = User.query.filter_by(id=user_id).first()
    return user