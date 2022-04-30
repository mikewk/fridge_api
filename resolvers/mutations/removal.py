from ariadne import ObjectType, convert_kwargs_to_snake_case
from model.removal import delete_food_item, delete_storage, delete_household, delete_household_invite, \
    remove_user_from_household

mutation = ObjectType("Mutation")


@mutation.field("deleteFoodItem")
@convert_kwargs_to_snake_case
def resolve_delete_food_item(obj, info, food_item_id):
    try:
        storage_id = delete_food_item(info, food_item_id)
        if storage_id:
            return {"success": 1, "id": storage_id, "error": None}
        else:
            return {"success": 0, "error": "Unknown error occurred", "id": storage_id}
    except Exception as e:
        return {"success": 0, "error": str(e), "id": storage_id}


@mutation.field("deleteStorage")
@convert_kwargs_to_snake_case
def resolve_delete_storage(obj, info, storage_id):
    try:
        if delete_storage(info, storage_id):
            return {"success": 1, "error": None, "id": storage_id}
        else:
            return {"success": 0, "error": "Unknown error occurred", "id": storage_id}
    except Exception as e:
        return {"success": 0, "error": str(e), "id": storage_id}


@mutation.field("deleteHousehold")
@convert_kwargs_to_snake_case
def resolve_delete_household(obj, info, household_id):
    try:
        if delete_household(info, household_id):
            return {"success": 1, "error": None, "id": household_id}
        else:
            return {"success": 0, "error": "Unknown error occurred", "id": household_id}
    except Exception as e:
        return {"success": 0, "error": str(e), "id": household_id}


@mutation.field("removeUserFromHousehold")
@convert_kwargs_to_snake_case
def resolve_remove_user_from_household(obj, info, user_id, household_id):
    try:
        payload = remove_user_from_household(info, user_id, household_id)
        return {"success": payload, "error": None, "id": user_id}
    except Exception as e:
        return {"success": False, "error": str(e), "id": user_id}


@mutation.field("deleteInvite")
@convert_kwargs_to_snake_case
def resolve_delete_invite(obj, info, invite_id):
    try:
        delete_household_invite(info, invite_id)
        payload = {"id": invite_id, "success": 1, "error": None}
    except Exception as e:
        payload = {"id": invite_id, "success": 0, "error": str(e)}
    return payload
