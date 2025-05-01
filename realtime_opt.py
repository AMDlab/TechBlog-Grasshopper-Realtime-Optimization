# r: numpy
# venv: site-packages
# r: scipy
import scriptcontext as sc

from Grasshopper.Kernel.Special import GH_NumberSlider
from System.Threading.Tasks import Task
from System import Decimal

import numpy as np
from scipy.optimize import minimize
from scipy.optimize import Bounds

import time
from ghpythonlib.treehelpers import list_to_tree

main_key = "optimization"
status_key = "status"
objective_key = "objective"
obj_der_key = "obj_der"
cons_key = "cons"
cjac_key = "cjac"
params_key = "params"
sliders_key = "sliders"
result_key = "result"
step_key = "step"
history_key = "history"


def run_process(x):
    """
    ここでGrasshopperへ処理を流す
    """
    # 変数が現在のものと一致するか
    for idx in range(len(x)):
        if sc.sticky[main_key][params_key][idx] != x[idx]:
            break
    else:
        # 一致する場合、終了する
        sc.sticky[main_key][status_key] = "processed"
        return
    # 一致しなかったとき処理を流す
    sc.sticky[main_key][status_key] = "processing"
    x_list = x.tolist()
    for idx in range(len(x)):
        sc.sticky[main_key][sliders_key][idx].SetSliderValue(Decimal(x_list[idx]))
    for idx in range(len(x)):
        sc.sticky[main_key][sliders_key][idx].ExpireSolution(True)

    # ここで結果を待つ
    for i in range(999):
        time.sleep(0.1)
        if sc.sticky[main_key][status_key] == "processed":
            break
    else:
        # 待てなかったらエラーとして出す
        sc.sticky[main_key][status_key] = "processed"
        raise Exception("loop end")
    sc.sticky[main_key][params_key] = np.array(x)


def func(x):
    run_process(x)
    obj = sc.sticky[main_key][objective_key]
    sc.sticky[main_key][step_key] += 1
    sc.sticky[main_key][history_key][0].append(obj)
    sc.sticky[main_key][history_key][1].append(x.tolist())
    return obj


def obj_der_func(x):
    run_process(x)
    sc.sticky[main_key][history_key][2].append(x)
    return sc.sticky[main_key][obj_der_key]


def cons_func(x):
    run_process(x)
    sc.sticky[main_key][history_key][3].append(sc.sticky[main_key][cons_key])
    return sc.sticky[main_key][cons_key]


def cjac_func(x):
    run_process(x)
    sc.sticky[main_key][history_key][4].append(x)
    return sc.sticky[main_key][cjac_key]


def optimization():
    """
    この関数を別タスクで開いて最適化を動かす。
    """
    # 制約
    ineq_cons = {'type': 'ineq',
                'fun' : lambda x: cons_func(x),
                'jac' : lambda x: cjac_func(x)}

    # 境界条件
    bounds = Bounds([0, -0.5], [1.0, 2.0])
    x0 = np.array([0.5, 0])
    # すぐに回し始めるとエラーになるため、遅延を挟む
    time.sleep(0.01)
    sc.sticky[main_key][result_key] = minimize(func, x0, method='SLSQP', jac=obj_der_func,
                constraints=[ineq_cons], options={'ftol': 1e-6, 'disp': True},
                bounds=bounds)
    sc.sticky[main_key][status_key] = "complete"
    time.sleep(0.01)
    ghenv.Component.ExpireSolution(True)


# 初回とResetが押されたときにリセット
if not main_key in sc.sticky.keys() or reset:
    if not run:
        sc.sticky[main_key] = {}
        sc.sticky[main_key][step_key] = 0 # ステップ数
        # 解析の状態を表す。
        # stop: 待機
        # processing: GHへ投げて結果待ち
        # processed: 結果がsc.sticky[main_key][objective_key]に反映された状態
        # complete: 解析完了
        sc.sticky[main_key][status_key] = "stop"
        sc.sticky[main_key][objective_key] = 0.
        sc.sticky[main_key][obj_der_key] = np.zeros(2)
        sc.sticky[main_key][cons_key] = 0.
        sc.sticky[main_key][cjac_key] = np.zeros(2)
        sc.sticky[main_key][params_key] = np.zeros(2)
        sc.sticky[main_key][sliders_key] = [slider
            for slider in ghenv.Component.Params.Input[1].Sources
            if isinstance(slider, GH_NumberSlider)] # 変更するNumberSliderを格納
        sc.sticky[main_key][result_key] = None # 結果を格納する
        sc.sticky[main_key][history_key] = [[], [], [], [], []]
    else:
        print("turn off run.") # runがTrueの時はリセットされない


if run:
    # processingの場合、数値を渡し、processedにする
    if sc.sticky[main_key][status_key] == "processing":
        time.sleep(0.01)
        sc.sticky[main_key][objective_key] = obj
        sc.sticky[main_key][obj_der_key] = np.array(obj_der)
        sc.sticky[main_key][cons_key] = cons
        sc.sticky[main_key][cjac_key] = np.array(cons_jac)
        sc.sticky[main_key][status_key] = "processed"

    # 実行されたとき解析を回す。
    if sc.sticky[main_key][status_key] == "stop":
        sc.sticky[main_key][step_key] = 0
        # ここで別タスクとして起動
        Task.Factory.StartNew(optimization)

    # 解析完了時に結果を返す
    if sc.sticky[main_key][status_key] == "complete":
        print(sc.sticky[main_key][status_key])
        print(sc.sticky[main_key][result_key])
    
print(sc.sticky[main_key][status_key])
print(sc.sticky[main_key][step_key])

h_obj = sc.sticky[main_key][history_key][0]
h_x = list_to_tree(sc.sticky[main_key][history_key][1])
