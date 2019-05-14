#coding=utf-8
import json,sys,ConfigParser
import requests

reload(sys)
sys.setdefaultencoding('utf-8')

def mid_biam_post(bussiness_data, method, rh_public_key, df_private_key, mid_url):
    mid_default_data = {"0": {"data": bussiness_data, "charset": "utf-8", "isEncrypt": "true", "isSign": "true",
                                "publicKey": rh_public_key, "privateKey": df_private_key}}
    mid_default_jsondata = json.dumps(mid_default_data, ensure_ascii=False)
    encrypt_biam_data = {"bean": "BiaEncryptDecrypt", "method": method, "arguments": mid_default_jsondata,
                           "random": "0.20185059086950652"}
    mid_response = requests.post(mid_url, encrypt_biam_data)
    result = json.loads(mid_response.text).get("data").get("data")
    if type(result)!=dict:
        result = eval(result)
    return result

def get_bussiness_data(bussiness_para, sevice_name,new_dic):
    bussiness_data = {'appKey': '2842652df9efa1bcd75750d81d892914', 'charset': 'UTF-8', 'version': '1.0.0','signType': 'RSA','timestamp': '20170608112956057', 'format': 'json', 'requestNo': '123455'}
    bussiness_data["serviceName"] = sevice_name
    if sevice_name =="cmrh.policy.product.GBatchIssue":
        request_param = json.dumps(bussiness_para, ensure_ascii=False)
        bussiness_data["requestParam"] = request_param
    elif sevice_name =="cmrh.policy.product.BatchWithdraw":
        bussiness_data["policyNo"] = new_dic.get("policyNo",bussiness_para["policyNo"])
        bussiness_data["channelOrderNo"] = bussiness_para["channelOrderNo"]
    elif sevice_name =="cmrh.policy.product.TicketChanges":
        print "************************"
        bussiness_para["policyNo"] = new_dic.get("policyNo",bussiness_para["policyNo"])
        request_param = json.dumps(bussiness_para, ensure_ascii=False)
        bussiness_data["requestParam"] = request_param
    return bussiness_data


