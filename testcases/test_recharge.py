"""
============================
Author:ann
Date:2020/3/5
Time:15:33
E-mail:326329411@qq.com
Mobile:15821865916
============================
"""
import unittest
import os
import jsonpath
from library.ddt import ddt,data
from common.read_write_excel import ReadWriteExcel
from common.handlerpath import DATA_DIR
from common.handlerconfig import conf
from common.handlerrequests import HandlerRequests
from common.handlerlog import log
from common.connectdb import DB
from common.handlerdata import CaseData,replace_data
from decimal import Decimal
from common.handle_sign import HandleSign

case_file = os.path.join(DATA_DIR,'apicases.xlsx')

@ddt
class TestRecharge(unittest.TestCase):
    excel = ReadWriteExcel(case_file,'recharge')
    cases = excel.read_excel()
    request = HandlerRequests()
    db = DB()

    @classmethod
    def setUpClass(cls):
        url = conf.get('env','base_url') + '/member/login'
        data = {
            'mobile_phone':conf.get('test_data','mobile_phone'),
            'pwd':conf.get('test_data','pwd')
        }
        headers = eval(conf.get('env', 'headers'))

        response = cls.request.send_request(url=url,method='post',json=data,headers=headers)
        res = response.json()

        token = jsonpath.jsonpath(res,'$..token')[0]
        token_type = jsonpath.jsonpath(res,'$..token_type')[0]
        member_id = str(jsonpath.jsonpath(res,'$..id')[0])

        token_value = token_type + ' ' + token
        CaseData.token_value = token_value
        CaseData.member_id = member_id
        CaseData.token = token

    @data(*cases)
    def test_recharge(self,case):
        """
        将登录放在setupclass中实现，获取到token_value作为该接口的入参
        :param case:
        :return:
        """
        url = conf.get('env','base_url') + case['url']
        method = case['method']

        headers = eval(conf.get('env', 'headers'))
        headers['Authorization'] = getattr(CaseData,'token_value')

        case['data'] = replace_data(case['data'])
        data = eval(case['data'])
        # 在请求体中加入，时间戳和签名
        sign_info = HandleSign.generate_sign(getattr(CaseData, "token"))
        data.update(sign_info)
        print('测试用例中data的值是：',data)
        print('data金额的值是：',data['amount'])
        expected = eval(case['expected'])
        row = case['case_id'] + 1

        if case['check_sql']:
            sql = 'select * from futureloan.member where id={}'.format(getattr(CaseData,'member_id'))
            result = self.db.find_one(sql)
            start_amount = result['leave_amount']
            # print('执行充值前的金额是：',start_amount)
        response = self.request.send_request(url=url,method=method,json=data,headers=headers)
        res = response.json()
        print('充值-测试用例执行结果：',res)

        if case['check_sql']:
            sql = 'select * from futureloan.member where id={}'.format(getattr(CaseData, 'member_id'))
            result = self.db.find_one(sql)
            end_amount = result['leave_amount']
            # print('执行充值后的金额是：', end_amount)
        try:
            self.assertEqual(res['code'],expected['code'])
            # self.assertEqual(res['msg'],expected['msg'])
            if case['check_sql']:
                self.assertEqual(end_amount-start_amount,Decimal(str(data['amount'])))
        except Exception as e:
            self.excel.write_excel(row=row,column=8,value='未通过')
            log.error('测试用例{}执行未通过'.format(case['title']))
            log.exception(e)
            raise e
        else:
            self.excel.write_excel(row=row,column=8,value='通过')
            log.info('测试用例{}执行通过'.format(case['title']))
