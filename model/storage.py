import os

from model.subscription_handler import send_message
from sql_classes import FoodItem, Tag, Storage
from model.authentication import validate_user
from model.authorization import get_storage_if_member, get_storage_if_owner
from db import get_db


def get_storage(info, storage_id):
    user = validate_user(info)
    if user is not None:
        storage = get_storage_if_member(storage_id, user)
        if storage is not None:
            return storage
        else:
            raise ValueError("User is not authorized to view this storage")

    else:
        raise ValueError("User is not authenticated")


def edit_storage(info, storage_id, name, storage_type):
    user = validate_user(info)
    db = get_db()
    if user is not None:
        storage = get_storage_if_owner(storage_id, user)
        if storage is not None:
            if name is not None:
                storage.name = name
            if storage_type is not None:
                storage.type = storage_type
            db.session.commit()

            # Send a message if we have a source id
            if "SourceID" in info.context.headers:
                user_ids = [user.id for user in storage.household.users]
                send_message(user_ids, info.context.headers["SourceID"], "Storage", storage, "edit")
            return storage

        else:
            raise ValueError("User is not authorized to update this storage")

    else:
        raise ValueError("User is not authenticated")


def add_food_item(info, storage_id, name, expiration, tags, entered, filename):
    from api import access_key
    from api import secret_key
    import boto3

    user = validate_user(info)
    db = get_db()
    if user is not None:
        storage = get_storage_if_member(storage_id, user)  # type: Storage
        if storage is not None:
            # get household from storage
            household = storage.household
            folder = household.folder

            food_item = FoodItem(name=name)
            food_item.enteredBy = user
            food_item.storage = storage
            if filename is not None:
                food_item.filename = folder+"/"+filename
            else:
                food_item.fileName = None
            if entered is not None:
                food_item.entered = entered
            if expiration is not None:
                food_item.expiration = expiration

            if tags is not None:
                # Go through each tag, create a tag, append it to the food item
                for tag in tags:
                    food_tag = Tag(tag=tag)
                    food_item.tags.append(food_tag)

            db.session.add(food_item)
            db.session.commit()

            # upload image to bucket

            if filename is not None:
                s3 = boto3.client("s3",
                                  aws_access_key_id=access_key,
                                  aws_secret_access_key=secret_key)
                try:
                    from api import upload_base
                    s3.upload_file(Filename=os.path.join(upload_base, filename),
                                   Bucket="fridge-app-photos-dev",
                                   Key=folder+"/"+filename)
                except Exception as e:
                    # We don't want file upload exceptions to kill the return, so... I dunno, log it?
                    print(str(e))
            # Send a message if we have a source id
            if "SourceID" in info.context.headers:
                user_ids = [user.id for user in household.users]
                send_message(user_ids, info.context.headers["SourceID"], "FoodItem", food_item, "add")

            return food_item
        else:
            raise ValueError("User is not authorized to access this storage")
