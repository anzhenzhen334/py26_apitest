"""
============================
Author:ann
Date:2020/3/6
Time:12:04
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
class TestAudit(unittest.TestCase):
    excel = ReadWriteExcel(case_file,'audit')
    cases = excel.read_excel()
    request = HandlerRequests()
    db = DB()

    @classmethod
    def setUpClass(cls):
        """
        管理员登录，方可执行添加项目审核等操作
        :return:
        """
        url = conf.get('env','base_url') + '/member/login'
        data = {
            'mobile_phone': conf.get('test_data','admin_mobile_phone'),
            'pwd': conf.get('test_data','admin_pwd')
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

    def setUp(self):
        """
        在每一条测试用例前都会执行setup，保证了每次执行审核前都新增了一个项目
        :return:
        """
        url = conf.get('env', 'base_url') + '/loan/add'
        data = {
            "member_id": getattr(CaseData,'member_id'),
            "title": "ann测试新增项目单位为月",
            "amount": 1000,
            "loan_rate": 5.0,
            "loan_term": 6,
            "loan_date_type": 1,
            "bidding_days": 1
                }
        headers = eval(conf.get('env', 'headers'))
        headers['Authorization'] = getattr(CaseData, 'token_value')

        response = self.request.send_request(url=url, method='post', json=data, headers=headers)
        res = response.json()

        loan_id = str(jsonpath.jsonpath(res, '$..id')[0])
        CaseData.loan_id = loan_id


    @data(*cases)
    def test_audit(self,case):
        """
        将登录（管理员）放在setupclass中实现，将添加项目放在setup中，保证了每次跑审核用例之前，都会先执行添加项目
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
        expected = eval(case['expected'])
        row = case['case_id'] + 1

        response = self.request.send_request(url=url,method=method,json=data,headers=headers)
        res = response.json()
        print('审核-测试用例执行结果：',res)

        if res['code'] == 0 and case['title'] =='项目未审核状态进行审核通过':
            pass_loan_id = str(data['loan_id'])
            CaseData.pass_loan_id = pass_loan_id

        if case['check_sql']:
            sql = 'select * from futureloan.loan where id={}'.format(getattr(CaseData, 'loan_id'))
            result = self.db.find_one(sql)
            end_status = result['status']
        try:
            self.assertEqual(res['code'],expected['code'])
            # self.assertEqual(res['msg'],expected['msg'])
            if case['check_sql']:
                self.assertEqual(end_status,expected['status'])
        #         把正常执行后应该是的状态放在expected中，与实际执行后的状态做对比进行断言。
        except Exception as e:
            self.excel.write_excel(row=row,column=8,value='未通过')
            log.error('测试用例{}执行未通过'.format(case['title']))
            log.exception(e)
            raise e
        else:
            self.excel.write_excel(row=row,column=8,value='通过')
            log.info('测试用例{}执行通过'.format(case['title']))