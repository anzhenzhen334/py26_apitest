"""
============================
Author:ann
Date:2020/3/3
Time:10:16
E-mail:326329411@qq.com
Mobile:15821865916
============================
"""
import unittest
import os
import jsonpath
from library.ddt import ddt, data
from common.read_write_excel import ReadWriteExcel
from common.handlerpath import DATA_DIR
from common.connectdb import DB
from common.handlerrequests import HandlerRequests
from common.handlerconfig import conf
from common.handlerlog import log
from common.handlerdata import CaseData
from common.handle_sign import HandleSign

case_file = os.path.join(DATA_DIR, "apicases.xlsx")
@ddt
class TestLoans(unittest.TestCase):
    excel = ReadWriteExcel(case_file, "loans")
    cases = excel.read_excel()
    request = HandlerRequests()
    db = DB()

    @classmethod
    def setUpClass(cls):
        url = conf.get('env', 'base_url') + '/member/login'
        data = {
            'mobile_phone': conf.get('test_data', 'admin_mobile_phone'),
            'pwd': conf.get('test_data', 'admin_pwd')
        }
        headers = eval(conf.get('env', 'headers'))

        response = cls.request.send_request(url=url, json=data, headers=headers, method='post')
        res = response.json()
        token = jsonpath.jsonpath(res, '$..token')
        token_type = jsonpath.jsonpath(res, '$..token_type')
        CaseData.token_value = token_type[0] + ' ' + token[0]
        CaseData.member_id = jsonpath.jsonpath(res, '$..id')[0]
        CaseData.token = token[0]

    @data(*cases)
    def test_loans(self, case):
        url = conf.get('env','base_url')+case['url']
        method= case['method']
        data = eval(case['data'])
        # 在请求体中加入，时间戳和签名
        sign_info = HandleSign.generate_sign(getattr(CaseData, "token"))
        data.update(sign_info)
        headers=eval(conf.get('env','headers'))
        headers['Authorization'] = getattr(CaseData,'token_value')
        expected = eval(case["expected"])
        row = case["case_id"] + 1

        response=self.request.send_request(url=url,method=method,params=data,headers=headers)
        res = response.json()
        print('项目列表接口返回的结果：',res)
        try:
            self.assertEqual(res['code'],expected['code'])
        except Exception as e:
            self.excel.write_excel(row=row,column=8,value='未通过')
            log.error('测试用例{}执行未通过'.format(case['title']))
            log.exception(e)
            raise e
        else:
            self.excel.write_excel(row=row,column=8,value='通过')
            log.info('测试用例执行通过')