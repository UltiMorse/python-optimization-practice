# BEGIN file_docstring
"""
PuLPモデラーのための簡略化されたウィスカスモデルのPythonによる定式化

Authors: Antony Phillips, Dr Stuart Mitchell  2007
"""
# END file_docstring

# BEGIN import_pulp
# PuLPモデラー関数をインポート
from pulp import *

# END import_pulp

# BEGIN define_prob
# 問題データを格納する 'prob' 変数を作成
prob = LpProblem("The Whiskas Problem", LpMinimize)
# END define_prob

# BEGIN chicken_beef_vars
# Beef（牛肉）とChicken（鶏肉）の2つの変数を下限値0で作成
x1 = prob.add_variable("ChickenPercent", 0, None, LpInteger)
x2 = prob.add_variable("BeefPercent", 0, None, LpContinuous)
# END chicken_beef_vars

# BEGIN obj_func
# 目的関数を最初に 'prob' に追加する
prob += 0.013 * x1 + 0.008 * x2, "Total Cost of Ingredients per can"
# END obj_func

# BEGIN constraints
# 5つの制約条件を入力する
prob += x1 + x2 == 100, "PercentagesSum"
prob += 0.100 * x1 + 0.200 * x2 >= 8.0, "ProteinRequirement"
prob += 0.080 * x1 + 0.100 * x2 >= 6.0, "FatRequirement"
prob += 0.001 * x1 + 0.005 * x2 <= 2.0, "FibreRequirement"
prob += 0.002 * x1 + 0.005 * x2 <= 0.4, "SaltRequirement"
# END constraints

# BEGIN lp_file
# 問題データを .lp ファイルに書き出す
prob.writeLP("WhiskasModel.lp")
# END lp_file

# BEGIN prob_solve
# PuLPが選択したソルバーを使って問題を解く
prob.solve()
# END prob_solve

# BEGIN print_status
# 解のステータスを画面に出力する
print("Status:", LpStatus[prob.status])
# END print_status

# BEGIN print_var_value
# 解決された最適解をもつ各変数を出力する
for v in prob.variables():
    print(v.name, "=", v.varValue)
# END print_var_value

# BEGIN print_obj
# 最適化された目的関数の値を画面に出力する
print("Total Cost of Ingredients per can = ", value(prob.objective))
# END print_obj
