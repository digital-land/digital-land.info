import random


def skewed_random_triangular(N, target=5):
    return round(random.triangular(0, N, target))
