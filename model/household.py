from sql_classes import User, Household, Storage
from model.authentication import validate_user, get_household_if_member, get_household_if_owner
from db import get_db


def create_household(info, name, location):
    user = validate_user(info)
    db = get_db()
    if user is not None:
        try:
            household = Household(name=name, location=location)
            household.owner = user
            household.users.append(user)
            db.session.add(household)
            db.session.commit()
            return household
        except Exception as e:
            raise e
    else:
        raise TypeError("validate_user did not return User")


def update_household(info, name, location, id_):
    user = validate_user(info)
    db = get_db()
    if user is not None:
        household = get_household_if_owner(id_, user)
        if household is None:
            raise ValueError("User it not authorized to update this household")
        try:
            if name is not None:
                household.name = name
            if location is not None:
                household.location = location
            db.session.commit()
            return household
        except Exception as e:
            raise e
    else:
        raise TypeError("validate_user did not return User")


def get_owned_households(info):
    user = validate_user(info)
    if user is not None:
        households = Household.query.filter_by(ownerId=user.id)
        return households
    else:
        raise TypeError("validate_user did not return User")


def get_member_households(info):
    user = validate_user(info)
    if user is not None:
        households = Household.query.filter(Household.users.any(User.id == user.id))
        return households
    else:
        raise TypeError("validate_user did not return User")


def get_household(info, household_id):
    user = validate_user(info)
    if user is not None:
        household = get_household_if_member(household_id, user)
        return household
    else:
        raise TypeError("validate_user did not return User")


def add_storage(info, name, storage_type, household_id):
    from api import app
    app.logger.info(household_id)
    user = validate_user(info)
    db = get_db()
    if user is not None:
        household = get_household_if_member(household_id, user)
        if household is not None:
            try:

                storage = Storage(name=name, type=storage_type)
                storage.household = household
                db.session.add(storage)
                db.session.commit()
                return storage
            except Exception as e:
                raise e
        else:
            raise ValueError("User is not authorized to update this household")
    else:
        raise TypeError("validate_user did not return User")
