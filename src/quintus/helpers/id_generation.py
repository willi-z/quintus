import random


def generate_id(length: int = 8):
    number = "0123456789"
    alpha = "abcdefghijklmnopqrstuvwxyz".upper()
    letters = number + alpha
    return "".join(random.choice(letters) for i in range(length))
