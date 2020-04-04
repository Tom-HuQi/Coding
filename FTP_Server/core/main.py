import optparse, socketserver, os, sys

# 导包
PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PATH)
from conf import settings
from core import server


# optparse用于处理命令行参数解析
class AvgHandler():

    def __init__(self):
        self.op = optparse.OptionParser()
        # self.op.add_option("-H", "--host", dest="host")
        # self.op.add_option("-P", "--port", dest="port")
        # options是包含以上参数对象,args是传递的位置参数。
        # 如:python test.py -H 127.0.0.1 -P 80 START;args接收的就是START
        options, args = self.op.parse_args()
        # 对客户端输入的命令进行分发(利用反射实现)
        self.verify_args(options, args)

    # 命令参数的分发
    def verify_args(self, options, args):
        cmd = args[0]
        if hasattr(self, cmd):
            func = getattr(self, cmd)
            func()

    # 启动FTP-Server,支持多客户端访问(利用socketserver实现)
    def start(self):
        print("The server is working...")
        # sockerserver逻辑单独写成一个server文件
        ftp_server_socket = socketserver.ThreadingTCPServer((settings.IP, settings.PORT), server.ServerHandler)
        ftp_server_socket.serve_forever()
