import uuid

from model.authentication import validate_user, get_household_if_member, get_household_if_owner
from sql_classes import User, Invite

from db import get_db


def get_user(info):
    user = validate_user(info)
    if user is None:
        raise Exception("Not a valid user")
    return user


def get_user_by_id(user_id):
    user = User.query.filter_by(id=user_id).first()
    return user


def change_default_household(info, household_id):
    user = validate_user(info)
    if user is None:
        raise Exception("Not a valid user")

    household = get_household_if_member(household_id, user)
    if household is None:
        raise Exception("User not authorized to access household")
    db = get_db()
    user.defaultHousehold = household
    db.session.commit()
    return household


def invite_user_to_household(info, household_id, message):
    owner = validate_user(info)
    if owner is None:
        raise Exception("Owner is not a valid user")

    household = get_household_if_owner(household_id, owner)
    if household is None:
        raise Exception("User not authorized to invite to this household")

    invite = Invite()
    invite.id = str(uuid.uuid1())
    invite.household = household
    invite.status = 0
    invite.message = message

    db = get_db()
    db.session.add(invite)
    db.session.commit()
    return invite


def accept_household_invite(info, invite_id):
    user = validate_user(info)
    if user is None:
        raise Exception("Not a valid user")

    invite = Invite.query.with_for_update().filter_by(id=invite_id).first()
    if invite is None:
        raise Exception("Invite not valid")

    if invite.household.owner == user:
        raise Exception("Owner can't join own household")

    if invite.status == 0:
        invite.status = 1
        invite.invitee = user
        invite.household.users.append(user)
        if user.defaultHousehold is None:
            user.defaultHousehold = invite.household

        db = get_db()
        db.session.commit()
    elif invite.status == 4:
        raise Exception("Invite has expired")
    else:
        raise Exception("Invite is invalid")

    return invite.household


def reject_household_invite(info, invite_id):
    user = validate_user(info)
    if user is None:
        raise Exception("Not a valid user")

    db = get_db()
    invite = Invite.query.with_for_update().filter_by(id=invite_id).first()
    if invite.status == 0:
        invite.status = 2
    elif invite.status == 1:
        raise Exception("Invite already accepted")

    db.session.commit()
    return True
