from sql_classes import User, Household, Storage, FoodItem
from model.authentication import validate_user, get_storage_if_member
from db import get_db


def update(info, storage_id, name, type):
    user = validate_user(info)
    db = get_db()
    if( user is not None ):
        storage = get_storage_if_member(storage_id, user)
        if( storage is not None ):
            if( name is not None ):
                storage.name = name
            if( type is not None ):
                storage.type = type
            db.session.commit()
        else:
            raise ValueError("User is not authorized to update this storage")
    
    else:
        raise ValueError("User is not authenticated")
        
def add_food_item(info, storage_id, name, expiration, tags, entered):
    user = validate_user(info)
    if( user is not None ):
        storage = get_storage_if_member(storage_id, user)
        if( storage is not None):
            foodItem = FoodItem(name=name)
            if( entered is not None):
                foodItem.entered = entered
            if( expiration is not None):
                foodItem.expiration = expiration
            #if( tags is not None):
                #TODO: 
            
            
        else:
            raise ValueError("User is not authorized to access this storage")