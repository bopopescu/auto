#-*- coding:utf-8 -*-
import os
import cx_Oracle
import time
from Result import Result

os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8'
class RHOracle(object):
    def __init__(self,usr="biacde",pwd="zhaoshang001",ip="10.62.52.60",port="1634",db="slis"):
        connstr = "%s/%s@%s:%s/%s" %(usr,pwd,ip,port,db)
        retry_count = 3
        backoff = 1.2
        count = 0
        while count < retry_count:
            try:
                self.conn = cx_Oracle.connect(connstr)
                self.cursor = self.conn.cursor()
                return
            except Exception:
                time.sleep(backoff)
                count = count + 1
        if retry_count == 3:
            raise Exception("Unable to connect to Database after 3 retries.")

    def fetchall_query(self,sql, param=[]):
        if len(param) > 0:
            self.cursor.execute(sql, param)
        else:
            self.cursor.execute(sql)
        retval = self.cursor.fetchall()
        return retval

    def fetchone_query(self, sql, param=[]):
        if len(param) > 0:
            self.cursor.execute(sql, param)
        else:
            self.cursor.execute(sql)
        retval = self.cursor.fetchone()
        return retval

    def execute_query(self, sql, param=[]):
        if len(param) > 0:
            retval = self.cursor.execute(sql, param)
        else:
            retval = self.cursor.execute(sql)
        return retval
		
    def execute_commit(self,sql):
        result = Result()
        try:
            self.cursor.execute(sql)
            self.conn.commit()
            result.flag=True
        except Exception, e:
            result.flag=False
            result.msg=str(e)
            raise Exception(e)
        return result

    '''
    查询多条返回 True， False    
    param参数可传list或dict， EG：param = ["1186020000068016"]，param = {"apply_bar_code": "1186020000068016"}
    '''
    def execute_query_many(self, sql_list, param=[]):
        result_list = []
        result = Result()
        try:
            for sql in sql_list:
                if "%s" in sql or "%d" in sql or ":" in sql:
                    self.cursor.execute(sql, param)
                else:
                    self.cursor.execute(sql)
                retval = self.cursor.fetchone()
                result_list.append(retval)
            result_list = [i[0] for i in result_list]
            if len(result_list) == 1:
                if result_list[0] == 1:
                    result.flag = True
                else:
                    result.flag = False
            else:
                result.flag = reduce(lambda x, y: x == y and x != 0, result_list)
        except Exception, e:
            result.flag = False
            result.msg = str(e)
        return result

    '''
    数据回滚/insert数据
    '''
    def execute_rollback_sql(self, sql_list, param=[]):
        try:
            for sql in sql_list:
                if "%s" in sql or "%d" in sql or ":" in sql:
                    self.cursor.execute(sql, param)
                else:
                    self.cursor.execute(sql)
            self.conn.commit()
        except Exception, e:
            print str(e)

    def check_query_count(self,sql):
        flag = False
        data = self.fetchone_query(sql)
        if int(data[0]) >= 1:
            flag = True
        return flag
#长险导核心
    def bia_to_core_batch(self, pono):
        result = Result()
        p_o_flag =self.cursor.var(cx_Oracle.STRING)
        p_o_msg = self.cursor.var(cx_Oracle.STRING)
        res =self.cursor.callproc("l_bia_eod_batch.bia_sync_to_core_by_pono",[pono,p_o_flag,p_o_msg])
        self.conn.commit()
        if res[1]=="Y":
            result.flag = True
        result.msg = res[2]
        return result
#短险导核心
    def biab_to_core_batch(self, pono):
        result = Result()
        p_type = self.cursor.var(cx_Oracle.STRING)
        p_o_flag =self.cursor.var(cx_Oracle.STRING)
        p_o_msg = self.cursor.var(cx_Oracle.STRING)
        res =self.cursor.callproc("biabcde.l_biab_service_batch.BIAB_SYNC_TO_CORE",[pono,p_type ,p_o_flag,p_o_msg])
        self.conn.commit()
        if res[2]=="Y":
            result.flag = True
        result.msg = res[3]
        return result        

    def update_policy_info(self, p_policy_no,p_effect_date):
        result = Result()
        flag = self.cursor.callfunc('pubcde.l_tmp_sys_test.update_policy_info', cx_Oracle.STRING,
                                    [p_policy_no, p_effect_date])
        if flag == 'Y':
            result.flag=True
        return result
	
    def fin_check(self,pono):
        result = Result()
        confirm_no_sql = "select f.confirm_no from fin_comp_account_trad_conf f where f.confirm_no like 'CK%'"

        try:
            confirm_no = self.fetchone_query(confirm_no_sql)[0]
            sql = "update fin_bank_trading g set g.confirm_no = '%s' where g.bank_trading_seq in (select t.bank_trading_seq from fin_temporary_collection t where t.policy_no = '%s')" %(confirm_no,pono)
            self.cursor.execute(sql)
            self.conn.commit()
            result.flag = True
        except Exception,e:
            result.msg = str(e)
        return result


    def __del__(self):
        self.cursor.close()
        self.conn.close()

if __name__ == '__main__':
    param = ["1186020000068016"]
    # param = {"apply_bar_code": "1186020000068016"}
    sqltest = RHOracle(usr="dbcheck", pwd="zhaoshang001", ip="10.62.54.35", db="slis")

    sql = ["select count(1) from uw_apply_info where apply_bar_code = :1 and apply_status = 09", "select count(1) from uw_apply_info where apply_bar_code = :1 and apply_status = 06"]
    # sql = ["select count(1) from uw_apply_info where apply_bar_code = :apply_bar_code and apply_status = 09", "select count(1) from uw_apply_info where apply_bar_code = :apply_bar_code and apply_status = 06"]
    result = sqltest.execute_query_many(sql, param)
    print result.flag

