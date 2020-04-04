## FTP-Server

#### 1、导包问题

```python
# 获取当前py文件所在目录
PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 导入一个模块时import,默认python解析器搜索当前目录/已安装的内置模块和第三方模块,搜索路径存放在sys模块的path中
# 将PATH加入搜索路径中
sys.path.append(PATH)
```

#### 2、命令行参数问题

```python
首先你必须导入该类，并创建一个OptionParser对象，然后再使用parser.add_option(...)待定义命令行参数

import optparse

# 实例化OptionParser对象(可以带参，也可以不带参数),带参的话会把参数变量的内容作为帮助信息输出
Usage = 'main_analyze.py -d yyyy-mm-dd -p(path)'
Parser = optparse.OptionParser(usage=Usage)

def usage():
    Parser.add_option("-d", "--date", dest="date", default="", help=r'yyyy-mm-dd 通配使用')
    Parser.add_option("-l", "--log-path", dest="path", help=r"Log file dir.")
    # -c/--channel 都可以
    Parser.add_option("-c", "--channel", dest="channel", default="\d+", help=r"Log file dir.")   


if __name__ == '__main__':
	usage()
    # 解析脚本输入的参数值，options是一个包含了option值的对象  #args是一个位置参数的列表
	option, args = Parser.parse_args()      
	anal = bbt_analyze.Analyze(option.date, option.path, option.channel) 
	anal.run()
```

```python
# bbt_analyze.py文件
class Analyze:
    def __init__(self, date, path channel):
        self.date = date
        self.year, self.month, self.day = date.split('-')
        self.path = path
        self.patern = re.compile(r'%s/%s/%s/%s/' % (app_id, platform, channel_type, channel) + self.year + '/' + str(int(self.month)) + '/' + str(int(self.day)))
```

各个参数的含义：

- dest：用于保存输入的临时变量，其值通过options的属性进行访问，存储的内容是dest之前输入的参数，多个参数用逗号分隔
- type: 用于检查命令行参数传入的参数的数据类型是否符合要求，有 string，int，float 等类型
- help：用于生成帮助信息
- default: 给dest的默认值，如果用户没有在命令行参数给dest分配值，则使用默认值

**实例**

```python
import optparse
usage="python %prog -H <target host> -p/-P <target ports>"  #用于显示帮助信息
parser=optparse.OptionParser(usage)  #创建对象实例
parser.add_option('-H',dest='Host',type='string',help='target host')   ##需要的命令行参数
parser.add_option('-P','-p',dest='Ports',type='string',help='target ports' default="20,21")  ## -p/-P 都可以
(options,args)=parser.parse_args()
print(options.Host)
print(options.Ports)
```

```python
>python test.py -H 10.0.0.1 -P 20,21,22
>10.0.0.1
>20,21,22
```

#### 3. 目录结构

##### (1) bin/FTP_Server.py	

```python
此目录为FTP服务端启动目录。
主要通过if __name__ == '__main__'调用core/main.py中的AvgHandler()
```

##### (2) conf

```python
1. account.cfg
	主要存储用户名及密码[server.py采用configparser模块校验用户名密码]

2. settings.py
	基本配置
```











