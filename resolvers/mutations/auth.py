import asyncio

from model.authentication import user_signup, user_login, refresh_token, send_password_reset, try_password_reset, \
    edit_username, edit_password
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


@mutation.field("refreshToken")
@convert_kwargs_to_snake_case
def resolve_refresh_token(obj, info):
    try:
        token = refresh_token(info)
        payload = {"token": token, "error": None}
    except Exception as e:
        payload = {"token": None, "error": str(e)}

    return payload


@mutation.field("sendPasswordReset")
@convert_kwargs_to_snake_case
def resolve_send_password_reset(obj, info, email, url_root, url_signature):
    from api import loop
    print("Resolving send_password_reset")
    try:
        asyncio.run_coroutine_threadsafe(send_password_reset(email, url_root, url_signature, info.context.remote_addr), loop)
        return "Email Sent"
    except Exception as e:
        print(str(e))
        return "Email Sent"


@mutation.field("tryPasswordReset")
@convert_kwargs_to_snake_case
def resolve_send_password_reset(obj, info, password, key):
    print("Resolving try_password_reset")
    try:
        payload = try_password_reset(password, key)
        return payload
    except Exception as e:
        print(str(e))
        return "An error occurred"


@mutation.field("changeUsername")
@convert_kwargs_to_snake_case
def resolve_edit_username(obj, info, email, password):
    print("Resolving changeUsername")
    try:
        token = edit_username(info, email, password)
        payload = {"token": token, "error": None}
    except Exception as e:
        payload = {"token": None, "error": str(e)}

    return payload


@mutation.field("changePassword")
@convert_kwargs_to_snake_case
def resolve_edit_password(obj, info, old_password, new_password):
    print("Resolving change password")
    try:
        token = edit_password(info, old_password, new_password)
        payload = {"token": token, "error": None}
    except Exception as e:
        payload = {"token": None, "error": str(e)}

    return payload
