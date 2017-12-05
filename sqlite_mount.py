#!/usr/bin/env python
# vim: set fileencoding=utf-8:
import argparse
import errno
import fuse
import functools
import os
import sys
import sqlite3
import stat
import time

#
# sqlite3 のファイルを fuse でマウントしてみる
#

#sqlite> pragma table_info('users');
#       cid = 0
#      name = uid
#      type = INTEGER
#   notnull = 0
#dflt_value =
#        pk = 1

class DBMount(fuse.LoggingMixIn, fuse.Operations):
    '''sqlite3 をマウントする'''
    def __init__(self, filename):
        self.filename = filename
        self.table = None
        self.stat = os.stat(filename)
        self._make_table_info()

    def _make_table_info(self):
        '''テーブルの一覧を作成する'''
        self.table_info = {}
        info = []
        with sqlite3.connect(self.filename) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' and name!='sqlite_sequence'")
            for v in cur.fetchall():
                info.append(v['name'])
            for name in info:
                cur.execute('PRAGMA table_info(`{0}`)'.format(name))
                pkname = None
                for v in cur.fetchall():
                    if pkname is None:
                        # primary key がないときは最初をキーとみなす
                        pkname = v['name']
                    if v['pk'] == 1:
                        pkname = v['name']
                        break
                self.table_info[name] = pkname

#    def destroy(self, path):
#        pass

    def readdir(self, path, fh):
        rslt = ['.', '..']
        if path == "/":
            rslt += self.table_info.keys()
        else:
            name = path[1:]
            if name not in self.table_info:
                raise fuse.FuseOSError(errno.ENOENT)
            pkname = self.table_info[name]
            with sqlite3.connect(self.filename) as conn:
                cur = conn.cursor()
                cur.execute('SELECT {0} FROM `{1}`'.format(pkname, name))
                for v in cur.fetchall():
                    rslt.append(str(v[0]))

        return rslt

    @functools.lru_cache(maxsize = 256)
    def _get_row_info(self, path):
        ss = path.split('/')
        # /table/pk -> ['',table,pk]
        table = ss[1]
        pk = ss[2]
        if table not in self.table_info:
            return None
        pkname = self.table_info[table]
        with sqlite3.connect(self.filename) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            sql = 'SELECT * FROM {0} WHERE {1}=?'.format(table, pkname)
            params = (pk, )
            cur.execute(sql, params)
            v = cur.fetchone()
            if v is None:
                return None
            rslt = []
            for k in v.keys():
                vv = v[k]
                rslt.append('{0}={1}'.format(k, vv))
            t = '\n'.join(rslt)
            t += '\n'
            return t.encode('utf-8')

    def getattr(self, path, fh = None):
        # パス区切り文字の数でテーブル名か中身か判断する
        if path.count('/') == 1:
            # テーブルっぽい
            t = dict((key, getattr(self.stat, key)) for key in ('st_atime',
                    'st_gid', 'st_mtime', 'st_uid', 'st_ctime'))
            t['st_nlink'] = 2
            t['st_mode'] = stat.S_IFDIR | 0o755
            return t
        else:
            rslt = self._get_row_info(path)
            if rslt is None:
                raise fuse.FuseOSError(errno.ENOENT)
            t = dict((key, getattr(self.stat, key)) for key in ('st_atime',
                    'st_gid', 'st_mtime', 'st_uid', 'st_ctime'))
            t['st_nlink'] = 1
            t['st_mode'] = stat.S_IFREG | 0o644
            t['st_size'] = len(rslt)
            return t

    def read(self, path, size, offset, fh):
        # 中身表示
        rslt = self._get_row_info(path)
        if rslt is None:
            raise fuse.FuseOSError(errno.ENOENT)
        return rslt[offset:offset + size]

def option_parse():
    parser = argparse.ArgumentParser(description='mount sqlite file')
    parser.add_argument('mountpoint', type=str, help='mount point')
    parser.add_argument('filename', type=str, help='sqlite3 filename')
    return parser.parse_args()

def main():
    args = option_parse()
    _fuse = fuse.FUSE(DBMount(args.filename), args.mountpoint, foreground = True)

if __name__ == '__main__':
    main()
