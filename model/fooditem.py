from model.authentication import validate_user, get_item_if_member
from db import get_db
from model.subscription_handler import send_message
from sql_classes import Tag


def update_food_item(info, food_item_id, name=None, expiration=None, tags=None):
    user = validate_user(info)
    if user is not None:
        item = get_item_if_member(food_item_id, user)
        if item is not None:
            if name is not None:
                item.name = name
            if expiration is not None:
                item.expiration = expiration
            # Remove existing tags
            tag_array = []
            for tag in tags:
                food_tag = Tag(tag=tag)
                tag_array.append(food_tag)
            item.tags[:] = tag_array
            db = get_db()
            db.session.commit()

            if "SourceID" in info.context.headers:
                user_ids = [user.id for user in item.storage.household.users]
                send_message(user_ids, info.context.headers["SourceID"], "FoodItem", item, "edit")

            return item
        else:
            raise ValueError("Unable to retrieve item")
    else:
        raise ValueError("User authentication failed")  # TODO: Standardize errors
    return None
