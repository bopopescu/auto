# coding: utf-8


VERSION = {
           # 项目不同环境配置   配置di1，st1等
           "di1": {"port": "443", "dbname01_db_ip": "100.69.13.43", "dbname02_db_ip": "100.69.13.43"},
           }

ENV_DEF_DIC = {
            # 项目的基础信息配置
            "project01": {
                # di环境配置
                "url": "https://100.69.181.13",
                "uri": "",
                "port": "443",
                "username": "zhangm002",
                "password": "cmrh1875",
                "api_ini_name": ["project01_para_configuration_01.ini"],
               },

            "project02": {
                # di环境配置
                "url": "http://100.69.181.31",
                "uri": "",
                "port": "80",
                "username": "admin",
                "password": "admin123456",
                "api_ini_name": ["project02_para_configuration_01.ini"],
            }
            }

ENV_DB_DIC = {
            # 项目用到的数据库配置
            "dbname01": {
                "db_name": "db_sid",
                "db_usr": "db_user",
                "db_pwd": "db_password",
                "db_ip": "100.69.13.43",
                "db_port": "4308"
            },
            "dbname02": {
                "db_name": "db_sid",
                "db_usr": "db_user",
                "db_pwd": "db_password",
                "db_ip": "100.69.13.43",
                "db_port": "4308"

            }
           }

ENV_SQL_DIC = {
                # demo
                "staffBindWechat": "",
            }
