import asyncio
from typing import Dict
from collections import defaultdict

# Someplace to store all our queues
allQueues: defaultdict[int, Dict[str, asyncio.Queue]] = defaultdict(lambda: {})


def add_new_queue(source_id, user_id):
    # Create our dictionary of source_id/queue for this user if we don't have them
    if user_id not in allQueues:
        allQueues[user_id] = dict()

    # make sure we don't already have a queue for this source id
    if source_id not in allQueues[user_id]:
        allQueues[user_id][source_id] = asyncio.Queue()

    return allQueues[user_id][source_id]


def remove_queue(source_id, user_id):
    if user_id in allQueues:  # check if we have queues for this user
        if source_id in allQueues[user_id]:  # check if we have a queue for this source_id
            print("Removing {} from user {} queue".format(source_id, user_id))
            allQueues[user_id].pop(source_id)
            # If this is the last queue for the user, let's remove the user from the queue list
            if len(allQueues[user_id]) == 0:
                allQueues[user_id].clear()
            return True
    return False


def send_message(user_ids, source_id, item_type, item, action):
    message = {"type": item_type, "action": action, "message": item.to_dict()}
    print("Sending {} to {} from {}".format(message, user_ids, source_id))
    for user_id in user_ids:   # iterate over our user ids
        for source, queue in allQueues[user_id].items():  # Since we use a default queue, we can skip checking user_id
            if source != source_id:  # make sure we don't send the message back to the source
                try:
                    queue.put_nowait(message)  # Finally, send the message
                except Exception as e:
                    print(str(e))  # Let's just print this out for now
