# BEGIN docstring_imports
"""
PuLPモデラーのための完全なウィスカスモデルのPythonによる定式化

Authors: Antony Phillips, Dr Stuart Mitchell  2007
"""

# PuLPモデラー関数をインポート
from pulp import *

# END docstring_imports

# BEGIN problem_data
# 原材料のリストを作成
Ingredients = ["CHICKEN", "BEEF", "MUTTON", "RICE", "WHEAT", "GEL"]

# 各原材料のコストの辞書を作成
costs = {
    "CHICKEN": 0.013,
    "BEEF": 0.008,
    "MUTTON": 0.010,
    "RICE": 0.002,
    "WHEAT": 0.005,
    "GEL": 0.001,
}

# 各原材料のタンパク質含有率（%）の辞書を作成
proteinPercent = {
    "CHICKEN": 0.100,
    "BEEF": 0.200,
    "MUTTON": 0.150,
    "RICE": 0.000,
    "WHEAT": 0.040,
    "GEL": 0.000,
}

# 各原材料の脂肪分含有率（%）の辞書を作成
fatPercent = {
    "CHICKEN": 0.080,
    "BEEF": 0.100,
    "MUTTON": 0.110,
    "RICE": 0.010,
    "WHEAT": 0.010,
    "GEL": 0.000,
}

# 各原材料の繊維質含有率（%）の辞書を作成
fibrePercent = {
    "CHICKEN": 0.001,
    "BEEF": 0.005,
    "MUTTON": 0.003,
    "RICE": 0.100,
    "WHEAT": 0.150,
    "GEL": 0.000,
}

# 各原材料の塩分含有率（%）の辞書を作成
saltPercent = {
    "CHICKEN": 0.002,
    "BEEF": 0.005,
    "MUTTON": 0.007,
    "RICE": 0.002,
    "WHEAT": 0.008,
    "GEL": 0.000,
}
# END problem_data

# BEGIN define_prob
# 問題データを格納する 'prob' 変数を作成
prob = LpProblem("The Whiskas Problem", LpMinimize)
# END define_prob

# BEGIN ingredient_vars
# 参照される変数を格納するための 'ingredient_vars' という辞書を作成
ingredient_vars = prob.add_variable_dict("Ingr", (Ingredients,), 0, None, LpContinuous)
# END ingredient_vars

# BEGIN obj_function
# 目的関数を最初に 'prob' に追加する
prob += (
    lpSum([costs[i] * ingredient_vars[i] for i in Ingredients]),
    "Total Cost of Ingredients per can",
)
# END obj_function

# BEGIN constraints
# 5つの制約条件を 'prob' に追加する
prob += lpSum([ingredient_vars[i] for i in Ingredients]) == 100, "PercentagesSum"
prob += (
    lpSum([proteinPercent[i] * ingredient_vars[i] for i in Ingredients]) >= 8.0,
    "ProteinRequirement",
)
prob += (
    lpSum([fatPercent[i] * ingredient_vars[i] for i in Ingredients]) >= 6.0,
    "FatRequirement",
)
prob += (
    lpSum([fibrePercent[i] * ingredient_vars[i] for i in Ingredients]) <= 2.0,
    "FibreRequirement",
)
prob += (
    lpSum([saltPercent[i] * ingredient_vars[i] for i in Ingredients]) <= 0.4,
    "SaltRequirement",
)
# END constraints

# 問題データを .lp ファイルに書き出す
prob.writeLP("WhiskasModel2.lp")

# PuLPが選択したソルバーを使って問題を解く
prob.solve()

# 解のステータスを画面に出力する
print("Status:", LpStatus[prob.status])

# 解決された最適解をもつ各変数を出力する
for v in prob.variables():
    print(v.name, "=", v.varValue)

# 最適化された目的関数の値を画面に出力する
print("Total Cost of Ingredients per can = ", value(prob.objective))
