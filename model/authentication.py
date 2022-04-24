import hashlib
import uuid

import jwt
import binascii
import configparser
import os

from model.emailer import send_email
from sql_classes import User, Household, Storage, FoodItem, PasswordResets
from sqlalchemy import and_
from db import get_db
from datetime import datetime, timedelta

config = configparser.ConfigParser()
config.read(os.getenv("SECRET_PATH"))
my_secret = config["auth"]["secret"]
my_salt = config["auth"]["salt"]
url_secret = config["auth"]["urlsecret"]


def user_signup(email, password, name):
    db = get_db()
    salt_base = str(uuid.uuid1())
    salt = salt_base + my_salt  # Now as good as a random salt
    try:
        user = User.query.filter_by(email=email).first()
        if user is not None:
            raise ValueError("Email address already has an account")
        my_hash = do_hash(password, salt)
        user = User(email=email, passwordHash=my_hash, fullName=name, salt=salt_base)
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        raise e

    # generate jwt
    dt = datetime.now() + timedelta(days=2)
    payload_data = {"id": user.id, "email": user.email, "exp": dt}
    token = jwt.encode(payload_data, my_secret, algorithm='HS256')
    return token


def user_login(email, password):
    try:
        user = User.query.filter_by(email=email).first()
        if user is None:
            raise ValueError("Invalid credentials supplied - username")
        salt = user.salt + my_salt
        my_hash = do_hash(password, salt)
        if user.passwordHash != str(my_hash):
            print(user.passwordHash);
            print(str(my_hash))
            raise ValueError("Invalid credentials supplied - password")
    except Exception as e:
        raise e

    return generate_jwt(user)


def do_hash(password, salt):
    return binascii.hexlify(hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'),
                                                salt.encode(), 100000)).decode("ascii")


def generate_jwt(user):
    # generate jwt
    dt = datetime.now() + timedelta(days=2)
    auth_households = [h.folder for h in user.households]
    payload_data = {"id": user.id, "email": user.email, "exp": dt,
                    "name": user.fullName, "authHouseholds": auth_households}
    token = jwt.encode(payload_data, my_secret, algorithm='HS256')
    return token


def refresh_token(info):
    # Get user if token is still valid
    user = validate_user(info)
    # generate new token
    return generate_jwt(user)


def validate_user(info, token=None):
    if token is None and "Authorization" in info.context.headers:
        auth = info.context.headers["Authorization"]
    else:
        auth = token

    if auth is not None:
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


def try_password_reset(password, key):
    # First, let's try to get the password reset data
    password_reset = PasswordResets.query.filter_by(token=key, status=0).first()
    if password_reset is None:
        return "Reset link invalid"

    # Check if link is expired
    valid_time = datetime.utcnow() - timedelta(minutes=30)
    if valid_time > password_reset.created:
        print(str(valid_time))
        print(str(password_reset.created))
        return "Reset link expired"

    # TODO: We can do more checks here, especially against the IP address, to look for attacks

    # If there are no validity problems, let's change the password
    user = User.query.filter_by(id=password_reset.user_id).first()
    if user is None:
        return "User not longer exists"
    print(str(user))
    print(user.passwordHash)
    print(user.email)
    # Let's make a new salt
    salt_base = str(uuid.uuid1())
    salt = salt_base + my_salt
    my_hash = do_hash(password, salt)
    db = get_db()
    user.passwordHash = my_hash
    user.salt = salt_base
    password_reset.status = 1
    db.session.commit()
    return "Success"


async def send_password_reset(email, url_root, url_signature, remote_ip):
    print("Doing send_password_reset")
    user = User.query.filter_by(email=email).first()
    print("Checking user")
    if user is None:
        print("No user found")
        return False

    # Verify url_root
    print("Checking signature")
    signature = do_hash(url_root, url_secret)
    if signature != url_signature:
        print("Signatures don't match!")
        print("Our sig")
        print(signature)
        print("Given sig")
        print(url_signature)
        return False

    # check for abusive request from a single IP
    check_dt = datetime.utcnow() - timedelta(minutes=30)
    try:
        pass_resets = PasswordResets.query.filter(and_(PasswordResets.created >= check_dt,
                                                       PasswordResets.request_ip == remote_ip)).count()
    except Exception as e:
        print(str(e))
        return False

    if pass_resets >= 4:
        print("Too many password requests")
        return False

    # Build DB entry
    print("Building DB Entry")
    new_uuid = uuid.uuid4()
    pass_reset = PasswordResets()
    pass_reset.user = user
    pass_reset.status = 0
    pass_reset.token = new_uuid
    pass_reset.request_ip = remote_ip
    db = get_db()
    db.session.add(pass_reset)
    db.session.commit()

    print("Building URL")
    # build URL
    url = url_root + "auth/reset/" + str(new_uuid)
    print("Sending email")
    try:
        await send_email(user.email, "Fridge Tracker Password Reset", emailTemplate.format(url))
    except Exception as e:
        print(str(e))
    print("Email sent")
    return True


emailTemplate = '''\
<html>
<head></head>
<body>
<p>We received a password reset request for the Fridge Tracker account at this email address.</p>
<p>If you do not have a Fridge Tracker account or did not request this reset, you can ignore this email</p>
<p>Otherwise, if you want to reset your password, use <a href="{}">this link</a></p>
<p>Thank you,<br>
The Team at Fridgetracker.co</p>
</body>
'''