"""
============================
Author:ann
Date:2020/3/5
Time:14:19
E-mail:326329411@qq.com
Mobile:15821865916
============================
"""
import unittest
import os
import random
from library.ddt import ddt,data
from common.read_write_excel import ReadWriteExcel
from common.handlerpath import DATA_DIR
from common.handlerconfig import conf
from common.handlerrequests import HandlerRequests
from common.handlerlog import log
from common.connectdb import DB
from common.handlerdata import CaseData,replace_data

case_file = os.path.join(DATA_DIR,'apicases.xlsx')

@ddt
class TestRegister(unittest.TestCase):
    excel = ReadWriteExcel(case_file,'register')
    cases = excel.read_excel()
    request = HandlerRequests()
    db = DB()

    @data(*cases)
    def test_register(self,case):
        url = conf.get('env','base_url') + case['url']
        method = case['method']

        CaseData.phone = self.random_phone()
        case['data'] = replace_data(case['data'])
        data = eval(case['data'])
        print('测试用例中data的值是：',data)

        expected = eval(case['expected'])
        headers = eval(conf.get('env','headers'))

        row = case['case_id'] + 1

        response = self.request.send_request(url=url,method=method,json=data,headers=headers)
        res = response.json()
        print('注册-测试用例执行结果：',res)

        try:
            self.assertEqual(res['code'],expected['code'])
            # self.assertEqual(res['msg'],expected['msg'])
            sql = 'select count(*) from futureloan.member where mobile_phone={}'.format(getattr(CaseData,'phone'))
            table_res = self.db.find_count(sql)
            if case['check_sql']:
                self.assertEqual(table_res,1)
        except Exception as e:
            self.excel.write_excel(row=row,column=8,value='未通过')
            log.error('测试用例{}执行未通过'.format(case['title']))
            log.exception(e)
            raise e
        else:
            self.excel.write_excel(row=row,column=8,value='通过')
            log.info('测试用例{}执行通过'.format(case['title']))

    def random_phone(self):
        phone = '138'
        n = random.randint(100000000,999999999)
        phone += str(n)[1:]

        return phone
        # sql = 'select count(*) from futureloan.member where mobile_phone={}'.format(phone)
        # result = self.db.find_count(sql)
        # if result:
        #     phone = self.random_phone()
        #     return phone
        # else:
        #     return phone


