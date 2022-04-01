from model.authentication import validate_user, get_household_if_owner
from sql_classes import Invite


def get_invites(info, household_id):
    user = validate_user(info)
    if user is None:
        raise Exception("Not a valid user")
    household = get_household_if_owner(household_id, user)
    if household is None:
        raise Exception("User not authorized to access household")

    return household.invites


def get_invite(info, invite_id):
    user = validate_user(info)
    if user is None:
        raise Exception("Not a valid user")
    invite = Invite.query.filter_by(id=invite_id).first()
    if invite is None:
        return None
    if user == invite.household.owner:
        raise Exception("Owner can't accept own invite")
    if invite.status == 1:
        if invite.invitee != user:
            return None
        else:
            raise Exception("User has already accepted this invite")
    if invite.status == 2 or invite.status == 3:
        return None

    if user in invite.household.users:
        raise Exception("User already belongs to this household")

    return invite
