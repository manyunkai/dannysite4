# -*-coding:utf-8 -*-
"""
Created on 2014-4-5

@author: Danny<manyunkai@hotmail.com>
DannyWork Project.
"""

import sys

if sys.version_info[0] == 3:
    import pymysql
    pymysql.install_as_MySQLdb()
