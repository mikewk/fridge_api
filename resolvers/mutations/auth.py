from model.authentication import user_signup, user_login, update_token
from ariadne import ObjectType, convert_kwargs_to_snake_case

mutation = ObjectType("Mutation")


@mutation.field("signup")
@convert_kwargs_to_snake_case
def resolve_signup(obj, info, email, password, name):
    try:
        [token, user] = user_signup(email, password, name)
        payload = {"token": token, "user": user, "error": None}
    except Exception as e:
        payload = {"token": None, "error": str(e)}
        
    return payload


@mutation.field("login")
@convert_kwargs_to_snake_case
def resolve_login(obj, info, email, password):
    try:
        [token, user] = user_login(email, password)
        payload = {"token": token, "user": user.to_dict(), "error": None}
    except Exception as e:
        payload = {"token": None, "error": str(e)}
    
    return payload


@mutation.field("getUpdatedToken")
@convert_kwargs_to_snake_case
def resolve_get_updated_token(obj, info):
    try:
        token = update_token(info)
        payload = {"token": token, "error": None}
    except Exception as e:
        payload = {"token": None, "error": str(e)}

    return payload
