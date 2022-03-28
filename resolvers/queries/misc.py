from model.household import get_owned_households, get_member_households, get_household
from ariadne import ObjectType, convert_kwargs_to_snake_case

from model.invites import get_invites, get_invite
from model.storage import get_storage
from model.user import get_user

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


@query.field("getStorage")
@convert_kwargs_to_snake_case
def resolve_get_member_households(obj, info, storage_id):
    try:
        storage = get_storage(info, storage_id)
        storage_dict = storage.to_dict()
        payload = {"storages": [storage_dict], "error": None}
    except Exception as e:
        payload = {"storages": None, "error": str(e)}
    return payload


@query.field("getInvites")
@convert_kwargs_to_snake_case
def resolve_get_invites(obj, info, household_id):
    try:
        invites = get_invites(info, household_id)
        payload = {"invites": map(lambda x: x.to_dict(), invites), "error": None}
    except Exception as e:
        payload = {"invites": None, "error": str(e)}

    return payload


@query.field("getInvite")
@convert_kwargs_to_snake_case
def resolve_get_invite(obj, info, invite_id):
    try:
        invite = get_invite(info, invite_id)
        if invite is None:
            payload = {"invites": None, "error": "Invite not found"}
        else:
            payload = {"invites": [invite.to_dict()], "error": None}
    except Exception as e:
        payload = {"invites": None, "error": str(e)}

    return payload


@query.field("getUser")
@convert_kwargs_to_snake_case
def resolve_get_invite(obj, info):
    try:
        user = get_user(info)
        payload = {"users": [user.to_dict()], "error": None}
    except Exception as e:
        payload = {"users": None, "error": str(e)}

    return payload
