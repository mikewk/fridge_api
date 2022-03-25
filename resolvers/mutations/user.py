from ariadne import ObjectType, convert_kwargs_to_snake_case

from model.user import change_default_household, reject_household_invite, accept_household_invite, \
    remove_user_from_household, invite_user_to_household

mutation = ObjectType("Mutation")


@mutation.field("changeDefaultHousehold")
@convert_kwargs_to_snake_case
def resolve_default_household(obj, info, household_id):
    try:
        user = change_default_household(info, household_id)
        payload = {"users": [user.to_dict()], "error": None}
    except Exception as e:
        payload = {"households": None, "error": str(e)}

    return payload


@mutation.field("inviteUserToHousehold")
@convert_kwargs_to_snake_case
def resolve_invite_user(obj, info, household_id, message):
    try:
        invite = invite_user_to_household(info, household_id, message)
        payload = {"invites": [invite.to_dict()], "error": None}
    except Exception as e:
        payload = {"invites": None, "error": str(e)}
    return payload


@mutation.field("acceptHouseholdInvite")
@convert_kwargs_to_snake_case
def resolve_accept_invite(obj, info, invite_id):
    try:
        household = accept_household_invite(info, invite_id)
        payload = {"households": [household.to_dict()], "error": None}
    except Exception as e:
        payload = {"households": None, "error": str(e)}
    return payload


@mutation.field("rejectHouseholdInvite")
@convert_kwargs_to_snake_case
def resolver_reject_invite(obj, info, invite_id):

    try:
        reject_household_invite(info, invite_id)
        payload = {"id": -1, "success": 1, "error": None}
    except Exception as e:
        payload = {"id": -1, "success": 0, "error": str(e)}
    return payload


@mutation.field("removeUserFromHousehold")
@convert_kwargs_to_snake_case
def resolve_remove_user(obj, info, user_id):

    try:
        remove_user_from_household(info, user_id)
        payload = {"id": user_id, "success": 1, "error": None}
    except Exception as e:
        payload = {"id": user_id, "success": 0, "error": str(e)}
    return payload
