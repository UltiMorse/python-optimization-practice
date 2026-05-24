'''
PuLPによるキャットフード混合の最適化

Authors: Naoto Yamazaki 2026
'''

from pulp import *

prob = LpProblem("猫缶問題にゃ", LpMinimize) # 名前と、最小化問題か最大化問題かを指定する。

# 変数の追加 下限と上限を指定。LpContinuousかLpIntegerかLpBinaryを第4引数に
x1 = prob.add_variable("鶏肉の割合", 0, None, LpContinuous) 
x2 = prob.add_variable("牛肉の割合", 0, None, LpContinuous)

# 目的関数を追加
prob += 0.013 * x1 + 0.008 * x2, "1缶あたりの材料の総コスト"
# 1g当たりのコストから。

# 制約
prob += x1 + x2 == 100, "合計100%"
prob += 0.100 * x1 + 0.200 * x2 >= 8.0, "タンパク質の必要量"
prob += 0.080 * x1 + 0.100 * x2 >= 6.0, "脂肪の必要量"
prob += 0.001 * x1 + 0.005 * x2 <= 2.0, "食物繊維の必要量"
prob += 0.002 * x1 + 0.005 * x2 <= 0.4, "塩分の必要量"

prob.writeLP("WhiskasModel.lp") # .Lpファイルに書き出す

prob.solve()

print("Status:", LpStatus[prob.status]) # prob.statusは状態コードを表す属性。LpStatusで文字列に変換する。

for v in prob.variables():
    print(v.name, "=", v.varValue)

print("1缶あたりの材料の総コスト = ", value(prob.objective))
