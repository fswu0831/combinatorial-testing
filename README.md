## Description

This code is an algorithm for creating a real-time OS test case.

Reachability testing derives test sequences automatically and on-the-fly, without constructing a static model.  And that algorithm implements t-way reachability testing.

## 変数の説明

### 全体の流れ
tway法のtとSYN-sequenceのCSVファイルをインポートすることで、race_setとテストケースを作成します。

### t_way
t-way法のtの数。1の場合ペアワイズ法を適用しないアルゴリズムが発火

### Q,Qs,Qr
シーケンスのテーブルQsが送信イベント、Qrが受信イベント。
QはQrとQsを縦方向に結合したもの。
Q[0]が初期値のSYN-sequence

||event|task|index|


## 関数の説明
|関数|説明|
|:---|:---|
|`cstruct`|control-structureに入っているイベントをリスト形式で返す|
|`no_index`|第一引数から第二引数までイベントで、control-structureに含まれているものがあったらTrue|
|`construct_race_table`|レーステーブルの作成、t_way=1のときはペアワイズを適用しないアルゴリズム|
|`str_to_list`|データ加工用。pandasの要素にリストを入れるとstrとして認識されるので加工している|
|`creating_race_set`|シーケンスからrace_setを作成する|
|`expand_table`|ペアワイズを適用するための関数|

### race_set作成のアルゴリズム
条件
1. rと同じタスクで起こっている
2. rのcontrol-structureにはいっていない
2. 対象のイベントより前に起こっている
上記を満たすrイベントのペアをrのracesetとする


## References

- Lei Y, Carver RH. Reachability testing of concurrent programs. IEEE Transactions on Software Engineering 2006
- Lei Y, Carver RH, Kacker R, Kung D.A combinatorial testing strategy for concurrent programs. Published online 7 June 2007 in Wiley InterScience (www.interscience.wiley.com). DOI: 10.1002/stvr.369
