import re
import json
import datahelper

# 报错信息
ERROR_MSG = 'errorMessage'
ERROR_FLG = 'errorFlag'
SUCC_MSG = 'succMessage'
ERROR_MSG_1 = "输入数据有误！"
DATA = 'data'
g_dict = dict()


def route(url_r):
    def set_func(func):
        # 对所有方法添加字典
        g_dict[url_r] = func

        def call_func():
            func()
        return call_func
    return set_func


@route(r"/index_page")
def index_page(url_data=None):
    result = {
        ERROR_FLG: 0,
    }
    print("这里是web.py---------------index_page------------")
    info_helper = datahelper.DataHelper()
    info_dict = info_helper.retrieve_data_from_mysql()
    # 建立返回字典
    print('从数据库获得的数据为-----', info_dict[DATA])
    json_data = []
    # 录入数据
    if info_dict[ERROR_FLG] == 0:
        if info_dict[DATA]:
            for temp in info_dict[DATA]:
                i_dict = dict()
                try:
                    i_dict["user"] = temp[4]
                    i_dict["stars"] = temp[1]
                    i_dict["header"] = temp[2]
                    i_dict["comment"] = temp[5]
                    i_dict["good_id"] = temp[6]
                except:
                    result[ERROR_FLG] = 1
                    result[ERROR_MSG] = ERROR_MSG_1
                else:
                    json_data.append(i_dict)
            result[DATA] = json.dumps(json_data)
    else:
        result[ERROR_FLG] = 1
        result[ERROR_MSG] = info_dict[ERROR_MSG]
    result[SUCC_MSG] = info_dict[SUCC_MSG]
    result = json.dumps(result)
    print('返回jason数据结果为：%s' % result)
    return result


@route(r"/index_add")
def index_add(url_data):
    print("这里是web.py的index_add", "-"*15, "url_data为", "-"*15)
    print(url_data)
    result = {
        ERROR_FLG: 0
    }
    # 检查字典格式是否正确
    try:
        user_name = url_data["users"]
        header = url_data["header"]
        comment = url_data["comment"]
        stars = int(url_data["stars"])
        good_id = int(url_data["good_id"])
    except:
        result[ERROR_MSG] = ERROR_MSG_1
        result[ERROR_FLG] = 1
        return result
    # 用datahelper.py连接数据库实现增删改操作
    info_helper = datahelper.DataHelper()
    pre_result = info_helper.add_to_mysql(user_name, stars, header, comment, good_id)

    # 检查pre_result是否有报错信息
    if pre_result[ERROR_FLG] == 1:
        result[ERROR_FLG] = 1
        result[ERROR_MSG] = pre_result[ERROR_MSG]
    else:
        result[SUCC_MSG] = pre_result[SUCC_MSG]
    result = json.dumps(result)
    print(result, "after converted to json")
    return result


@route(r"/index_del")
def index_del(url_data):
    print("这里是web.py的index_del", "-"*15, "url_data为", "-"*15)
    print(url_data)
    result = {
        ERROR_FLG:0
    }
    try:
        user_name = url_data["users"]
        good_id = url_data["good_id"]
    except:
        result[ERROR_MSG] = ERROR_MSG_1
        result[ERROR_FLG] = 1
        return result
    info_helper = datahelper.DataHelper()
    pre_result = info_helper.del_from_mysql(user_name,good_id)
    # 检查pre_result返回的报错信息
    if pre_result[ERROR_FLG] == 1:
        result[ERROR_FLG] = 1
        result[ERROR_MSG] = pre_result[ERROR_MSG]
    else:
        result[SUCC_MSG] = pre_result[SUCC_MSG]
    print(result)
    result = json.dumps(result)
    return result


def app(start_header, url, url_data=None):
    # 设置header

    print('*'*40)
    print("这里是web.py-------app")
    print("url: ", url)
    print("url_data: ", url_data)
    for temp_r, call_func in g_dict.items():
        ret = re.match(temp_r, url)
        if ret:
            # 设置header
            start_header("200 OK", {'Content-Type': 'text/html;charset=utf-8'})
            return call_func(url_data)
    # 如果输入无效网址
    print("无匹配方法")
    start_header("404 Not Found", {'Content-Type': 'text/html;charset=utf-8'})
    return "-----invalid-----url-----detected--------"



