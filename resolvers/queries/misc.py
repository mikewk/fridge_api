from model.household import get_owned_households, get_member_households, get_household
from ariadne import ObjectType, convert_kwargs_to_snake_case
query = ObjectType("Query")


@query.field("getOwnedHouseholds")
@convert_kwargs_to_snake_case
def resolve_get_owned_households(obj, info):
    try:
        households = get_owned_households(info)
        households_dict = map(lambda x: x.to_dict(), households)
        payload = {"households": households_dict, "error": None}
    except Exception as e:
        payload = {"households": None, "error": str(e)}
    return payload


@query.field("getMemberHouseholds")
@convert_kwargs_to_snake_case
def resolve_get_member_households(obj, info):
    try:
        households = get_member_households(info)
        households_dict = map(lambda x: x.to_dict(), households)
        payload = {"households": households_dict, "error": None}
    except Exception as e:
        payload = {"households": None, "error": str(e)}
    return payload


@query.field("getHousehold")
@convert_kwargs_to_snake_case
def resolve_get_member_households(obj, info, household_id):
    try:
        household = get_household(info, household_id)
        household_dict = household.to_dict()
        payload = {"households": [household_dict], "error": None}
    except Exception as e:
        payload = {"households": None, "error": str(e)}
    return payload
