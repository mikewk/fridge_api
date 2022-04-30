import hashlib
import uuid

import jwt
import binascii
import configparser
import os

from model.emailer import send_email
from sql_classes import User, PasswordResets
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
    salt_base = str(uuid.uuid4())
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
        if not valid_hash(password, salt, user.passwordHash):
            raise ValueError("Invalid credentials supplied - password")
    except Exception as e:
        raise e

    return generate_jwt(user)


def valid_hash(password, salt, target_hash):
    my_hash = str(do_hash(password, salt))
    return target_hash == my_hash


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


def edit_username(info, new_username, password):
    user = validate_user(info)
    # validate password
    if not valid_hash(password, user.salt+my_salt, user.passwordHash):
        raise ValueError("Invalid Password")

    # update user
    user.email = new_username
    db = get_db()
    db.session.commit()

    return generate_jwt(user)


def edit_password(info, old_password, new_password):
    user = validate_user(info)
    # validate password
    if not valid_hash(old_password, user.salt + my_salt, user.passwordHash):
        raise ValueError("Invalid Password")

    # generate new salt and password hash
    new_salt = str(uuid.uuid4())
    new_password_hash = do_hash(new_password, new_salt + my_salt)

    #update user
    user.passwordHash = new_password_hash
    user.salt = new_salt
    db = get_db()
    db.session.commit()

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


def try_password_reset(password, key):
    # First, let's try to get the password reset data
    password_reset = PasswordResets.query.filter_by(token=key, status=0).first()
    if password_reset is None:
        return "Reset link invalid"

    # Check if link is expired
    valid_time = datetime.utcnow() - timedelta(minutes=30)
    if valid_time > password_reset.created:
        return "Reset link expired"

    # TODO: We can do more checks here, especially against the IP address, to look for attacks

    # If there are no validity problems, let's change the password
    user = User.query.filter_by(id=password_reset.user_id).first()
    if user is None:
        return "User not longer exists"

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
    user = User.query.filter_by(email=email).first()
    if user is None:
        return False

    # Verify url_root
    signature = do_hash(url_root, url_secret)
    if signature != url_signature:
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
        return False

    # Build DB entry
    new_uuid = uuid.uuid4()
    pass_reset = PasswordResets()
    pass_reset.user = user
    pass_reset.status = 0
    pass_reset.token = new_uuid
    pass_reset.request_ip = remote_ip
    db = get_db()
    db.session.add(pass_reset)
    db.session.commit()

    # build URL
    url = url_root + "auth/reset/" + str(new_uuid)
    try:
        await send_email(user.email, "Fridge Tracker Password Reset", emailTemplate.format(url))
    except Exception as e:
        print(str(e))
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