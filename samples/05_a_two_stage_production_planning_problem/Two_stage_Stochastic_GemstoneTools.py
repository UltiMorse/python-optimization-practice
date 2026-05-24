r"""
Author: Louis Luangkesorn <lugerpitt@gmail.com> 2019
https://github.com/lluang

Title: Gemstone Optimization problem

Problem taken from Data, Models, and Decisions by Bertsimas and Freund, 4th Edition
DMD 7.2

## 2 stage problem

- **Scenarios:** $s \in S = (1, 2, 3, 4)$
- **Probability scenario occuring:** $p^s$
- **Cost of steel:** $c$
- **Total steel:** $cap_{steel}$
- **Total molding and assembly hours:** $cap_{molding}, cap_{assembly}^s$
- **Wrench and plier earnings by scenario:** $w^s, p^s$
- **Max demand wrenches and pliers:** $UB_w, UB_p$
- **Decision variables**
  - $(W_{t+1}^s, P_{t+1}^s)$
- **Objective**   $Max \sum_s (p^s * (w^s W_{t+1}^s + p^s P_{t+1}^s) - c$
- **Steel Constraint:** $1.5W_{t+1}^1 + P_{t+1}^1 - C \le 0$
- **Molding Constraint:** $W_{t+1}^1 + P_{t+1}^1 \le cap_{molding}$
- **Assembly Constraint:** $0.3 W_{t+1}^1 + 0.5 P_{t+1}^1  \le cap_{assembly}^s$
- **Demand Limit W:** $W \le UB_w$
- **Demand Limit P:** $P \le UB_p$
- **Nonnegativity:** $W, P \ge 0$
"""

import pulp

# パラメータ設定
products = ["wrenches", "pliers"]
price = [130, 100]
steel = [1.5, 1]
molding = [1, 1]
assembly = [0.3, 0.5]
capsteel = 27
capmolding = 21
LB = [0, 0]
capacity_ub = [15, 16]
steelprice = 58
scenarios = [0, 1, 2, 3]
pscenario = [0.25, 0.25, 0.25, 0.25]
wrenchearnings = [160, 160, 90, 90]
plierearnings = [100, 100, 100, 100]
capassembly = [8, 10, 8, 10]

production = [(j, i) for j in scenarios for i in products]
pricescenario = [[wrenchearnings[j], plierearnings[j]] for j in scenarios]
priceitems = [item for sublist in pricescenario for item in sublist]

# パラメータ用の辞書を作成する
price_dict = dict(zip(production, priceitems))
capacity_dict = dict(zip(products, capacity_ub * 4))
steel_dict = dict(zip(products, steel))
molding_dict = dict(zip(products, molding))
assembly_dict = dict(zip(products, assembly))

# 問題を定義するための 'gemstoneprob' 変数を作成する
gemstoneprob = pulp.LpProblem("The Gemstone Tool Problem", pulp.LpMaximize)

# 変数とパラメータを辞書として作成する
production_vars = gemstoneprob.add_variable_dict(
    "production", (scenarios, products), 0, None, pulp.LpContinuous
)
steelpurchase = gemstoneprob.add_variable("steelpurchase", 0, None, pulp.LpContinuous)

# 最初に目的関数を 'gemstoneprob' に追加する
gemstoneprob += (
    pulp.lpSum(
        [
            pscenario[j] * (price_dict[(j, i)] * production_vars[j, i])
            for (j, i) in production
        ]
        - steelpurchase * steelprice
    ),
    "Total cost",
)

for j in scenarios:
    gemstoneprob += pulp.lpSum(
        [steel_dict[i] * production_vars[j, i] for i in products]
    ) - steelpurchase <= 0, ("Steel capacity" + str(j))
    gemstoneprob += pulp.lpSum(
        [molding_dict[i] * production_vars[j, i] for i in products]
    ) <= capmolding, ("molding capacity" + str(j))
    gemstoneprob += pulp.lpSum(
        [assembly_dict[i] * production_vars[j, i] for i in products]
    ) <= capassembly[j], ("assembly capacity" + str(j))
    for i in products:
        gemstoneprob += production_vars[j, i] <= capacity_dict[i], (
            "capacity " + str(i) + str(j)
        )

# 問題の中身を出力する
print(gemstoneprob)

# 問題のデータを.lpファイルに書き出す
gemstoneprob.writeLP("gemstoneprob.lp")
# PuLPのデフォルトソルバーを用いて問題を解く
gemstoneprob.solve()
# 解のステータスを画面に出力する
print("Status:", pulp.LpStatus[gemstoneprob.status])

# 出力

# 各変数の最適化された値を出力する
for v in gemstoneprob.variables():
    print(v.name, "=", v.varValue)
result = [v.varValue for v in gemstoneprob.variables()]

# 最適化された目的関数の値をコンソールに出力する
print("Total price = ", pulp.value(gemstoneprob.objective))
