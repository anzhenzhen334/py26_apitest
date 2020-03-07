"""
============================
Author:ann
Date:2020/2/24
Time:21:26
E-mail:326329411@qq.com
Mobile:15821865916
============================
"""
import pymysql
from common.handlerconfig import conf

"""
封装需求：查询
"""


class DB(object):
    def __init__(self):
        self.conn = pymysql.connect(host=conf.get('db', 'host'),
                                    port=conf.getint('db', 'port'),
                                    user=conf.get('db', 'user'),
                                    password=conf.get('db', 'pwd'),
                                    cursorclass=pymysql.cursors.DictCursor,
                                    charset='utf8')
        self.cur = self.conn.cursor()

    def find_one(self, sql):
        self.conn.commit()
        # 获取查询出来的第一条数据
        self.cur.execute(sql)
        data = self.cur.fetchone()
        return data
    #     先创建游标 再关闭游标  获取到的都是新数据 也可以 是另外一种实现方式

    def find_all(self, sql):
        self.conn.commit()
        # mysql事务隔离 需要提交下事务
        # 获取查询出来的所有数据
        self.cur.execute(sql)
        data = self.cur.fetchall()
        return data
    def find_count(self,sql):
        self.conn.commit()
        res = self.cur.execute(sql)
        return res
    # 返回结果条数


    def close(self):
        # 关闭游标，断开连接
        self.cur.close()
        self.conn.close()

#
# db = DB()
# sql = 'select * from futureloan.member limit 1'
# res = db.find_one(sql)
# print(res,type(res))
# print(res['id'])

# ['leave_amount']
