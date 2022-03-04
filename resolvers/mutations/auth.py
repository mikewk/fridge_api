from model.authentication import user_signup, user_login
from ariadne import ObjectType, convert_kwargs_to_snake_case

mutation = ObjectType("Mutation")


@mutation.field("signup")
@convert_kwargs_to_snake_case
def resolve_signup(obj, info, email, password, name):
    try:
        token = user_signup(email, password, name)
        payload = {"token": token, "error": None}
    except Exception as e:
        payload = {"token": None, "error": str(e)}
        
    return payload


@mutation.field("login")
@convert_kwargs_to_snake_case
def resolve_login(obj, info, email, password):
    try:
        token = user_login(email, password)
        payload = {"token": token, "error": None}
    except Exception as e:
        payload = {"token": None, "error": str(e)}
    
    return payload
