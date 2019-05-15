from socket import *
from sys import *
from multiprocessing import *
import re
from urllib import parse


class Server(object):
    def __init__(self, port, app):
        # 创建服务器接听套接字
        self.tcp_server = socket(AF_INET, SOCK_STREAM)
        self.tcp_server.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        # 绑定本地ip和指定端口,设置为listen状态
        self.tcp_server.bind(("", port))
        self.tcp_server.listen()
        # 保存web文件的app方法
        self.app = app

    def set_response_header(self, status, headers):
        # 设置HTTP header
        self.header = "HTTP/1.1 " + status + "\r\n"
        # 添加各种属性
        for temp in headers.items():
            self.header += "%s:%s\r\n" % (temp[0], temp[1])
        # 空一行
        self.header += "\r\n"
        print(self.header)

    # 数据分离成字典形式
    @staticmethod
    def split_data(data):
        data_dict = dict()
        data_list = data.split("&")
        # 把数据用字典形式存储
        for temp in data_list:
            para_list = temp.split("=")
            data_dict[para_list[0]] = parse.unquote(para_list[1])
            print(parse.unquote(para_list[1]))
        return data_dict

    # 接受客户端请求
    def receive_info(self, worker_tcp):
        # 从客户端接收请求
        info = worker_tcp.recv(1024).decode("utf-8")

        if not info:
            worker_tcp.close()
            return
        print(">"*50)
        print(info)
        print(">"*50)
        # 处理获取数据请求
        request_lines = info.splitlines()
        # 第一行最后一行分离
        info_first_line = request_lines[0]

        print(">"*50)
        print("The first line is: ",info_first_line)
        print(">"*50)

        # 获取url
        ret = re.match(r"([^\s]+)\s(/[^\s]*)", info_first_line)

        # 获取请求方法和url
        request_type = ret.group(1)
        url = ret.group(2)

        # 设置默认根目录
        if url == "/":
            url = "/index.html"
        data_dict = dict()

        # post请求处理方法
        if request_type == "POST":
            info_last_line = request_lines[len(request_lines) - 1]
            print(">"*50)
            print("The last line is: ",info_last_line)
            print(">"*50)
            data_dict = eval(info_last_line)

        # get请求处理方法
        if request_type == "GET":
            print("*"*10, url, "*"*10)
            # 如果有数据存在
            if "?" in url:
                split_list = url.split("?")
                url = split_list[0]
                data_dict = self.split_data(split_list[1])

        # 打印值
        print(data_dict)
        print(url)
        # html静态文件
        if not url.startswith("/index_"):
            try:
                with open("./static"+ url, "rb") as f:
                    file_content = f.read()
            except:
                # 设置header
                self.set_response_header("404 Not Found", {'content-type': 'text/html;charset=utf-8'})
                print("*"*40)
                print(self.header)
                worker_tcp.send(self.header.encode("utf-8"))
                # 关闭套接字
                worker_tcp.close()
            else:
                # 设置header
                # 如果是css文件
                if url.endswith(".css"):
                    self.set_response_header("200 OK", {'content-type': 'text/css;charset=utf-8'})
                else:
                    self.set_response_header("200 OK", {'content-type': 'text/html;charset=utf-8'})

                print("-----------这是发送回去的header---------")
                print(self.header)
                print("-"*40)
                response = self.header.encode("utf-8") + file_content
                worker_tcp.send(response)
                # 关闭套接字
                worker_tcp.close()
        # _index结尾的，交给web框架
        else:
            # 用框架函数app处理得到body和header
            body = self.app(self.set_response_header, url, data_dict)
            if body:
                response = self.header + body
                print(response)
            else:
                response = self.header
            worker_tcp.send(response.encode("utf-8"))
            # 关闭套接字
            worker_tcp.close()

    def keep_run(self):
        while True:
            # 接受accept值
            worker_tcp, user_ip = self.tcp_server.accept()
            # 创建进程
            p = Process(target=self.receive_info, args=(worker_tcp,))
            p.start()
            worker_tcp.close()


def wrong_format():
    print("The format should be as the following:")
    print("python3 xxxx.py 7890 web:app")


def main():
    # 检查命令行参数
    if len(argv) == 3:
        try:
            port = int(argv[1])
            # 提取动态文件和接口
            ret = re.match(r"([^\s]+):([^\s]+)", argv[2])
            frame_name = ret.group(1)
            app_name = ret.group(2)
        except:
            # 报错，提示输入标准
            wrong_format()
            return
    else:
        wrong_format()
        return
    # 在系统中加入路径
    path.append("./dynamic")
    # 导入动态模块和方法
    frame = __import__(frame_name)
    app = getattr(frame, app_name)

    # 创建server对象
    web_server = Server(port, app)
    web_server.keep_run()


if __name__ == "__main__":
    main()