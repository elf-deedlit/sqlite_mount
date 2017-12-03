# sqlite_mount
sqliteをmountする

## 使い方
$~ sqlite_mount.py <mount_point> <mount_file>

## 機能
* テーブルをフォルダ名、プライマリキーをファイル名として表示する
* ファイルの中身を表示すると、そのプライマリキーの中身を表示する

## 注意
* 対応はPython3のみ
* pip install fusepy が必要
* エラー処理は全然やっていない
* 現在の機能は表示だけ

## TODO
* Python2.7には対応しないと
* Python2.6への対応はlru_cacheとかargparseとかのインストールが必要

