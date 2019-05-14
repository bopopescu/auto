#接口自动化录制工具

##环境
python3

mitmproxy

window

##安装
python可以安装anaconda，py2、py3多环境共存

pip install mitmproxy

下载对应环境mitm证书。浏览器打开mitm.it

##使用
1、命令行下运行python get_Inter_Data.py启动

2、开始业务测试操作

3、测试完成，按下ctrl+c停止录制会自动生成para_configuration.ini(自动化测试所需的ini文件)和record.json(接口全部数据)