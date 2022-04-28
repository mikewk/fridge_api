from ariadne import ObjectType, convert_kwargs_to_snake_case
from model.household import add_storage
from model.storage import edit_storage

mutation = ObjectType("Mutation")


@mutation.field("addStorageToHousehold")
@convert_kwargs_to_snake_case
def add_to_household(obj, info, name, storage_type, household_id):
    try:
        storage = add_storage(info, name, storage_type, household_id)
        payload = {"storages": [storage.to_dict()], "error": None}
    except Exception as e:
        payload = {"storages": None, "error": str(e)}
    
    return payload


@mutation.field("editStorage")
@convert_kwargs_to_snake_case
def resolve_edit_storage(obj, info, storage_id, name=None, storage_type=None):
    try:
        storage = edit_storage(info, storage_id, name, storage_type)
        payload = {"storages": [storage.to_dict()], "error": None}
    except Exception as e:
        payload = {"storages": None, "error": str(e)}
    
    return payload
