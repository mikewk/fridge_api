from model.authentication import validate_user, get_item_if_member
from db import get_db


def update_food_item(info, food_item_id, name=None, expiration=None):
    user = validate_user(info)
    if user is not None:
        item = get_item_if_member(food_item_id, user)
        if item is not None:
            if name is not None:
                item.name = name
            if expiration is not None:
                item.expiration = expiration
            db = get_db()
            db.session.commit()
            return item
        else:
            raise ValueError("Unable to retrieve item")
    else:
        raise ValueError("User authentication failed") # TODO: Standardize errors
    return None
