from sqlalchemy import inspect
import random
import string


def object_as_dict(obj):
    return {c.key: getattr(obj, c.key) for c in inspect(obj).mapper.column_attrs}


def generate_serial_number(length=20):
    alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ" + '23456789'*3
    chars = [random.choice(alphabet) for _ in range(length)]
    return ''.join(chars)
