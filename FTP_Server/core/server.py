import socketserver, json, configparser, os

from conf import settings

# 状态码信息
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


# 采用socketserver, 支持多客户端访问
class ServerHandler(socketserver.BaseRequestHandler):

    def handle(self):
        while 1:
            data = self.request.recv(1024).strip().decode("utf-8")
            print("服务端：", data)
            data = json.loads(data)
            """
                事先定好C/S通信格式,action是操作命令
                {"action": "auth",
                 "username": "yuan",
                 "password": 123
                }
            """
            # 先判断客户端传递过来的数据有值,有值且由此命令方法则通过反射执行服务端操作命令方法
            if data.get("action"):
                if hasattr(self, data.get("action")):
                    func = getattr(self, data.get("action"))
                    # data是字典格式,采用打散传入对应的操作类方法
                    func(**data)
                else:
                    print("Invalid cmd")
            else:
                print("Invalid cmd")

    """
        命令操作类方法
    """

    # 登录 - 用户名密码的验证方法
    def auth(self, **data):
        username = data["username"]
        password = data["password"]

        user = self.authenticate(username, password)
        if user:
            self.send_response(254)
        else:
            self.send_response(253)

    # 文件上传
    def upload(self, **data):
        print("uploadData", data)
        file_name = data.get("file_name")
        file_size = data.get("file_size")
        target_path = data.get("target_path")
        abs_path = os.path.join(self.mainPath, target_path, file_name)

        has_receive = 0
        # 如果传过来的文件存在,要判断是否需要断点续传
        if os.path.exists(abs_path):
            file_has_size = os.stat(abs_path).st_size
            # 断点续传
            if file_has_size < file_size:
                self.request.sendall("800".encode("utf-8"))
                choice = self.request.recv(1024).decode("utf-8")
                if choice == "Y":
                    self.request.sendall(str(file_has_size).encode("utf-8"))
                    has_receive += file_has_size
                    f = open(abs_path, "ab")
                else:
                    f = open(abs_path, "wb")

            else:
                # 文件全
                self.request.sendall("801".encode("utf-8"))
                return

        else:
            self.request.sendall("802".encode("utf-8"))
            f = open(abs_path, "wb")

        while has_receive < file_size:
            try:
                data = self.request.recv(1024)
            except Exception as e:
                break
            f.write(data)
            has_receive += len(data)
        f.close()

    # 目录结构显示
    def ls(self, **data):
        # 只能查看自己home目录
        file_list = os.listdir(self.mainPath)
        file_str = "\n".join(file_list)
        if not len(file_list):
            file_str = "<empty dir>"
        self.request.sendall(file_str.encode('utf-8'))

    # 切换目录
    def cd(self, **data):
        dirname = data.get("dirname")
        if dirname == "..":
            self.mainPath = os.path.dirname(self.mainPath)
        else:
            self.mainPath = os.path.join(self.mainPath, dirname)

        self.request.sendall(self.mainPath.encode('utf-8'))

    def mkdir(self, **data):
        dirname = data.get("dirname")
        path = os.path.join(self.mainPath, dirname)
        if not os.path.exists(path):
            # 含有/表示是多级的
            if "/" in dirname:
                os.makedirs(path)
            else:
                os.mkdir(path)
                self.request.sendall("create success".encode('utf-8'))
        else:
            self.request.sendall("dirname exist".encode('utf-8'))

    """
        逻辑判断类方法
    """

    # 校验用户名密码
    def authenticate(self, user, pwd):
        cfg = configparser.ConfigParser()
        cfg.read(settings.ACCOUNT_PATH)

        if user in cfg.sections():
            if cfg[user]["Password"] == pwd:
                # 登录成功后,使用该用户名
                self.user = user
                self.mainPath = os.path.join(settings.BASE_DIR, "home", self.user)
                print("pass authenticate")
                return user

    # 向客户端发消息
    def send_response(self, status_code):
        response = {"status_code": status_code}
        self.request.sendall(json.dumps(response).encode("utf-8"))
