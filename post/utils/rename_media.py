import os


def rename_media(instance, file_name):
    """
    Renames the media file.
    :param instance:
    :param file_name:
    :return:
    """
    post_id = instance.id
    basename, ext = os.path.splitext(file_name)
    new_file = f'{post_id}{ext}'

    username = instance.user.username
    
    path = os.path.join(username, new_file)

    return path