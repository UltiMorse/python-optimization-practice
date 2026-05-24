# 2段階の生産計画問題 (A Two Stage Production Planning Problem)

生産計画問題において、意思決定者は利益を最大化するために最終製品を生産するべく、資材、労働力、その他の資源をどう調達するかを決定しなければなりません。

このケーススタディでは、ある企業 (GTC) がレンチとプライヤーを製造していますが、鉄鋼の調達可能性、機械の処理能力（成形と組み立て）、労働力、および市場の需要という制約を受けます。GTC は鉄鋼をどれだけ購入するかを決定したいと考えています。この問題を複雑にしているのは、利用可能な組み立て能力と製品当たりの収益貢献が現在のところ不明であるものの、次の期の初めには判明する予定であるという点です。

したがって、今回の期間において GTC は以下のことを行わなければなりません：
- **どれだけの鉄鋼を購入するかを決定する。**

次の期間の初めに、利用可能な組み立て能力と、レンチおよびプライヤー各1ユニット当たりの収益が判明したのち、GTC は以下を決定します：
- **レンチとプライヤーをそれぞれいくつ生産するか。**

不確実性は、それぞれ等しい確率をもつ 4 つの想定シナリオのいずれかとして表現されます。

最初に、PuLPパッケージをインポートします。

```python
import pulp
```

次に、データを読み込みます。ここではデータをベクトル（リスト）として読み込みます。実際の運用では、これらはデータベースから読み込まれることが多いでしょう。まず、シナリオによって変化しないデータ要素です。これらはそれぞれ2つの値を持ち、1つはレンチ用、もう1つはプライヤー用です。

```python
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
```

次のパラメータセットは、4つのシナリオに対応するものです。

```python
scenarios = [0, 1, 2, 3]
pscenario = [0.25, 0.25, 0.25, 0.25]
wrenchearnings = [160, 160, 90, 90]
plierearnings = [100, 100, 100, 100]
capassembly = [8, 10, 8, 10]
```

次に、製品とシナリオの組み合わせを表すリストを作成します。これらは後でパラメータ用の辞書を作成するために使用されます。

```python
production = [(j, i) for j in scenarios for i in products]
pricescenario = [[wrenchearnings[j], plierearnings[j]] for j in scenarios]
priceitems = [item for sublist in pricescenario for item in sublist]
```

そして、`dict(zip(…))` を使用してこれらのリストを辞書に変換します。これは、パラメータを意味のある名前で参照できるようにするためです。

```python
price_dict = dict(zip(production, priceitems))
capacity_dict = dict(zip(products, capacity_ub * 4))
steel_dict = dict(zip(products, steel))
molding_dict = dict(zip(products, molding))
assembly_dict = dict(zip(products, assembly))
```

決定変数を定義するために、インデックス値が関連付けられた変数の辞書を作成するメソッド `add_variable_dict()` を使用します。

```python
gemstoneprob = pulp.LpProblem("The Gemstone Tool Problem", pulp.LpMaximize)

# 変数とパラメータを辞書として作成する
production_vars = gemstoneprob.add_variable_dict(
    "production", (scenarios, products), 0, None, pulp.LpContinuous
)
```

`LpProblem` を作成し、次に目的関数を作成します。目標が「純収益を最大化すること」であるため、これが最大化問題 (maximization problem) であることに注意してください。

```python
steelpurchase = gemstoneprob.add_variable("steelpurchase", 0, None, pulp.LpContinuous)
```

目的関数は `pulp.lpSum()` 関数を使用して指定します。`+=` を使用して問題に追加されることに注意してください。

```python
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
```

その後、制約条件を追加します。ここでの制約は、シナリオと製品に基づいて構成されたセットであり、`for i in list:` の記法を使用して指定されます。各制約内で、合計（シグマ）はリスト内包表記を使用して表現されます。制約条件は、最後の論理比較演算子（通常は `<=` または `>=` ですが、`==` になることもあります）と、制約が適用される特定のシナリオや製品を区別するための「名前」が末尾に付けられることによって、目的関数とは区別されることに注意してください。

```python
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
```

完全なコードは `Two_stage_Stochastic_GemstoneTools.py` に記述されています。

```python
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

# 問題のデータを .lp ファイルに書き出す
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
```
