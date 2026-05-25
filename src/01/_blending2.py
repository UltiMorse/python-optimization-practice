'''
PuLPによるキャットフード混合の最適化。全問題の解法

Authors: Naoto Yamazaki 2026
'''


from pulp import *

Ingredients =["鶏肉", "牛肉", "マトン", "米", "麦", "ゲル"]

costs = {
    "鶏肉": 0.013,
    "牛肉": 0.008,
    "マトン": 0.010,
    "米": 0.002,
    "麦": 0.005,
    "ゲル": 0.001,
}

proteinPercent = {
    "鶏肉": 0.100,
    "牛肉": 0.200,
    "マトン": 0.150,
    "米": 0.000,
    "麦": 0.040,
    "ゲル": 0.000,
}

fatPercent = {
    "鶏肉": 0.080,
    "牛肉": 0.100,
    "マトン": 0.110,
    "米": 0.010,
    "麦": 0.010,
    "ゲル": 0.000,
}

fibrePercent = {
    "鶏肉": 0.001,
    "牛肉": 0.005,
    "マトン": 0.003,
    "米": 0.100,
    "麦": 0.150,
    "ゲル": 0.000,
}

saltPercent = {
    "鶏肉": 0.002,
    "牛肉": 0.005,
    "マトン": 0.007,
    "米": 0.002,
    "麦": 0.008,
    "ゲル": 0.000,
}

prob = LpProblem("猫缶問題にゃ", LpMinimize)

Ingredients_vars = prob.add_variable_dict("材料", (Ingredients,), 0, None, LpContinuous)

# 目的関数
prob += (
    lpSum([costs[i] * Ingredients_vars[i] for i in Ingredients]),
    "1缶あたりの材料の総コスト"
)

# 制約(括弧の有無は改行の有無による。)
prob += lpSum([Ingredients_vars[i] for i in Ingredients]) == 100, "合計100%"

prob += (
    lpSum([proteinPercent[i] * Ingredients_vars[i] for i in Ingredients]) >= 8.0, 
    "タンパク質の必要量"
)

prob += (
    lpSum([fatPercent[i] * Ingredients_vars[i] for i in Ingredients]) >= 6.0, 
    "脂肪の必要量"
)

prob += (
    lpSum([fibrePercent[i] * Ingredients_vars[i] for i in Ingredients]) <= 2.0, 
    "食物繊維の必要量"
)

prob += (
    lpSum([saltPercent[i] * Ingredients_vars[i] for i in Ingredients]) <= 0.4, 
    "食塩の必要量"
)

prob.writeLP("WhiskasModel2.lp")

prob.solve()

print("Status:", LpStatus[prob.status])

for v in prob.variables():
    print(v.name, "=", v.varValue)

print("1缶あたりの材料の総コスト = ", value(prob.objective))
