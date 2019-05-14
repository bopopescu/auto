# -*- coding: utf-8 -*-

# @Time    : 2018/4/20 17:47
# @Author  : songq001
# @Comment :

from titanrun.common.DbOperate import RHOracle
from business.conf import EnvSetting


# ############################相关DB的处理--Start##############################################################
def connect_db(version, sid):
    sqlobj = RHOracle(usr=EnvSetting.ENV_DB_DIC.get(sid)["db_usr"],
                      pwd=EnvSetting.ENV_DB_DIC.get(sid)["db_pwd"],
                      ip=EnvSetting.VERSION.get(version)[sid + "_db_ip"],
                      db=EnvSetting.ENV_DB_DIC.get(sid)["db_name"])
    return sqlobj


def check_sql(sql_list, db_usr, db_pwd, db_ip, db_name, param=[]):
    sqlobj = RHOracle(usr=db_usr, pwd=db_pwd, ip=db_ip, db=db_name)
    result = sqlobj.execute_query_many(sql_list, param)
    return result


def dml_sql(sql_list, db_usr, db_pwd, db_ip, db_name, param=[]):
    sqlobj = RHOracle(usr=db_usr, pwd=db_pwd, ip=db_ip, db=db_name)
    sqlobj.execute_rollback_sql(sql_list, param)


def check_db(sql_list, version, sid='slis', param=[]):
    result = check_sql(sql_list, EnvSetting.ENV_DB_DIC.get(sid)["db_usr"], EnvSetting.ENV_DB_DIC.get(sid)["db_pwd"],
                            EnvSetting.VERSION.get(version)[sid + "_db_ip"],
                            EnvSetting.ENV_DB_DIC.get(sid)["db_name"], param)
    return result


def dml_db(sql_list, version, sid='slis', param=[]):
    dml_sql(sql_list, EnvSetting.ENV_DB_DIC.get(sid)["db_usr"], EnvSetting.ENV_DB_DIC.get(sid)["db_pwd"],
                 EnvSetting.VERSION.get(version)[sid + "_db_ip"],
                 EnvSetting.ENV_DB_DIC.get(sid)["db_name"], param)

# ############################相关DB的处理--END################################################################


