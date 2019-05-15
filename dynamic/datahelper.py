import pymysql
import json

ERROR_FLG = 'errorFlag'
ERROR_MSG = 'errorMessage'
SUCC_MSG = 'succMessage'

EM_1 = '评论不存在！'
EM_2 = 'sql语句失败!'
EM_3 = "数据库连接失败！"
EM_4 = '删除成功'
EM_5 = "商品不存在！"
EM_6 = "评价成功！"
EM_7 = "您已评价过！"
EM_8 = '获取数据成功'

DATA = 'data'


class DataHelper(object):
    def __init__(self):
        self.is_connect = False


    # 连接数据库
    def connect_mysql(self):
        self.conn = pymysql.connect(port=3306, user="root", password="12345678", host="localhost", database="shopping",
                                    charset="utf8")
        # 获取cursor
        self.cursor = self.conn.cursor()
        self.is_connect = True
        print("连接数据库成功")

    # 关闭数据库连接
    def close_connection(self):
        self.cursor.close()
        self.conn.close()

    # 删除评论
    def del_from_mysql(self, user_name,good_id):
        print("这里是data-helper------del_from_mysql")
        # 如果连接关闭，建立连接
        if not self.is_connect:
            self.connect_mysql()
        result = {
            ERROR_FLG: 1
        }
        if not self.is_this_user_exist(user_name, good_id):
            print("user not exist")
            result[ERROR_MSG] = EM_1
            return result
        para = [user_name, good_id]
        # 逻辑删除评论
        sql = """ update comments set is_delete=1 where users=%s and is_delete=0 and good_id=%s"""
        print("sql语句为： ",sql)
        try:
            count = self.cursor.execute(sql, para)
            print("找到符合标准的数据为（删除）： ",count)
        except:
            result[ERROR_MSG] = EM_2
        else:
            result[ERROR_FLG] = 0
            result[SUCC_MSG] = EM_4
        # 保存删除
        self.conn.commit()
        # 关闭连接
        self.close_connection()
        print(result,'datahelper')
        return result

    # 检查评论是否存在
    def is_this_user_exist(self, user_name, good_id):
        # 检查用户是否已经评论
        para = [user_name, good_id]
        sql = """ select users from comments where users=%s and is_delete=0 and good_id=%s"""
        print("-------------从mysql检查user是否已经评论-------------")
        print("sql语句为-----", sql)
        count = self.cursor.execute(sql, para)
        if count == 0:
            return False
        else:
            return True

    # 向mysql增加数据
    def add_to_mysql(self, user_name, stars, header, comment, good_id):
        # 检查字典格式是否正确
        print("--------------进入datahelper的add_to_mysql-------------")
        result = {
            ERROR_FLG: 0
        }
        # 如果连接关闭，建立连接
        if not self.is_connect:
            self.connect_mysql()

        # 如果用户从未评论
        if not self.is_this_user_exist(user_name, good_id):
            para=[user_name, stars, header, comment, good_id]
            # 要执行的sql语句
            sql = """ insert into comments (users, stars, header, comment, good_id) values (%s, %s, %s, %s, %s); """
            # 从mysql获取数据
            print("----------------向mysql增加数据---------------")
            print("sql语句为-----", sql)
            try:
                self.cursor.execute(sql, para)
            except:
                result[ERROR_FLG] = 1
                result[ERROR_MSG] = EM_5
            print("sql语句执行成功","*"*20)
            self.conn.commit()
            result[SUCC_MSG] = EM_6
        else:
            result[ERROR_FLG] = 1
            result[ERROR_MSG] = EM_7
        # 关闭连接
        self.close_connection()
        print(result,'datahelper')
        return result

    # 从mysql获得数据，加载到页面
    def retrieve_data_from_mysql(self):
        # 如果连接关闭，建立连接
        result = {
            ERROR_FLG: 1
        }
        try:
            if not self.is_connect:
                self.connect_mysql()
        except:
            result[ERROR_MSG] = EM_3
            return result
        # 连接数据库

        print("%" * 40)
        print("进入datahelper class---------retrieve_data_from_mysql")
        # 要直行的sql语句
        sql = """ select * from comments where is_delete=0 """
        print('要执行的sql语句 %s' % sql)
        # 从mysql获取数据
        try:
            self.cursor.execute(sql)
            info = self.cursor.fetchall()
        except:
            result[ERROR_MSG] = EM_2
        else:
            result[DATA] = info
            result[ERROR_FLG] = 0
            result[SUCC_MSG] = EM_8
        # 关闭连接
        self.close_connection()
        return result
