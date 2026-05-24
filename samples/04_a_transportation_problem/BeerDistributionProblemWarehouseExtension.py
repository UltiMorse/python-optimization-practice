"""
The Beer Distribution Problem for the PuLP Modeller with Extension for a Warehouse
"""

# PuLPモデラー関数をインポートする
from pulp import *

# すべての供給ノードのリストを作成する
Warehouses = ["A", "B"]

# 各供給ノードの供給ユニット数の辞書を作成する
supply = {"A": 1000, "B": 4000}

# すべての需要ノードのリストを作成する
Bars = ["1", "2", "3", "4", "5", "D"]

# 各需要ノードの需要ユニット数の辞書を作成する
demand = {"1": 500, "2": 900, "3": 1800, "4": 200, "5": 700, "D": 900}

# 各輸送経路のコストのリストを作成する
costs = [  # Bars
    # 1 2 3 4 5 D
    [2, 4, 5, 2, 1, 0],  # A   Warehouses
    [3, 1, 3, 2, 3, 0],  # B
]

# コストデータを辞書にする
costs_dict = makeDict([Warehouses, Bars], costs, 0)

# 問題のデータを格納する 'prob' 変数を作成する
prob = LpProblem("Beer Distribution Problem", LpMinimize)

# 輸送のすべての可能なルートを含むタプルのリストを作成する
Routes = [(w, b) for w in Warehouses for b in Bars]

# 参照される変数（ルート）を含む 'Vars' という辞書を作成する
vars = prob.add_variable_dict("Route", (Warehouses, Bars), 0, None, LpInteger)

# 最初に目的関数を 'prob' に追加する
prob += (
    lpSum([vars[w, b] * costs_dict[w][b] for (w, b) in Routes]),
    "Sum_of_Transporting_Costs",
)

# 各供給ノード（倉庫）について、供給上限制約を prob に追加する
for w in Warehouses:
    prob += (
        lpSum([vars[w, b] for b in Bars]) <= supply[w],
        f"Sum_of_Products_out_of_Warehouse_{w}",
    )

# 各需要ノード（バー）について、需要下限制約を prob に追加する
for b in Bars:
    prob += (
        lpSum([vars[w, b] for w in Warehouses]) >= demand[b],
        f"Sum_of_Products_into_Bar{b}",
    )

# 問題のデータを.lpファイルに書き出す
prob.writeLP("BeerDistributionProblem.lp")

# PuLPのデフォルトソルバーを用いて問題を解く
prob.solve()

# 解のステータスを画面に出力する
print("Status:", LpStatus[prob.status])

# 各変数の最適化された値を出力する
for v in prob.variables():
    print(v.name, "=", v.varValue)

# 最適化された目的関数の値を画面に出力する
print("Total Cost of Transportation = ", value(prob.objective))
