import asyncio
import model.subscription_handler as handler
from ariadne import convert_kwargs_to_snake_case, SubscriptionType, UnionType

from model.authentication import validate_user

subscription = SubscriptionType()
message_types = UnionType("MessageTypes")


@message_types.type_resolver
async def resolve_messages_type(obj, *_):
    if "_type" in obj:
        return obj["_type"]
    # If it doesn't have a type, it's an AuthPayload
    return "AuthPayload"


@subscription.source("messages")
@convert_kwargs_to_snake_case
async def messages_source(obj, info, source_id, token):
    user = validate_user(info, "Bearer "+token)
    if user is None:
        raise ValueError("User is not valid")
    queue = handler.add_new_queue(source_id, user.id)
    try:
        while True:
            print('{} is listening'.format(source_id))
            message = await queue.get()
            queue.task_done()
            yield message
    except asyncio.CancelledError:
        handler.remove_queue(source_id, user.id)
        raise


@subscription.field("messages")
@convert_kwargs_to_snake_case
async def messages_res(messages, info, source_id, token):
    print("Resolving {}".format(messages))
    return messages
