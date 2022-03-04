import hashlib
import jwt
import binascii
from sql_classes import User, Household, Storage
from sqlalchemy import and_
from db import get_db
from datetime import datetime, timedelta

my_secret = "dev_secret_hash"
my_salt = "fridgeapp"

def user_signup(email, password, name):
    db = get_db()
    salt = email + my_salt;
    try:
        user = User.query.filter_by(email=email).first()
        if( user is not None ):
            raise ValueError("Email address already has an account")
        hash = binascii.hexlify(hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode(), 100000))
        user = User(email=email, passwordHash=hash, fullName=name)
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        raise e
        
    #generate jwt
    dt = datetime.now() + timedelta(days=2)
    payload_data = {"id":user.id, "email":user.email, "exp":dt}
    token = jwt.encode(payload_data, my_secret, algorithm='HS256').decode('UTF-8')
    return token



def user_login(email, password):
    db = get_db()
    salt = email + my_salt;
    try:
        hash = binascii.hexlify(hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode(), 100000))
        user = User.query.filter_by(email=email, passwordHash=hash).first()
        if( user is None ):
            raise ValueError("Invalid credentials supplied")  
    except Exception as e:
        raise e
        
    #generate jwt
    dt = datetime.now() + timedelta(days=2)
    payload_data = {"id":user.id, "email":user.email, "exp":dt}
    token = jwt.encode(payload_data, my_secret, algorithm='HS256').decode('UTF-8')
    return token

def validate_user(info):
    from api import app
    if( "Authorization" in info.context.headers ):
        auth = info.context.headers["Authorization"]
        scheme, token = auth.split()
        if( scheme.lower() != "bearer" ):
            raise ValueError("Invalid token")
        try:
            payload = jwt.decode(token, my_secret, algorithms=["HS256"])
            user_id = payload.get("id")
            if( user_id is None ):
                raise ValueError("Invalid token - Malformed")
            user = User.query.filter_by(id=user_id).first()
            if( user is None ):
                raise ValueError("Invalid token - User Not Found")
            return user
        except Exception as e:
            raise e
    else:
        raise ValueError("No Authorization found in headers")
        
def get_storage_if_member(storage_id, user):
    #First step, get the household id of the storage_id
    storage = Storage.query.get(storage_id)
    
    #next, check if the user is a member of this household
    if storage is not None:
        household_id = storage.householdId
        if get_household_if_member(household_id, user) is None:
            return None
        else:
            return storage
    else:
        raise ValueError("Storage does not exist")

def get_household_if_member(household_id, user):
    #It was doable in one line, hurrah
    household = Household.query.filter(and_(Household.id==household_id, Household.users.any(User.id == user.id))).first()
    return household

def get_household_if_owner(household_id, user):
    household = Household.query.filter_by(id=household_id, owner=user).first()
    return household;
    