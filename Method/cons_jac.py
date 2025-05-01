import numpy as np

def jac(x):
    """Constraint Jacobian function"""
    return [-2*x[0], -1.0]

a = jac([x0, x1])
