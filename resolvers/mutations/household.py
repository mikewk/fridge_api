from model.household import create_household, update_household
from ariadne import ObjectType, convert_kwargs_to_snake_case

mutation = ObjectType("Mutation")


@mutation.field("createHousehold")
@convert_kwargs_to_snake_case
def resolve_create_household(obj, info, name, location):
    try:
        household = create_household(info, name, location)
        payload = {"households": [household.to_dict()], "error": None}
    except Exception as e:
        payload = {"households": None, "error": str(e)}

    return payload


@mutation.field("updateHousehold")
@convert_kwargs_to_snake_case
def resolve_update_household(obj, info, household_id, name=None, location=None):
    try:
        household = update_household(info, name, location, household_id)
        payload = {"households": [household.to_dict()], "error": None}
    except Exception as e:
        payload = {"households": None, "error": str(e)}

    return payload
