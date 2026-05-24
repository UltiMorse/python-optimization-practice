"""
The Looping Sudoku Problem Formulation for the PuLP Modeller

Authors: Antony Phillips, Dr Stuart Mitchell
edited by Dr Nathan Sudermann-Merx
"""

# PuLPモデラー関数をインポートする
from pulp import *

# 数独のすべての行、列、および値は1から9までの値を取る
VALS = ROWS = COLS = range(1, 10)

# 各箱の各マスの行と列のインデックスを含む boxes リストが作成される
Boxes = [
    [(3 * i + k + 1, 3 * j + l + 1) for k in range(3) for l in range(3)]
    for i in range(3)
    for j in range(3)
]

# 問題のデータを格納する prob 変数が作成される
prob = LpProblem("Sudoku Problem")

# 決定変数が作成される
choices = prob.add_variable_dict("Choice", (VALS, ROWS, COLS), 0, 1, LpBinary)

# 必要ないため目的関数は定義しない

# 各マスに1つの値しか入らないことを保証する制約を追加する
for r in ROWS:
    for c in COLS:
        prob += lpSum([choices[v, r, c] for v in VALS]) == 1

# 各値に対して行、列、および箱の制約が追加される
for v in VALS:
    for r in ROWS:
        prob += lpSum([choices[v, r, c] for c in COLS]) == 1

    for c in COLS:
        prob += lpSum([choices[v, r, c] for r in ROWS]) == 1

    for b in Boxes:
        prob += lpSum([choices[v, r, c] for (r, c) in b]) == 1

# 開始時の数字が制約として入力される
input_data = [
    (5, 1, 1),
    (6, 2, 1),
    (8, 4, 1),
    (4, 5, 1),
    (7, 6, 1),
    (3, 1, 2),
    (9, 3, 2),
    (6, 7, 2),
    (8, 3, 3),
    (1, 2, 4),
    (8, 5, 4),
    (4, 8, 4),
    (7, 1, 5),
    (9, 2, 5),
    (6, 4, 5),
    (2, 6, 5),
    (1, 8, 5),
    (8, 9, 5),
    (5, 2, 6),
    (3, 5, 6),
    (9, 8, 6),
    (2, 7, 7),
    (6, 3, 8),
    (8, 7, 8),
    (7, 9, 8),
    (3, 4, 9),
    # 前回の数独は一意の解しか持たないため、複数の解を持つ数独を
    # 得るためにボードからいくつかの数字を削除する
    #    (1, 5, 9),
    #    (6, 6, 9),
    #    (5, 8, 9)
]

for v, r, c in input_data:
    prob += choices[v, r, c] == 1

# 問題のデータが.lpファイルに書き出される
prob.writeLP("Sudoku.lp")

# 書き込み用の sudokuout.txt ファイルが作成/上書きされる
sudokuout = open("sudokuout.txt", "w")

while True:
    prob.solve()
    # 解のステータスが画面に出力される
    print("Status:", LpStatus[prob.status])
    # 制約を満たし、「最適」とみなされた場合、解が出力される
    if LpStatus[prob.status] == "Optimal":
        # 解が sudokuout.txt ファイルに書き込まれる
        for r in ROWS:
            if r in [1, 4, 7]:
                sudokuout.write("+-------+-------+-------+\n")
            for c in COLS:
                for v in VALS:
                    if value(choices[v, r, c]) == 1:
                        if c in [1, 4, 7]:
                            sudokuout.write("| ")
                        sudokuout.write(str(v) + " ")
                        if c == 9:
                            sudokuout.write("|\n")
        sudokuout.write("+-------+-------+-------+\n\n")
        # 同じ解が再び見つからないようにする制約を追加する
        prob += (
            lpSum(
                [
                    choices[v, r, c]
                    for v in VALS
                    for r in ROWS
                    for c in COLS
                    if value(choices[v, r, c]) == 1
                ]
            )
            <= 80
        )
    # 新しい最適解が見つからない場合、プログラムを終了する
    else:
        break
sudokuout.close()

# ユーザーに解の保存場所が提示される
print("Solutions Written to sudokuout.txt")
