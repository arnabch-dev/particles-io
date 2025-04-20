import random
import string
def get_random_object_id():
    SIZE = 6
    chars = string.ascii_uppercase + string.digits
    return "".join(random.choices(chars,k=SIZE))