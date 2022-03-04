from ariadne import ObjectType, convert_kwargs_to_snake_case

mutation = ObjectType("Mutation")


@mutation.field("removeFoodItem")
@convert_kwargs_to_snake_case
def food_item(obj, info):
    return None


@mutation.field("removeStorage")
@convert_kwargs_to_snake_case
def storage(obj, info):
    return None


@mutation.field("removeHousehold")
@convert_kwargs_to_snake_case
def household(obj, info):
    return None


@mutation.field("removeUserFromHousehold")
@convert_kwargs_to_snake_case
def user_from_household(obj, info):
    return None
