import uuid

def generate_room_name(username1, username2):
    # Concatenate usernames
    combined_username = ''.join(sorted([username1, username2]))

    # Generate a UUID based on the combined username
    room_uuid = uuid.uuid5(uuid.NAMESPACE_DNS, combined_username)

    # Return the UUID as a string
    return str(room_uuid)