import logging

from ariadne import ObjectType, convert_kwargs_to_snake_case
from model.storage import add_food_item
from model.fooditem import update_food_item

mutation = ObjectType("Mutation")


@mutation.field("addFoodItemToStorage")
@convert_kwargs_to_snake_case
def add_to_storage(obj, info, storage_id, name, expiration=None, tags=None, entered=None):
    try:
        food_item = add_food_item(info, storage_id, name, expiration, tags, entered)
        payload = {"foodItems": [food_item.to_dict()], "error": None}
    except Exception as e:
        payload = {"foodItems": None, "error": str(e)}
    return payload


@mutation.field("updateFoodItem")
@convert_kwargs_to_snake_case
def update(obj, info, food_item_id, name=None, expiration=None, tags=None):
    try:
        food_item = update_food_item(info, food_item_id, name, expiration, tags)
        payload = {"foodItems": [food_item.to_dict()], "error": None}
    except Exception as e:
        logging.exception("Uh oh")
        payload = {"foodItems": None, "error": str(e)}
    return payload


@mutation.field("addTagsToFoodItem")
@convert_kwargs_to_snake_case
def add_tags(obj, info):
    return None


@mutation.field("removeTagsFromFoodItem")
@convert_kwargs_to_snake_case
def remove_tags(obj, info):
    return None


@mutation.field("moveFoodItemToStorage")
@convert_kwargs_to_snake_case
def move_to_storage(obj, info):
    return None


