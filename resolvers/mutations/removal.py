from ariadne import ObjectType, convert_kwargs_to_snake_case
from model.removal import remove_food_item, remove_storage, remove_household, delete_household_invite, \
    remove_user_from_household

mutation = ObjectType("Mutation")


@mutation.field("removeFoodItem")
@convert_kwargs_to_snake_case
def food_item(obj, info, food_item_id):
    try:
        storage_id = remove_food_item(info, food_item_id)
        if storage_id:
            return {"success": 1, "id": storage_id, "error": None}
        else:
            return {"success": 0, "error": "Unknown error occurred"}
    except Exception as e:
        return {"success": 0, "error": str(e)}


@mutation.field("removeStorage")
@convert_kwargs_to_snake_case
def storage(obj, info, storage_id):
    try:
        if remove_storage(info, storage_id):
            return {"success": 1, "error": None}
        else:
            return {"success": 0, "error": "Unknown error occurred"}
    except Exception as e:
        return {"success": 0, "error": str(e)}


@mutation.field("removeHousehold")
@convert_kwargs_to_snake_case
def household(obj, info, household_id):
    try:
        if remove_household(info, household_id):
            return {"success": 1, "error": None}
        else:
            return {"success": 0, "error": "Unknown error occurred"}
    except Exception as e:
        return {"success": 0, "error": str(e)}


@mutation.field("removeUserFromHousehold")
@convert_kwargs_to_snake_case
def resolve_remove_user_from_household(obj, info, user_id, household_id):
    try:
        payload = remove_user_from_household(info, user_id, household_id)
        return {"success": payload, "error": None}
    except Exception as e:
        return {"success": False, "error": str(e)}


@mutation.field("deleteInvite")
@convert_kwargs_to_snake_case
def resolve_cancel_invite(obj, info, invite_id):
    try:
        delete_household_invite(info, invite_id)
        payload = {"id": invite_id, "success": 1, "error": None}
    except Exception as e:
        payload = {"id": invite_id, "success": 0, "error": None}
    return payload
