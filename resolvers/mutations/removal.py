from ariadne import ObjectType, convert_kwargs_to_snake_case
from model.removal import remove_food_item, remove_storage, remove_household

mutation = ObjectType("Mutation")


@mutation.field("removeFoodItem")
@convert_kwargs_to_snake_case
def food_item(obj, info, food_item_id):
    try:
        if remove_food_item(info, food_item_id):
            return {"success": 1, "error": None}
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

    return None


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

    return None


@mutation.field("removeUserFromHousehold")
@convert_kwargs_to_snake_case
def user_from_household(obj, info):
    return None
