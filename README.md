# sqlite_mount
sqliteをmountする

## 使い方
$~ sqlite_mount.py <mount_point> <mount_file>

### Python3.x
$ pip install fusepy

### Python2.7
$ pip install fusepy backports.functools_lru_cache

### Python2.6
$ yum install fuse-libs
$ pip install argparse fusepy backports.functools_lru_cache

## 機能
* テーブルをフォルダ名、プライマリキーをファイル名として表示する
* ファイルの中身を表示すると、そのプライマリキーの中身を表示する

## 注意
* エラー処理は全然やっていない
* 現在の機能は表示だけ

## TODO
* 書き込み機能も作る？

