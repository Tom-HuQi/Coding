import optparse, socket, configparser, json, os, sys

STATUS_CODE = {
    250: "Invalid cmd format, e.g:{'action':'get', 'filename':'test.py', 'size':344}",
    251: "Invalid cmd",
    252: "Invalid auth data",
    253: "Wrong username or password",
    254: "Passed authentication",
    255: "Filename doesn't provided",
    256: "File doesn't exist on server",
    257: "ready to send file",
    258: "md5 verification",

    800: "the file exist, but not enough, is continue?",
    801: "the file exist!",
    802: "ready to receive datas",

    900: "md5 valdate success"
}


class ClientHandler():

    def __init__(self):
        self.op = optparse.OptionParser()
        self.op.add_option("-H", "--host", dest="host")
        self.op.add_option("-P", "--port", dest="port")
        self.op.add_option("-u", "--username", dest="username")
        self.op.add_option("-p", "--password", dest="password")

        self.options, self.args = self.op.parse_args()
        # 校验参数方法
        self.verify_args()
        # 建立连接方法
        self.make_connection()
        self.mainPath = os.path.dirname(os.path.abspath(__file__))
        self.last = 0

    # 启动客户端且连接服务端的参数
    def verify_args(self):
        host = self.options.host
        port = self.options.port
        username = self.options.username
        password = self.options.password

        if int(port) > 0 and int(port) < 65535:
            return True
        else:
            # 端口错误,直接退出
            exit("Port is in 0-65535")

    # 建立连接
    def make_connection(self):
        self.sock = socket.socket()
        self.sock.connect((self.options.host, int(self.options.port)))

    # 交互方法
    def interaction(self):
        print("Begin to interractive...")
        if self.authenticate():
            while 1:
                cmd_info = input("[%s]" % self.current_dir).strip()
                cmd_list = cmd_info.split()
                if hasattr(self, cmd_list[0]):
                    func = getattr(self, cmd_list[0])
                    func(cmd_list)

    # 用户密码校验
    def authenticate(self):
        # 如果用户名密码为空,要用户输入
        if self.options.username is None or self.options.password is None:
            username = input("username:")
            password = input("password:")
            return self.get_auth_result(username, password)
        return self.get_auth_result(self.options.username, self.options.password)

    # 获取输入的用户名密码发给服务端验证
    def get_auth_result(self, user, pwd):
        data = {
            "action": "auth",
            "username": user,
            "password": pwd
        }

        self.sock.send(json.dumps(data).encode("utf-8"))
        response = self.response()
        response = json.loads(response)
        print("response:", response['status_code'])
        if response['status_code'] == 254:
            self.user = user
            self.current_dir = user
            print(STATUS_CODE[254])
            return True
        else:
            print(STATUS_CODE[response['status_code']])

    # 上传
    def upload(self, cmd_list):
        print(cmd_list)
        action, local_path, target_path = cmd_list
        local_path = os.path.join(self.mainPath, local_path)
        file_name = os.path.basename(local_path)
        file_size = os.stat(local_path).st_size

        data = {
            "action": "upload",
            "file_name": file_name,
            "file_size": file_size,
            "target_path": target_path
        }

        self.sock.send(json.dumps(data).encode("utf-8"))
        is_exist = self.sock.recv(1024).decode("utf-8")

        has_send = 0

        if is_exist == "800":
            # 断点续传
            choice = input("the file exist, but not enough, is continue?[Y/N]").strip()
            if choice.upper() == "Y":
                self.sock.sendall("Y".encode("utf-8"))
                continue_position = self.sock.recv(1024).decode("utf-8")
                has_send += int(continue_position)
            else:
                self.sock.sendall("N".encode("utf-8"))
        elif is_exist == "801":
            print("The file exist")
            return
        else:
            pass

        f = open(local_path, "rb")
        f.seek(has_send)
        while has_send < file_size:
            data = f.read(1024)
            self.sock.sendall(data)
            has_send += len(data)
            self.show_progress(has_send, file_size)
        f.close()
        print("upload success")

    # 文件展示
    def ls(self, cmd_list):
        data = {
            "action":"ls",
        }
        self.sock.sendall(json.dumps(data).encode('utf-8'))
        data = self.sock.recv(1024).decode('utf-8')
        print(data)

    # 切换路径
    def cd(self, cmd_list):
        data = {
            "action":"cd",
            "dirname":cmd_list[1]
        }
        self.sock.sendall(json.dumps(data).encode('utf-8'))
        data = self.sock.recv(1024).decode('utf-8')
        self.current_dir = os.path.basename(data)

    # 创建文件夹
    def mkdir(self, cmd_list):
        data={
            "action":"mkdir",
            "dirname":cmd_list[1]
        }
        self.sock.sendall(json.dumps(data).encode('utf-8'))
        data = self.sock.recv(1024).decode('utf-8')

    # 接收服务端消息方法
    def response(self):
        data = self.sock.recv(1024).decode("utf-8")
        return data

    # 进度条
    def show_progress(self, has, total):
        rate = float(has)/float(total)
        rate_num = int(rate * 100)
        if self.last != rate_num:
            sys.stdout.write("%s%% %s\r"%(rate_num, ">"*rate_num))
        self.last = rate_num


# 实例化socket对象
client = ClientHandler()

# 调用与服务端交互的方法
client.interaction()
