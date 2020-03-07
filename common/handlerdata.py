"""
============================
Author:ann
Date:2020/2/28
Time:20:44
E-mail:326329411@qq.com
Mobile:15821865916
============================
"""
import re
from common.handlerconfig import conf

class CaseData:
    # 这个类专门用来保存用例执行过程中提取出来的、给其他用例用的数据（例如test_charge中的setupclass中提取出来的token_value和member_id
    pass

def replace_data(s):
    r1 = r"#(.+?)#"
    while re.search(r1,s):
        # 根据是否匹配到要替换的数据，来判断要不要进入循环
        res = re.search(r1, s)
        # 匹配一个需要替换的内容 如#mobile_phone#
        data = res.group()
        # 获得需要替换的内容
        key = res.group(1)
        # 获取需要替换的字段如mobile_phone
        try:
            # s = s.replace(data, conf.get('test_data', key))
            s = re.sub(r1,conf.get('test_data', key),s,1)
        #     根据要替换的字典，去配置文件中找对应的数据，进行替换
        except Exception as e:
            # s = s.replace(data, getattr(CaseData,key))
            s = re.sub(r1, getattr(CaseData,key), s, 1)
    #         如果配置文件找不到，报错了，则去CaseData的属性中找对应的值进行替换
    return s

# s= '{"member_id":#member_id#,"amount":1000,"loan_id=#loan_id#"}'
# r1= r"#(.+?)#"
# res = re.search(r1,s)
# # res的结果是一个match对象
# print(res)
# data = res.group()
# # data的结果是#member_id#
# print(data)
# key = res.group(1)
# # key的结果是member_id
# print(key)