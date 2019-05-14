# coding: utf-8


VERSION = {
           # 项目不同环境配置   配置di1，st1等
           "di1": {"port": "443", "dbname01_db_ip": "100.69.13.43", "dbname02_db_ip": "100.69.13.43", "url_web": "https://msp-di1.dev.cmrh.com"},
           }

ENV_DEF_DIC = {
            # 项目的基础信息配置
            "project01": {
                # di环境配置
                "url": "https://msp-di1.dev.cmrh.com",
                "uri": "RH_MSPSERVER",
                "port": "443",
                "url_web": "https://msp-di1.dev.cmrh.com",
                "username": "L000000032@cmrhagent.com",
                "password": "cmrh1875",
                "code": "cmrh1875",
                "api_ini_name": [],
               },
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
