import boto3

from model.authentication import validate_user, get_item_if_member, get_storage_if_member, get_household_if_owner, \
    get_household_if_member
from db import get_db
from model.user import get_user_by_id
from sql_classes import Invite


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
    db = get_db()
    db.session.delete(item)
    db.session.commit()

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


def delete_household_invite(info, invite_id):
    owner = validate_user(info)
    if owner is None:
        raise Exception("Owner is not a valid user")

    invite = Invite.query.filter_by(id=invite_id).first()
    household_id = invite.householdId
    household = get_household_if_owner(household_id, owner)

    if household is None:
        raise Exception("User not authorized to delete invites from this household")

    db = get_db()
    db.session.delete(invite)
    db.session.commit()
    return True


def remove_user_from_household(info, user_id, household_id):
    owner = validate_user(info)
    if owner is None:
        raise Exception("Owner is not a valid user")

    if user_id == owner.id:
        raise Exception("Owner can not remove themselves from household")

    household = get_household_if_owner(household_id, owner)
    if household is None:
        raise Exception("'Owner' is not authorized to remove users from this household")

    user = get_user_by_id(user_id)
    if user is None:
        raise Exception("User to remove not found")

    household.users.remove(user)
    db = get_db()
    db.session.commit()
    return True


def leave_household(info, household_id):
    user = validate_user(info)
    if user is None:
        raise Exception("User is not a valid user")

    household = get_household_if_member(household_id, user)
    if household is None:
        raise Exception("User is not a member of this household")

    if user.id == household.owner.id:
        raise Exception("Owner is not allowed to leave the household")

    household.users.remove(user)
    db = get_db()
    db.session.commit()
    return True
