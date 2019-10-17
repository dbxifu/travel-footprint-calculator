from datetime import datetime
from uuid import uuid4


def generate_unique_id():
    """
    :return: a unique identifier that can be sorted chronologically.
    """
    return datetime.now().strftime('%Y-%m-%d_%H:%M:%S_') + str(uuid4())[0:4]
