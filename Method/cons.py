import numpy as np

def cons(x):
    """Constraint function"""
    return 1 - x[0]**2 - x[1]

a = cons([x0, x1])
