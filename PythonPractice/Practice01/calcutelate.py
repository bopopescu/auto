# -*- coding: utf-8 -*-

# @Time    : 2018/8/27 18:13
# @Author  : songq001
# @Comment : 

"""
h、涉及数据及来源：
（1） 金控公司资本充足率=金控公司合格资本净额/金控公司法定资本*100%
（2）金控公司合格资本净额=金融控股公司合格资本-扣减项
（3）金融控股公司合格资本=核心资本+附属资本
（4）核心资本=实收资本（K54）+资本公积（K64）+盈余公积（K69）
+未分配利润（K73）
（5）附属资本=一般风险准备（K72）
（6）扣减项=商誉+长期股权投资-核心资本*10%
          =商誉（E60）+长期股权投资（E45）-核心资本*10%

以上字段数据均来自资产负债表（对应的列和行）；

金控公司法定资本数据来源：H端手动上报；
金控公司法定资本=所有子公司（并表范围的公司）对应的法定资本*金控公司持股比例；
"""


def calcutelate(legal_capital):
    """
    input: legal_capital 金控公司法定资本
    4001:实收资本（K54） 4002：资本公积(K64)。4101:盈余公积(K69)  4190:未分配利润(K73)  4102:一般风险准备（K72）  1711：商誉（E60) 1524：长期股权投资 (E45)
    :return: 
    """
    base_dict = {"1524": 90917171335.47, "1711": 9670605.55,  "4001": 107030000.00,  "4002": 4508099237.61,
                "4101": 282827606.00, "4102": 3086793890.36, "4190": 72971043131.70}
    # 核心资本
    core_sum = base_dict["4001"] + base_dict["4002"] + base_dict["4101"] + base_dict["4190"]
    # 扣减项
    deduction = base_dict["1711"] + base_dict["1524"] - core_sum*0.1
    # 金融控股公司合格资本
    qualified_capital = core_sum + base_dict["4102"]
    # 金控公司合格资本净额
    capital_netamount = qualified_capital - deduction
    print "金控公司合格资本净额：" + str(capital_netamount)
    # 金控公司资本充足率
    capital_adequacyratio = capital_netamount / legal_capital

    print "金控公司资本充足率：%.2f" % (capital_adequacyratio*100) + "%"


if __name__ == '__main__':
    legal_capital = 319856013570.46
    calcutelate(legal_capital)



