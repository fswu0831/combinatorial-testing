## Description

This code is an algorithm for creating a real-time OS test case.

Reachability testing derives test sequences automatically and on-the-fly, without constructing a static model.  And that algorithm implements t-way reachability testing.

## 変数の説明

### t_way
t-way法のtの数

### Q,Qs,Qr
シーケンスのテーブルQsが送信イベント、Qrが受信イベント
Q[0]が初期値


## 関数の説明
|関数|説明|
|:---|:---|
|`cstruct`|control-structureに入っているイベントをリスト形式で返す|
|`no_index`|第一引数から第二引数までイベントで、control-structureに含まれているものがあったらTrue|
|`construct_race_table`|レーステーブルの作成、t_way=1のときはペアワイズを適用しないアルゴリズム|
|`str_to_list`|データ加工用。pandasの要素にリストを入れるとstrとして認識されるので加工している|
|`creating_race_set`|シーケンスからrace_setを作成する|
|`expand_table`|ペアワイズを適用するための関数|


## References

- Lei Y, Carver RH. Reachability testing of concurrent programs. IEEE Transactions on Software Engineering 2006
- Lei Y, Carver RH, Kacker R, Kung D.A combinatorial testing strategy for concurrent programs. Published online 7 June 2007 in Wiley InterScience (www.interscience.wiley.com). DOI: 10.1002/stvr.369