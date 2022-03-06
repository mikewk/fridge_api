from model.authentication import validate_user, get_item_if_member, get_storage_if_member, get_household_if_owner
from db import get_db


def remove_food_item(info, food_item_id):
    user = validate_user(info)
    if user is None:
        raise ValueError("User not authenticated")
    item = get_item_if_member(food_item_id, user)
    if item is None:
        raise ValueError("Unable to retrieve FoodItem")
    db = get_db()
    db.session.delete(item)
    db.session.commit()
    return True


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
