from socket import *
import re
import multiprocessing
import time
import dynamic.mini_frame

class WSGIServer(object):
    def __init__(self):
        # initialize tcp_server
        self.tcp_server = socket(AF_INET,SOCK_STREAM)
        # set port to be re-usable
        self.tcp_server.setsockopt(SOL_SOCKET, SO_REUSEADDR,1)
        # give port:8080 to the server
        self.tcp_server.bind(("",8080))
        self.tcp_server.listen()

    def service_client(self,new_socket):
        print("成功建立连接！")
        # receive from clients
        request = new_socket.recv(1024).decode("utf-8")
        list_a = request.splitlines()
        print(">"*20)
        print(list_a)
        dest = re.match(r"[^/]+(/)([^ ]*)", list_a[0])
        # check dest's value
        if dest:
            if dest.group(2) == "":
                dest_file = "index.html"
            else:
                dest_file = dest.group(2)
        
        #if file_name does not end with .py, then it is static
        if not dest_file.endswith(".py"):
            print("正在打开"+dest_file)
            # open file, read and send back
            try:
                file_a = open("./static/" + dest_file, "rb")
            except:
                print("打开失败")
                response = "HTTP/1.1 404 NOT FOUND\r\n"
                response += "\r\n--------file not found-------"
                new_socket.send(response.encode("utf-8"))
            else:
                info = file_a.read()
                file_a.close()
                print("文件已关闭")
                response = "HTTP/1.1 200 OK\r\n"
                response += "\r\n"
                new_socket.send(response.encode("utf-8"))
                new_socket.send(info)
                print("信息发送成功")
        else:
            env = dict()
            env['PATH_INFO'] = dest_file
            body = dynamic.mini_frame.application(env,self.set_response_header)
            # if ends with .py,construct header from self.status
            header = "HTTP/1.1 %s\r\n" % self.status
            # construct header from self.header
            for temp in self.headers:
                header += "%s:%s\r\n" % (temp[0],temp[1])
            header += '\r\n'
            # use wsgi
            response = header + body
            # send response to the browser
            new_socket.send(response.encode("utf-8"))

        new_socket.close()

    def set_response_header(self,status,headers):
        self.status = status
        self.headers = [('server','mini_web v8.8')]
        self.headers += headers


    def run_forever(self):
        while True:
            tcp_worker,user_ip = self.tcp_server.accept()
            # use multiprocessing for time effient reasons
            p = multiprocessing.Process(target=self.service_client,args=(tcp_worker,))
            p.start() 
            # close worker and free space   
            tcp_worker.close()
        # close server if interrupted
        self.tcp_server.close()

def main():
    """ controll all, create web-server object and run forever """
    wsgi_server = WSGIServer()
    wsgi_server.run_forever()

if __name__ == "__main__":
    main()
