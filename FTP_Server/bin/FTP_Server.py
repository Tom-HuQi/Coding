import os, sys

# 获取当前py文件所在目录
PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 导入一个模块时import,默认python解析器搜索当前目录/已安装的内置模块和第三方模块,搜索路径存放在sys模块的path中
# 将PATH加入搜索路径中
sys.path.append(PATH)

from core import main

if __name__ == '__main__':
    main.AvgHandler()
