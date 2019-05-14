
html_model_pub 即http请求原始form形式参数接口使用说明：

需配置项：
1.参照：D:\rh_auto_test\business\conf\BusinessSetting.py

说明：

MSP_DEF_DIC={"msp":{
                "url":"https://perf.dev.cmrh.com/RH_MSPSERVER",              //系统接口请求地址前缀
                "login_url":"https://perf.dev.cmrh.com",                     //登录地址前缀，若与url一致也必须放入值
                "api_ini_name":"msp_para_configuration.ini",                 //接口配置信息的ini文件
                "db_bia_usr":"biacde",
                "db_fin_usr":"findata",
                "db_bia_pwd":"zhaoshang001",
                "db_fin_pwd":"zhaoshang001",
                "db_ip":"110.62.54.51",
                "db_name":"slis",
                "db_port":"1634"
               },
 }


2.参照：D:\rh_auto_test\config\api\msp\msp_para_configuration.ini

说明：
[PARA]                  --接口返回值存储引用
DICT_IN_OUT

[IS_LOGIN]              --登录信息
LOGIN_SIGN=Y            --登录标识，若接口无需登录，则写N即可
LOGIN_URL={}            --登录的url和默认参数， 用dick存储

[MODEL_URL]             --拼接接口的url模块
MODEL_URL_DATA


[UPLOAD]
UPLOAD_DEFAULT_FILES    --上传接口相关的变量信息


[RE]
RE_SET=                 --正则表达式设置，用于抓取html返回页面的相关值 （目前一个接口只支持一个，需要再扩展修改）


[METHED]
REQUEST_METHOD          --请求接口的类型，post，get还是上传文件


[DATA]
MSP_DEFAULT_DATA        --请求接口的默认参数


剩余其他同xml，db处理等


3.引入包
import urllib3
from urllib3.exceptions import InsecureRequestWarning
from collections import OrderedDict

