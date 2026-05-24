"""
A set partitioning model of a wedding seating problem

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
    - 文字間の最大距離を計算することによって
    """
    return abs(ord(table[0]) - ord(table[-1]))


# BEGIN possible_tables
# すべての可能なテーブルのリストを作成する
possible_tables = [tuple(c) for c in pulp.allcombinations(guests, max_table_size)]
# END possible_tables

# BEGIN class_and_obj_fn
seating_model = pulp.LpProblem("Wedding Seating Model", pulp.LpMinimize)

# BEGIN define_x
# テーブル設定が使用されるかを示すバイナリ変数を作成する
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
# ゲストは1つのテーブルにのみ着席しなければならない
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
