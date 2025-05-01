# r: numpy
# venv: site-packages
# r: scipy

import numpy as np
from scipy.optimize import minimize
from scipy.optimize import Bounds

# 目的関数
def rosen(x):
    """The Rosenbrock function"""
    return sum(100.0*(x[1:]-x[:-1]**2.0)**2.0 + (1-x[:-1])**2.0)

# 目的関数の勾配
def rosen_der(x):
    xm = x[1:-1]
    xm_m1 = x[:-2]
    xm_p1 = x[2:]
    der = np.zeros_like(x)
    der[1:-1] = 200*(xm-xm_m1**2) - 400*(xm_p1 - xm**2)*xm - 2*(1-xm)
    der[0] = -400*x[0]*(x[1]-x[0]**2) - 2*(1-x[0])
    der[-1] = 200*(x[-1]-x[-2]**2)
    return der

# 制約
ineq_cons = {'type': 'ineq',
            'fun' : lambda x: 1 - x[0]**2 - x[1],
            'jac' : lambda x: np.array([-2*x[0], -1.0])}
# 境界条件
bounds = Bounds([0, -0.5], [1.0, 2.0])
x0 = np.array([0.5, 0])

if run:
    # ここで最適化させる
    opt = minimize(rosen, x0, method='SLSQP', jac=rosen_der,
                constraints=ineq_cons, options={'ftol': 1e-9, 'disp': True},
                bounds=bounds)
    print(opt)

    # 結果を出力
    a = opt.x.tolist()
