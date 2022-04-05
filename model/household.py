import uuid
import boto3

from model.subscription_handler import send_message
from sql_classes import User, Household, Storage
from model.authentication import validate_user, get_household_if_member, get_household_if_owner
from db import get_db


def create_household(info, name, location):
    from api import config
    user = validate_user(info)
    db = get_db()
    if user is not None:
        try:
            folder = str(uuid.uuid1())
            household = Household(name=name, location=location, folder=folder)
            household.owner = user
            household.users.append(user)
            db.session.add(household)
            db.session.commit()

            if user.defaultHousehold is None:
                user.defaultHousehold = household

            db.session.commit()
            access_key = config["auth"]["awsid"]
            secret_key = config["auth"]["awssecret"]

            s3=boto3.client("s3",
                            aws_access_key_id=access_key,
                            aws_secret_access_key=secret_key)

            response = s3.put_object(Bucket="fridge-app-photos-dev", Key=(folder+'/'))
            print(response)

            return household
        except Exception as e:
            raise e
    else:
        raise TypeError("validate_user did not return User")


def update_household(info, name, location, id_):
    user = validate_user(info)
    db = get_db()
    if user is not None:
        household = get_household_if_owner(id_, user)
        if household is None:
            raise ValueError("User it not authorized to update this household")
        try:
            if name is not None:
                household.name = name
            if location is not None:
                household.location = location
            db.session.commit()
            return household
        except Exception as e:
            raise e
    else:
        raise TypeError("validate_user did not return User")


def get_owned_households(info):
    user = validate_user(info)
    if user is not None:
        households = Household.query.filter_by(ownerId=user.id)
        return households
    else:
        raise TypeError("validate_user did not return User")


def get_member_households(info):
    user = validate_user(info)
    if user is not None:
        households = Household.query.filter(Household.users.any(User.id == user.id))
        return households
    else:
        raise TypeError("validate_user did not return User")


def get_household(info, household_id):
    user = validate_user(info)
    if user is None:
        raise TypeError("User is not valid")

    household = get_household_if_member(household_id, user)
    if household is None:
        raise TypeError("User not authorized to access this household")

    return household


def add_storage(info, name, storage_type, household_id):
    from api import app
    app.logger.info(household_id)
    user = validate_user(info)
    db = get_db()
    if user is not None:
        household = get_household_if_member(household_id, user)
        if household is not None:
            try:
                storage = Storage(name=name, type=storage_type)
                storage.household = household
                db.session.add(storage)
                db.session.commit()
                if "SourceID" in info.context.headers:
                    user_ids = [user.id for user in storage.household.users]
                    send_message(user_ids, info.context.headers["SourceID"], "Storage", storage, "add")
                return storage
            except Exception as e:
                raise e
        else:
            raise ValueError("User is not authorized to update this household")
    else:
        raise TypeError("validate_user did not return User")
