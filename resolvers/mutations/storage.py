from ariadne import ObjectType, convert_kwargs_to_snake_case
from model.household import add_storage
from model.storage import update
import traceback
mutation = ObjectType("Mutation")

@mutation.field("addStorageToHousehold")
@convert_kwargs_to_snake_case
def add_to_household(obj, info, name, type, household_id):
    try:
        storage = add_storage(info, name, type, household_id)
        payload = {"storages":[storage.to_dict()], "error":None}
    except Exception as e:
        payload = {"storages":None, "error": str(e)}
    
    return payload

@mutation.field("updateStorage")
@convert_kwargs_to_snake_case
def update(obj, info, id, name=None, type=None):
    try:
        storages = update(info, id, name, type)
        payload = {"storages":[storage.to_dict()], "error":None}
    except Exception as e:
        payload = {"storages":None, "error": str(e)}
    
    return payload

