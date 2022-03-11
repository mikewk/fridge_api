from sql_classes import FoodItem, Tag
from model.authentication import validate_user, get_storage_if_member
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


def update(info, storage_id, name, storage_type):
    user = validate_user(info)
    db = get_db()
    if user is not None:
        storage = get_storage_if_member(storage_id, user)
        if storage is not None:
            if name is not None:
                storage.name = name
            if storage_type is not None:
                storage.type = storage_type
            db.session.commit()
        else:
            raise ValueError("User is not authorized to update this storage")

    else:
        raise ValueError("User is not authenticated")


def add_food_item(info, storage_id, name, expiration, tags, entered):
    user = validate_user(info)
    db = get_db()
    if user is not None:
        storage = get_storage_if_member(storage_id, user)
        if storage is not None:
            food_item = FoodItem(name=name)
            food_item.enteredBy = user
            food_item.storage = storage
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
            return food_item
        else:
            raise ValueError("User is not authorized to access this storage")
