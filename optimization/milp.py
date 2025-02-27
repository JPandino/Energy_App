import pandas as pd
import numpy as np
from pulp import *

def milp_optimization(dic_ext, data):

    steps = 24
    delta_t = 1
    dic = {"unit": ["A", "B"],
           "VIs": dic_ext["param_1"],
           "VIi": dic_ext["param_2"],
           "VFs": dic_ext["param_3"],
           "VFi": dic_ext["param_4"],
           "vsmax": dic_ext["param_5"],
           #"vsmin": dic_ext["param_6"],
           "vimax": dic_ext["param_7"],
           #"vimin": dic_ext["param_8"],
           #"qsmax": dic_ext["param_9"],
           #"qimax": dic_ext["param_10"],
           "pmax": {"A": dic_ext["param_11"], "B": dic_ext["param_11"]},
           #"pwmax": {"A": dic_ext["param_12"], "B": dic_ext["param_12"]},
           "pmin": {"A": dic_ext["param_13"], "B": dic_ext["param_13"]},
           #"pwmin": {"A": dic_ext["param_14"], "B": dic_ext["param_14"]},
           "e_p": {"A": dic_ext["param_15"], "B": dic_ext["param_15"]},
           "e_pw": {"A": dic_ext["param_16"], "B": dic_ext["param_16"]},
           "rp": dic_ext["param_17"],
           "M_acl": dic_ext["param_18"],
           "P_acl": dic_ext["param_19"],
           "k1": 8.0,
           "k2": 1000.0,
           "C": 0.0036
           }

    model = LpProblem("OptimizationProblem", LpMaximize)

    p = LpVariable.dicts("p", (dic["unit"], range(steps)), 0, None)
    pw = LpVariable.dicts("pw", (dic["unit"], range(steps)), 0, None)
    qs = LpVariable.dicts("qs", range(steps), 0, None)
    qi = LpVariable.dicts("qi", range(steps), 0, None)
    vs = LpVariable.dicts("vs", range(steps), 0, dic["vsmax"])
    vi = LpVariable.dicts("vi", range(steps), 0, dic["vimax"])
    profit = LpVariable.dicts("profit", range(steps), None, None)

    i_p = LpVariable.dicts("i_p", (dic["unit"], range(steps)), 0, 1, cat='Binary')
    i_pw = LpVariable.dicts("i_pw", (dic["unit"], range(steps)), 0, 1, cat='Binary')
    i_p_pw = LpVariable.dicts("i_p_pw", (dic["unit"], range(steps)), 0, 1, cat='Binary')
    i_pw_p = LpVariable.dicts("i_pw_p", (dic["unit"], range(steps)), 0, 1, cat='Binary')
    i_f = LpVariable.dicts("i_f", (dic["unit"], range(steps)), 0, 1, cat='Binary')
    i_os = LpVariable.dicts("i_os", (dic["unit"], range(steps)), 0, 1, cat='Binary')
    i_off = LpVariable.dicts("i_off", (dic["unit"], range(steps)), 0, 1, cat='Binary')
    i_st = LpVariable.dicts("i_st", (dic["unit"], range(steps)), 0, 1, cat='Binary')

    for u in dic["unit"]:
        for t in range(steps):
            model += p[u][t] >= dic["pmin"][u] * i_p[u][t]
            model += pw[u][t] >= dic["pmin"][u] * i_pw[u][t]

    for t in range(steps):
        if t == 0:
            model += vs[t] == dic["VIs"] + dic["C"] * (
                        data["upper_flow"][t] + sum([pw[u][t] for u in dic["unit"]]) - sum(
                    [p[u][t] for u in dic["unit"]]) - qs[t])
        else:
            model += vs[t] == vs[t - 1] + dic["C"] * (
                        data["upper_flow"][t] + sum([pw[u][t] for u in dic["unit"]]) - sum(
                    [p[u][t] for u in dic["unit"]]) - qs[t])

    for t in range(steps):
        if t == 0:
            model += vi[t] == dic["VIi"] + dic["C"] * (
                        data["lower_flow"][t] + sum([p[u][t] for u in dic["unit"]]) + qs[t] - sum(
                    [pw[u][t] for u in dic["unit"]]) - qi[t])
        else:
            model += vi[t] == vi[t - 1] + dic["C"] * (
                        data["lower_flow"][t] + sum([p[u][t] for u in dic["unit"]]) + qs[t] - sum(
                    [pw[u][t] for u in dic["unit"]]) - qi[t])

    model += vs[steps - 1] == dic["VFs"]
    model += vi[steps - 1] == dic["VFi"]

    for t in range(steps):
        model += profit[t] == data["pld"][t] * (
                    sum([p[u][t] * dic["e_p"][u] for u in dic["unit"]]) - dic["M_acl"]) * delta_t - data["pld"][t] * (
                     sum([pw[u][t] * dic["e_pw"][u] for u in dic["unit"]])) * delta_t - dic["k1"] * (
                             sum([p[u][t] * dic["e_p"][u] for u in dic["unit"]]) + sum(
                         [pw[u][t] * dic["e_pw"][u] for u in dic["unit"]])) * delta_t - dic["k2"] * sum(
            [i_st[u][t] for u in dic["unit"]]) - dic["k2"] * sum([i_off[u][t] for u in dic["unit"]])

    for u in dic["unit"]:
        for t in range(steps):
            model += -dic["pmax"][u] + dic["pmin"][u] <= pw[u][t] - i_pw[u][t] * dic["pmax"][u]
            model += pw[u][t] - i_pw[u][t] * dic["pmax"][u] <= 0
            model += -dic["pmax"][u] + dic["pmin"][u] <= p[u][t] - i_p[u][t] * dic["pmax"][u]
            model += p[u][t] - i_p[u][t] * dic["pmax"][u] <= 0

            model += i_p[u][t] + i_pw[u][t] <= 1
            model += i_p[u][t] + i_pw[u][t] == i_f[u][t]
            model += i_p_pw[u][t] + i_pw_p[u][t] + i_os[u][t] == i_st[u][t]

            if t == 0:
                model += p[u][t] - p[u][t + 1] <= dic["rp"] * dic["pmax"][u]
                model += p[u][t + 1] - p[u][t] <= dic["rp"] * dic["pmax"][u]
                model += pw[u][t] - pw[u][t + 1] <= dic["rp"] * dic["pmax"][u]
                model += pw[u][t + 1] - pw[u][t] <= dic["rp"] * dic["pmax"][u]

                model += i_f[u][t + 1] - i_f[u][t] == i_os[u][t + 1] - i_off[u][t + 1]
                model += i_pw[u][t] + i_p[u][t + 1] - i_pw_p[u][t + 1] <= 1
                model += i_p[u][t] + i_pw[u][t + 1] - i_p_pw[u][t + 1] <= 1

            else:
                model += p[u][t - 1] - p[u][t] <= dic["rp"] * dic["pmax"][u]
                model += p[u][t] - p[u][t - 1] <= dic["rp"] * dic["pmax"][u]
                model += pw[u][t - 1] - pw[u][t] <= dic["rp"] * dic["pmax"][u]
                model += pw[u][t] - pw[u][t - 1] <= dic["rp"] * dic["pmax"][u]

                model += i_f[u][t] - i_f[u][t - 1] == i_os[u][t] - i_off[u][t]
                model += i_pw[u][t - 1] + i_p[u][t] - i_pw_p[u][t] <= 1
                model += i_p[u][t - 1] + i_pw[u][t] - i_p_pw[u][t] <= 1

    model += sum([profit[t] for t in range(steps)])

    model.solve()
    #print("Status:", LpStatus[model.status])

    df_resultado = pd.DataFrame()

    if LpStatus[model.status] == 'Optimal':  # Tem água para ir de VI a VF

        result_optimization = {"Receita": value(model.objective)}

        p_value = [[p[u][t].varValue for u in dic["unit"]] for t in range(steps)]
        pw_value = [[pw[u][t].varValue for u in dic["unit"]] for t in range(steps)]
        vs_value = [round(vs[i].varValue, 2) for i in vs]
        qs_value = [round(qs[i].varValue, 2) for i in qs]
        vi_value = [round(vi[i].varValue, 2) for i in vi]
        qi_value = [round(qi[i].varValue, 2) for i in qi]
        i_p_value = [[i_p[u][t].varValue for u in dic["unit"]] for t in range(steps)]
        i_pw_value = [[i_pw[u][t].varValue for u in dic["unit"]] for t in range(steps)]
        i_f_value = [sum([i_f[u][t].varValue for u in dic["unit"]]) for t in range(steps)]
        i_p_pw_value = [[i_p_pw[u][t].varValue for u in dic["unit"]] for t in range(steps)]
        i_pw_p_value = [[i_pw_p[u][t].varValue for u in dic["unit"]] for t in range(steps)]
        i_os_value = [[i_os[u][t].varValue for u in dic["unit"]] for t in range(steps)]
        i_off_value = [[i_off[u][t].varValue for u in dic["unit"]] for t in range(steps)]

        df_resultado = pd.DataFrame(
            data=[p_value, pw_value, vs_value, qs_value, vi_value, qi_value, i_p_value, i_pw_value, i_f_value, i_p_pw_value, i_pw_p_value, i_os_value, i_off_value]).T
        df_resultado.columns = ["p", "pw", "vs", "qs", "vi", "qi", "i_p", "i_pw", "i_f", "i_p_pw", "i_pw_p", "i_os", "i_off"]

    else:

        result_optimization = {}

    return result_optimization, df_resultado