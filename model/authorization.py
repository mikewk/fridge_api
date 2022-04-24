from sqlalchemy import and_

from sql_classes import FoodItem, Storage, Household, User


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
