import logging
import os
import traceback
import uuid
from time import sleep
from urllib import request

from ariadne import ObjectType, convert_kwargs_to_snake_case
from model.storage import add_food_item
from model.fooditem import edit_food_item

mutation = ObjectType("Mutation")


@mutation.field("addFoodItemToStorage")
@convert_kwargs_to_snake_case
def add_to_storage(obj, info, storage_id, name, expiration=None, tags=None, entered=None, filename=None):
    try:
        food_item = add_food_item(info, storage_id, name, expiration, tags, entered, filename)
        payload = {"foodItems": [food_item.to_dict()], "error": None}
    except Exception as e:
        payload = {"foodItems": None, "error": str(e)}
    return payload


@mutation.field("editFoodItem")
@convert_kwargs_to_snake_case
def update(obj, info, food_item_id, name=None, expiration=None, tags=None):
    try:
        food_item = edit_food_item(info, food_item_id, name, expiration, tags)
        payload = {"foodItems": [food_item.to_dict()], "error": None}
    except Exception as e:
        logging.exception("Uh oh")
        payload = {"foodItems": None, "error": str(e)}
    return payload


@mutation.field("getSuggestions")
@convert_kwargs_to_snake_case
def resolve_get_suggestions(obj, info, image):
    from api import upload_base
    sleep(3)
    # Generate uuid for image
    filename = str(uuid.uuid1())
    if image is not None:
        try:
            with request.urlopen(image) as response:
                data = response.read()
            with open(os.path.join(upload_base, filename), "wb") as f:
                f.write(data)
        except Exception as e:
            traceback.print_exception(e)
            return {"suggestion": None, "error": "File upload failed"}

    try:
        payload = {"suggestion":
                   {"name": "TODO: Bethany",
                    "tags": ["Definitely", "Not", "Ai"],
                    "filename": filename},
                   "error": None}
    except Exception as e:
        payload = {"suggestion": None, "error": str(e)}
    return payload


@mutation.field("addTagsToFoodItem")
@convert_kwargs_to_snake_case
def add_tags(obj, info):
    return None


@mutation.field("deleteTagsFromFoodItem")
@convert_kwargs_to_snake_case
def remove_tags(obj, info):
    return None


@mutation.field("moveFoodItemToStorage")
@convert_kwargs_to_snake_case
def move_to_storage(obj, info):
    return None
