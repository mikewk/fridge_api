import hashlib
import jwt
import binascii
import configparser
import os
from sql_classes import User, Household, Storage, FoodItem
from sqlalchemy import and_
from db import get_db
from datetime import datetime, timedelta

config = configparser.ConfigParser()
config.read(os.getenv("SECRET_PATH"))
my_secret = config["auth"]["secret"]
my_salt = config["auth"]["salt"]


def user_signup(email, password, name):
    db = get_db()
    salt = email.lower() + my_salt  # Not as good as a random salt, but we just won't let users change their username
    try:
        user = User.query.filter_by(email=email).first()
        if user is not None:
            raise ValueError("Email address already has an account")
        my_hash = binascii.hexlify(hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode(), 100000))
        user = User(email=email, passwordHash=my_hash, fullName=name)
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        raise e

    # generate jwt
    dt = datetime.now() + timedelta(days=2)
    payload_data = {"id": user.id, "email": user.email, "exp": dt}
    token = jwt.encode(payload_data, my_secret, algorithm='HS256')
    return [token, user]


def user_login(email, password):
    salt = email.lower() + my_salt
    try:
        my_hash = binascii.hexlify(hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode(), 100000))
        user = User.query.filter_by(email=email, passwordHash=my_hash).first()
        if user is None:
            raise ValueError("Invalid credentials supplied")
    except Exception as e:
        raise e

    return [generate_jwt(user), user]


def generate_jwt(user):
    # generate jwt
    dt = datetime.now() + timedelta(days=2)
    auth_households = [h.folder for h in user.households]
    payload_data = {"id": user.id, "email": user.email, "exp": dt,
                    "name": user.fullName, "authHouseholds": auth_households}
    token = jwt.encode(payload_data, my_secret, algorithm='HS256')
    return token


def update_token(info):
    # Get user if token is still valid
    user = validate_user(info)
    # generate new token
    return generate_jwt(user)


def validate_user(info):
    if "Authorization" in info.context.headers:
        auth = info.context.headers["Authorization"]
        scheme, token = auth.split()
        if scheme.lower() != "bearer":
            raise ValueError("Invalid token")
        try:
            payload = jwt.decode(token, my_secret, algorithms=["HS256"])
            user_id = payload.get("id")

            if user_id is None:
                raise ValueError("Invalid token - Malformed")
            user = User.query.filter_by(id=user_id).first()
            if user is None:
                raise ValueError("Invalid token - User Not Found")

            return user
        except Exception as e:
            raise e
    else:
        raise ValueError("No Authorization found in headers")


def get_item_if_member(item_id, user):
    # First, let's get the item
    item = FoodItem.query.get(item_id) # type: FoodItem
    # If the FoodItem doesn't exist, return none
    if item is None:
        return None

    # Check if the user has access to the storage the item is in, if they don't return none
    storage_id = item.storageId
    storage = get_storage_if_member(storage_id, user)
    if storage is None:
        return None

    # Since they have access to storage, return the item
    return item


def get_storage_if_member(storage_id, user):
    # First step, get the household id of the storage_id
    storage = Storage.query.get(storage_id)
    if storage is None:
        return None

    # next, check if the user is a member of this household
    household_id = storage.householdId
    if get_household_if_member(household_id, user) is None:
        return None
    else:
        return storage


def get_household_if_member(household_id, user):
    # It was doable in one line, hurrah
    household = Household.query.filter(and_(Household.id == household_id,
                                            Household.users.any(User.id == user.id))
                                       ).first()
    return household


def get_household_if_owner(household_id, user):
    household = Household.query.filter_by(id=household_id, owner=user).first()
    return household
