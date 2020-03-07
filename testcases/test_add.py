"""
============================
Author:ann
Date:2020/3/6
Time:11:30
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
class TestAdd(unittest.TestCase):
    excel = ReadWriteExcel(case_file,'add')
    cases = excel.read_excel()
    request = HandlerRequests()
    db = DB()

    @data(*cases)
    def test_add(self,case):
        """
        将登录放在测试用例excel的第一行，根据接口类型，判断如果是登录，那么获取其响应结果中的token_value
        :param case:
        :return:
        """
        url = conf.get('env','base_url') + case['url']
        method = case['method']

        headers = eval(conf.get('env', 'headers'))

        if  case['interface'] != 'login':
            headers['Authorization'] = getattr(CaseData,'token_value')

        case['data'] = replace_data(case['data'])
        data = eval(case['data'])

        if case['interface'] != 'login':
            sign_info = HandleSign.generate_sign(getattr(CaseData, "token"))
            data.update(sign_info)
            # 在请求体中加入，时间戳和签名

        print('测试用例中data的值是：',data)
        expected = eval(case['expected'])
        row = case['case_id'] + 1

        if case['check_sql']:
            case['check_sql'] = replace_data(case['check_sql'])
            sql = case['check_sql']
            result = self.db.find_count(sql)
            start_sum = result
            print('执行添加项目前的总项目数是：',start_sum)

        response = self.request.send_request(url=url,method=method,json=data,headers=headers)
        res = response.json()
        print('执行接口后的结果是：',res)

        if case['interface'] == 'login':
            token_type = jsonpath.jsonpath(res,'$..token_type')[0]
            token = jsonpath.jsonpath(res,'$..token')[0]
            member_id = str(jsonpath.jsonpath(res,'$..id')[0])

            token_value = token_type + ' ' + token
            CaseData.token = token
            CaseData.token_value = token_value
            CaseData.member_id = member_id

        if case['check_sql']:
            case['check_sql'] = replace_data(case['check_sql'])
            sql = case['check_sql']
            result = self.db.find_count(sql)
            end_sum = result
            print('执行添加项目后的总项目数是：',end_sum)

        try:
            self.assertEqual(res['code'],expected['code'])
            # self.assertEqual(res['msg'],expected['msg'])
            if case['check_sql']:
                self.assertEqual(end_sum-start_sum,1)
        except Exception as e:
            self.excel.write_excel(row=row,column=8,value='未通过')
            log.error('测试用例{}执行未通过'.format(case['title']))
            log.exception(e)
            raise e
        else:
            self.excel.write_excel(row=row,column=8,value='通过')
            log.info('测试用例{}执行通过'.format(case['title']))