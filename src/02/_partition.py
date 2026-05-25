"""
結婚式の座席配置の集合分割モデル

Authors: Naoto Yamazaki 2026
"""


from typing import Tuple, Union

import pulp

max_tables = 5
max_table_size = 4
guests = "A B C D E F G I J K L M N O P Q R".split()

def happiness(
        table: Union[
            Tuple[str,str], Tuple[str, str, str, str], Tuple[str], Tuple[str, str, str]
            ],
        ) -> int:
        return abs(ord(table[0]) - ord(table[-1]))

# 考えられるすべてのテーブルの組み合わせのリストを作成する。
possible_tables = [tuple(c) for c in pulp.allcombinations(guests, max_table_size)]

seating_model = pulp.LpProblem("結婚式の座席モデル", pulp.LpMinimize)

# そのテーブル設定が解に含まれる場合は1、そうでない場合は0になるbool変数
_table_keys = ["_".join(t) for t in possible_tables]
vars_by_key = seating_model.add_variable_dict(
    "table_%s", (_table_keys,), 0, 1, pulp.LpInteger
)
x = {t: vars_by_key["_".join(t)] for t in possible_tables}

seating_model += pulp.lpSum([happiness(table) * x[table] for table in possible_tables])


seating_model += (
    pulp.lpSum([x[table] for table in possible_tables]) <= max_tables,
    "テーブルの最大数"
)

# ゲストは一つのテーブルのみに配置される。
for guest in guests:
    seating_model += (
        pulp.lpSum([x[table] for table in possible_tables if guest in table]) == 1,
        f"Must_seat_{guest}",
    )

seating_model.solve()

print(f"The chosen tables are out of a total of {len(possible_tables)}:")
for table in possible_tables:
      if x[table].value() == 1.0:
            print(table)
