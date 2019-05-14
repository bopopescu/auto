# -*- coding:utf-8 -*-
import os
import sys
from robot.api import logger
from robot.libraries import BuiltIn
from titanrun.common.Core import rh_replace_arg_dic, quit_driver, get_driver, split_input_arg, get_csv_by_no

class Model(object):
    def __init__(self,data_resouce, model="ride",version='',browser="chrome"):
        self.data_resouce = data_resouce
        self.model = model
        self.version = version
        self.browser = browser

    def web_model(self):
        if self.model == "ride":
            path = os.getcwd()
        else:
            path = os.path.abspath('..')
        Verify = BuiltIn._Verify()
        driver = get_driver()
        class_dict = dict()
        arg_dic = {}
        for i in range(len(self.data_resouce)):
            api, num = split_input_arg(self.data_resouce[i])
            api_name = api.split("_")[0]
            val_path = os.path.join(path,"config","web",api_name,"data","val","%s.csv"%api)
            elem_path = os.path.join(path,"config", "web", api_name, "data", "elem", "%s.csv" % api)
            val_data = get_csv_by_no(val_path, num)
            elm_data = get_csv_by_no(elem_path, 1)
            rh_replace_arg_dic(arg_dic, val_data)
            if i == 0:
                script_path = os.path.join(path,"business","script")
                sys.path.append(script_path)
                lists = os.listdir(script_path)
                for l in lists:
                    mod = __import__(l[:-3])
                    for c in dir(mod):
                        obj_class = getattr(mod, c)
                        class_dict[c] = obj_class
            for cla, obj in class_dict.items():
                obj_method = getattr(obj, api, None)
                if obj_method:
                    obj_method = getattr(obj(driver,self.browser,self.version), api)
                    result = obj_method(val_data,elm_data)
                    if not result.flag:
                        quit_driver(driver)
                        Verify.fail("%s failed,%s" %(obj_method.__name__,result.msg))
                    rh_replace_arg_dic(result.arg, arg_dic)
                    logger.info("%s success!" %obj_method.__name__)

if __name__ == '__main__':
    # data_resouce = [
    #     "gcm_login:1",
    #     "gcm_report:1",
    #     "gcm_deal:1",
    #     "gcm_enter:1",
    #     "gcm_review:1",
    #     "gcm_logout:1",
    #     "gcm_login:3",
    #     "gcm_approve:1",
    #     "gcm_logout:1",
    #     "gcm_login:1",
    #     "gcm_notice:1",
    #     "gcm_atp_enter:1",
    #     "gcm_atp_check:1"
    # ]
    # data_resouce = [
    #     "gps_login:1",
    #     "gps_apply:3",
    #     "gps_enter:1",
    #     "gps_add_insure:1",
    #     # "gps_change_insurance:1",
    #     "gps_check:1",
    #     "gps_logout:1",
    #     "gnc_login:1",
    #     "gnc_gps_manu_uw:1",
    #     "gnc_logout:1",
    #     "gps_login:1",
    #     "gps_pay_pool:1",
    #     "gps_pay_modify:1",
    #     "gps_logout:1",
    #     "gps_login:3",
    #     "gps_atp_enter:1",
    #     "gps_atp_check:1",
    #     "gps_logout:1",
    #     "gps_login:1",
    #     "gps_confirm:1",
    #     "gps_effective:1"
    # ]

    # data_resouce = [
    #     "gnc_login:1",
    #     "gnc_task_fill_query:1",
    #     "gnc_apply_allocation:2",
    #     "gnc_invoice_info_input:1",
    #     "gnc_cont_grp_insured_input:2",
    #     "gnc_apply_allocation_finish:1",
    #     "gnc_logout:1",
    #     "gnc_login:3",
    #     "gnc_atp_receive_and_pay:1",
    #     "gnc_atp_receive_and_paycheck:1",
    #     "gnc_logout:1",
    #     "gnc_login:1",
    #     "gnc_group_pol_approve:1",#fail
    #     "gnc_group_uw_auto:1",
    #     "gnc_manu_uw_all:1",
    #     "gnc_group_pol_sign:1",
    #     "gnc_get_url:2",
    #     "gnc_scanmock_vsc:2",
    #     "gnc_get_url:1",
    #     "gnc_policy_receipt_verify:1",
    #
    #     ]
    # data_resouce = [
    #     "gnc_login:1",
    #     "gnc_task_fill_query:1",
    #     "gnc_apply_allocation:3",
    #     "gnc_invoice_info_input:1",
    #     "gnc_cont_grp_insured_input:1",
    #     "gnc_apply_allocation_finish:1",
    #     "gnc_logout:1",
    #     "gnc_login:3",
    #     "gnc_atp_receive_and_pay:1",
    #     "gnc_atp_receive_and_paycheck:1",
    #     "gnc_logout:1",
    #     "gnc_login:1",
    #     "gnc_group_pol_approve:1",#fail
    #     "gnc_group_uw_auto:1",
    #     "gnc_manu_uw_all:1",
    #     "gnc_group_pol_sign:1",
    #     "gnc_get_url:2",
    #     "gnc_scanmock_vsc:2",
    #     "gnc_get_url:1",
    #     "gnc_policy_receipt_verify:1",
    #
    #     ]

    # data_resouce = [
    #     "uw_login:1",
    # "uw_incept_entry:10",
    # "uw_get_url:2",
    # "uw_scanmock_vsc:2",
    # "uw_get_url:1",
    # "uw_batch_ending:1",
    #     "uw_form_task_assign:1",
    #     "uw_check_policy_info_ins_client_info:1",
    #     "uw_check_policy_info_app_client_info:1",
    #     "uw_check_policy_info_account:1",
    #     "uw_check_policy_info_beneficiary_info:1,",
    #     "uw_check_policy_info_report:1",
    #     "uw_check_policy_info_main_product:10",
    #     "uw_check_policy_info:2",
    #     "uw_assign_check_task:1",
    #     "uw_logout:1",
    #     "uw_login:2",
    #     "uw_check_list:1",
    #     "uw_dispatch_undwrt_task_page:1",
    #     "uw_logout:1",
    #     "uw_login:1",
    #     "uw_undwrt_task_list_closeproblem:1",
    #     "uw_undwrt_task_list_evaluateform:1",
    #     "uw_undwrt_task_list:1",
    #     "uw_logout:1",
    #     "uw_login:3",
    #     "uw_fin_receive:1",
    #     "uw_fin_receive_check:1",
    #     "uw_logout:1",
    #     "uw_login:1",
    #     "uw_issue_indivival_main:1",
    #     "uw_sms_send_check:1",
    #     "uw_print_task_check:1"
    # ]
    data_resouce = [
         "uw_login:1",
        "uw_incept_entry:1",# 8-5005
        # "uw_logout:1",
        # "uw_login:2",
        # "uw_get_url:2",
        # "uw_scanmock_vsc:1",# 1-1001/5005;2-2002
        # "uw_get_url:1",
        # "uw_batch_ending:1",
        # "uw_form_task_assign:1",
        #  "uw_check_policy_info_ins_client_info:18",
        # "uw_check_policy_info_app_client_info:20",
        # # "uw_check_policy_info_beneficiary_info:1,",  # list,必须加上","
        # "uw_check_policy_info_account:1",
        # "uw_check_policy_info_report:1",
        # "uw_check_policy_info_main_product:20",# 8-5005
        # # "uw_check_policy_info_add_product:1,",  # 没有就不要
        # "uw_check_policy_info:3",# 3-5005
        # "uw_assign_check_task:1",
        # "uw_logout:1",
        # "uw_login:2",  # zyb login
        # "uw_check_list:1",
        # "uw_dispatch_undwrt_task_page:1",
        # "uw_logout:1",
        # "uw_login:1",  # szx login
        # # "uw_undwrt_task_list_note:1",
        # # "uw_undwrt_task_list_vsc:1",
        # # "uw_get_url:2",
        # # "uw_scanmock_vsc:3",
        # # "uw_get_url:1",
        # # "uw_undwrt_task_list_writeoff:1", #容易出错
        # "uw_undwrt_task_list_closeproblem:1",
        # "uw_undwrt_task_list_evaluateform:1",  # 非标为2
        # "uw_undwrt_task_list:1",
        # # 下发核保决定（非标体通过）后需要增加如下5个操作
        # # "uw_undwrt_task_list_vsc:2",
        # # "uw_get_url:2",
        # # "uw_scanmock_vsc:4",
        # # "uw_get_url:1",
        # # "uw_undwrt_task_list_writeoff:2",
        # "uw_logout:1",
        # "uw_login:3",  # wyf login
        #  "uw_fin_receive:1",
        # "uw_fin_receive_check:1",
        # "uw_logout:1",
        # "uw_login:1",
        #  "uw_issue_indivival_main:1",
        # "uw_sms_send_check:1",
        # "uw_print_task_check:1",
    ]

    # data_resouce = [
    #         "pos_login:1",
    #         "pos_entry_client_locate:1",
    #         "pos_entry_client_select:1",
    #         "pos_entry_apply_info_input:2",   #退保2，犹豫期退保1
    #         "pos_entry_accept_item_confirm:1",
    #         "pos_entry_binding_order_adjust:1",
    #         "pos_entry_accept_detail_input:2",  #退保2，犹豫期退保1
    #         "pos_entry_accept_result:1",
    #         "pos_entry_accept_finish:1",
    #         "pos_integrate_query:1",
    #         "pos_logout:1",
    #         "pos_login:2",
    #         "pos_fin_payment:1",
    #         "pos_fin_payment_check:1"
    #         ]

    # data_resouce = [
    #                 "claim_login:1",
    #                 # "claim_report:3",
    #                 # "claim_deal:1",
    #                 # "claim_get_url:2",
    #                 # "claim_scanmock_vsc:1",
    #                 # "claim_get_url:1",
    #                 # "claim_deal2:1",
    #                 # "claim_case_input_applicant:1",
    #                 # "claim_case_input_payee:1",
    #                 # "claim_case_input_accident_disease:3",
    #                 "claim_examination_main:1",
    #                 "claim_logout:1",
    #                 "claim_login:2",  # zyb login
    #                 "claim_review:1",
    #                 "claim_notice:1",
    #                 "claim_logout:1",
    #                 "claim_login:3",
    #                 "claim_fin_payment:1",
    #                 "claim_fin_payment_check:1",
    #                 ]
    # data_resouce=[
    #     # "bep_login:1",
    #     # "bep_bill_new_page_base3:1",
    #     # "bep_bill_new_page_expense3:4,",
    #     # "bep_bill_new_page_submit3:1",
    #     # "bep_personal_documents:1",
    #     # "bep_get_url:2",
    #     # "bep_scanmock_vsc:1",
    #
    #             # "bep_login:1",
    #             # "bep_bill_new_page_base:1",
    #             # "bep_bill_new_page_expense:1,",
    #             # "bep_bill_new_page_submit:1",
    #             # "bep_personal_documents:1",
    #             # "bep_get_url:2",
    #             # "bep_scanmock_vsc:1",
    #
    #
    #               #   "bep_login:2",
    #               # "bep_bill_new_page_base:4",
    #               # "bep_bill_new_page_expense:7,",
    #               # "bep_bill_new_page_submit:1",
    #               # "bep_personal_documents:1",
    #               # "bep_get_url:2",
    #               # "bep_scanmock_vsc:1",
    #
    #                 "bep_login:7",
    #                 "bep_group_work:1",
    #                 "bep_center_task_trial:1",
    #                 "bep_group_work:2",
    #                 "bep_center_task_trial:1",
    #               ]
    # data_resouce=["atp_login:1",
    #               # "atp_transfer_draw:1",
    #               "atp_agreement_batch:1"
    #               ]
    # path = "D:/worksvn/rh_auto_test_9.30"
    # file = "D:/worksvn/rh_auto_test_9.30/config/web/claim/cfg/claim_configuration.ini"
    web_model(data_resouce, "python")