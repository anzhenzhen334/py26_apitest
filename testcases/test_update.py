"""
============================
Author:ann
Date:2020/3/3
Time:10:52
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
from common.handlerdata import CaseData,replace_data
from common.handle_sign import HandleSign

case_file = os.path.join(DATA_DIR, "apicases.xlsx")
@ddt
class TestUpdate(unittest.TestCase):
    excel = ReadWriteExcel(case_file, "update")
    cases = excel.read_excel()
    request = HandlerRequests()
    db = DB()

    @classmethod
    def setUpClass(cls):
        url = conf.get('env', 'base_url') + '/member/login'
        data = {
            'mobile_phone': conf.get('test_data', 'mobile_phone'),
            'pwd': conf.get('test_data', 'pwd')
        }
        headers = eval(conf.get('env', 'headers'))

        response = cls.request.send_request(url=url, json=data, headers=headers, method='post')
        res = response.json()
        token = jsonpath.jsonpath(res, '$..token')
        token_type = jsonpath.jsonpath(res, '$..token_type')
        CaseData.token = token[0]
        CaseData.token_value = token_type[0] + ' ' + token[0]
        CaseData.member_id = str(jsonpath.jsonpath(res, '$..id')[0])

    @data(*cases)
    def test_update(self, case):
        url = conf.get('env','base_url')+case['url']
        method= case['method']
        case['data'] = replace_data(case['data'])
        data = eval(case['data'])
        # 在请求体中加入，时间戳和签名
        sign_info = HandleSign.generate_sign(getattr(CaseData, "token"))
        data.update(sign_info)
        # print('data中reg_name的值是',data['reg_name'],type(data['reg_name']))
        headers=eval(conf.get('env','headers'))
        headers['Authorization'] = getattr(CaseData,'token_value')
        expected = eval(case["expected"])
        row = case["case_id"] + 1

        response=self.request.send_request(url=url,method=method,json=data,headers=headers)
        res = response.json()
        print('更新昵称接口返回的结果：',res)
        try:
            self.assertEqual(res['code'],expected['code'])
            if case['check_sql']:
                sql = 'select * from futureloan.member where mobile_phone={}'.format(conf.get('test_data','mobile_phone'))
                res_name = self.db.find_one(sql)['reg_name']
                # print('执行后结果昵称是：',res_name,type(res_name))
                self.assertEqual(res_name,data['reg_name'])
        except Exception as e:
            self.excel.write_excel(row=row,column=8,value='未通过')
            log.error('测试用例{}执行未通过'.format(case['title']))
            log.exception(e)
            raise e
        else:
            self.excel.write_excel(row=row,column=8,value='通过')
            log.info('测试用例执行通过')