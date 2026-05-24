# 集合分割問題 (A Set Partitioning Problem)

集合分割問題 (set partitioning problem) は、ある集合 (S) に含まれる要素を、どのようにより小さな部分集合に分割できるかを決定する問題です。集合 S のすべての要素は、いずれか1つの部分集合にのみ含まれなければなりません。関連する問題には以下のものがあります：

- **集合パッキング (set packing)** - すべての要素は、0個または1個の部分集合に含まれなければならない。
- **集合被覆 (set covering)** - すべての要素は、少なくとも1個の部分集合に含まれなければならない。

このケーススタディでは、ウェディングプランナーが結婚式のゲストの座席の割り当てを決定する必要があります。この問題をモデル化するために、テーブルを部分集合としてモデル化し、結婚式に招待されたゲストを集合 S の要素としてモデル化します。ウェディングプランナーは、すべてのテーブルの合計の「幸福度 (happiness)」を最大化したいと考えています（ここではコードの実装に合わせて目的関数を `LpMinimize` としていますが、考え方としては最適な状態を探すものとなります）。

集合分割問題は、考えられるそれぞれの部分集合を明示的に列挙することでモデル化できます。（列挙（column generation）を用いないと）このアプローチは要素数が多い場合には計算が極めて困難になりますが、部分集合の目的関数の係数が非線形な式（例えば今回の「幸福度」など）であっても、線形計画法 (Linear Programming) を用いて問題を解くことができるという利点があります。

まず、`allcombinations()` を使用して、想定されるすべてのテーブル座席の組み合わせからなるリストを生成します。

```python
# 考えられるすべてのテーブル組み合わせのリストを作成する
possible_tables = [tuple(c) for c in pulp.allcombinations(guests, max_table_size)]
```

次に、そのテーブルが解に含まれる場合は 1、そうでない場合は 0 になるバイナリ変数（二値変数）を作成します。

```python
# テーブル設定が使用されることを示すバイナリ変数（二値変数）を作成する
_table_keys = ["_".join(t) for t in possible_tables]
vars_by_key = seating_model.add_variable_dict(
    "table_%s", (_table_keys,), 0, 1, pulp.LpInteger
)
x = {t: vars_by_key["_".join(t)] for t in possible_tables}
```

`LpProblem` を作成し、その後で目的関数を構築します。このスクリプトで使用される「幸福度」関数は、他の方法でモデル化しようとすると非常に困難になることに注意してください。

```python
seating_model = pulp.LpProblem("Wedding Seating Model", pulp.LpMinimize)

# BEGIN define_x
# テーブル設定が使用されることを示すバイナリ変数（二値変数）を作成する
_table_keys = ["_".join(t) for t in possible_tables]
vars_by_key = seating_model.add_variable_dict(
    "table_%s", (_table_keys,), 0, 1, pulp.LpInteger
)
x = {t: vars_by_key["_".join(t)] for t in possible_tables}
# END define_x

seating_model += pulp.lpSum([happiness(table) * x[table] for table in possible_tables])
```

解において許可されるテーブルの最大数を指定します。

```python
# テーブルの最大数を指定する
seating_model += (
    pulp.lpSum([x[table] for table in possible_tables]) <= max_tables,
    "Maximum_number_of_tables",
)
```

以下の制約条件セットは、ゲストが確実に1つのテーブルのみに割り当てられるように保証することによって、集合分割問題を定義します。

```python
# ゲストは必ず1つのテーブルにのみ配置されなければならない
for guest in guests:
    seating_model += (
        pulp.lpSum([x[table] for table in possible_tables if guest in table]) == 1,
        f"Must_seat_{guest}",
    )
```

完全なコードは `wedding.py` に記述されています。

```python
"""
ウェディングの座席配置問題の集合分割モデル

Authors: Stuart Mitchell 2009
"""

from typing import Tuple, Union

import pulp

max_tables = 5
max_table_size = 4
guests = "A B C D E F G I J K L M N O P Q R".split()


def happiness(
    table: Union[
        Tuple[str, str], Tuple[str, str, str, str], Tuple[str], Tuple[str, str, str]
    ],
) -> int:
    """
    テーブルの幸福度を求める
    - 文字間の最大距離を計算することによって求める
    """
    return abs(ord(table[0]) - ord(table[-1]))


# BEGIN possible_tables
# 考えられるすべてのテーブル組み合わせのリストを作成する
possible_tables = [tuple(c) for c in pulp.allcombinations(guests, max_table_size)]
# END possible_tables

# BEGIN class_and_obj_fn
seating_model = pulp.LpProblem("Wedding Seating Model", pulp.LpMinimize)

# BEGIN define_x
# テーブル設定が使用されることを示すバイナリ変数（二値変数）を作成する
_table_keys = ["_".join(t) for t in possible_tables]
vars_by_key = seating_model.add_variable_dict(
    "table_%s", (_table_keys,), 0, 1, pulp.LpInteger
)
x = {t: vars_by_key["_".join(t)] for t in possible_tables}
# END define_x

seating_model += pulp.lpSum([happiness(table) * x[table] for table in possible_tables])
# END class_and_obj_fn

# BEGIN total_table_constraint
# テーブルの最大数を指定する
seating_model += (
    pulp.lpSum([x[table] for table in possible_tables]) <= max_tables,
    "Maximum_number_of_tables",
)
# END total_table_constraint

# BEGIN exactly_one_table_constraint
# ゲストは必ず1つのテーブルにのみ配置されなければならない
for guest in guests:
    seating_model += (
        pulp.lpSum([x[table] for table in possible_tables if guest in table]) == 1,
        f"Must_seat_{guest}",
    )
# END exactly_one_table_constraint

seating_model.solve()

print(f"The chosen tables are out of a total of {len(possible_tables)}:")
for table in possible_tables:
    if x[table].value() == 1.0:
        print(table)
```
