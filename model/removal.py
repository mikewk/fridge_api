import boto3

from model.authentication import validate_user, get_item_if_member, get_storage_if_member, get_household_if_owner
from db import get_db


def remove_food_item(info, food_item_id):
    from api import access_key
    from api import secret_key
    user = validate_user(info)
    if user is None:
        raise ValueError("User not authenticated")
    item = get_item_if_member(food_item_id, user)
    if item is None:
        raise ValueError("Unable to retrieve FoodItem")
    storage_id = item.storageId
    filename = item.filename
    db = get_db()
    db.session.delete(item)
    db.session.commit()

    # Remove item from S3
    s3 = boto3.client("s3",
                      aws_access_key_id=access_key,
                      aws_secret_access_key=secret_key)
    print(filename)
    s3.delete_object(Bucket="fridge-app-photos-dev", Key=filename)

    return storage_id


def remove_storage(info, storage_id):
    user = validate_user(info)
    if user is None:
        raise ValueError("User not authenticated")
    storage = get_storage_if_member(storage_id, user)
    if storage is None:
        raise ValueError("Unable to retrieve Storage")
    db = get_db()
    db.session.delete(storage)
    db.session.commit()
    return True


def remove_household(info, household_id):
    user = validate_user(info)
    if user is None:
        raise ValueError("User not authenticated")
    household = get_household_if_owner(household_id, user)
    if household is None:
        raise ValueError("Unable to retrieve Household")
    db = get_db()
    db.session.delete(household)
    db.session.commit()
    return True
