"""
============================
Author:ann
Date:2020/3/6
Time:14:57
E-mail:326329411@qq.com
Mobile:15821865916
============================
"""
"""
投资接口：
1、需要有标：管理员登录，加标、审核，
2、用户登录
3、投资用例的执行

# 关于投资的sql校验语句
1、用户表、校验用户余额是否发生变化，变化金额等于所投金额（根据用户id去查member表）
SELECT * FROM futureloan.member WHERE id={}
2、根据用户id和标id去投资表中查用户的投资记录，（invest里面查用户对应的标是否新增一条记录）
SELECT * FROM futureloan.invest WHERE member_id={} and loan_di={}
3、根据用户id去流水标中查询流水记录（查询用户投资之后是否多了一条记录）
SELECT * FROM future.financelog WHERE pay_member_id={}
4、在刚好投满的情况下，可以根据投资记录的id，去回款计划表中查询是否，生成回款计划。
SELECT * FROM future.repayment WHERE invest_id={}
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
class TestInvest(unittest.TestCase):
    excel = ReadWriteExcel(case_file,'invest2')
    cases = excel.read_excel()
    request = HandlerRequests()
    db = DB()

    @data(*cases)
    def test_invest(self,case):
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

        # 关于sql校验：需要校验投资用户可用余额减少（sql1）、需要校验流水记录表中增加了一条记录
        if case['check_sql']:
            sql1 = "select * from futureloan.member where id={}".format(getattr(CaseData,'member_id'))
            start_amount = self.db.find_one(sql1)['leave_amount']
            print('执行投资前的用户余额时：',start_amount)
            sql2 = "select * from futureloan.financeLog where pay_member_id={}".format(getattr(CaseData,'member_id'))
            start_sum = self.db.find_count(sql2)
            print("执行投资前流水记录表中的数量是：",start_sum)
            sql3 = "SELECT * FROM futureloan.invest WHERE member_id={} and loan_id={}".format(CaseData.member_id,CaseData.loan_id)
            start_invest = self.db.find_count(sql3)
            print('投资前的投资记录条数：',start_invest)

        response = self.request.send_request(url=url,method=method,json=data,headers=headers)
        res = response.json()
        print('执行接口后的结果是：',res)

        if case['interface'] == 'login':
            token_type = jsonpath.jsonpath(res,'$..token_type')[0]
            token = jsonpath.jsonpath(res,'$..token')[0]
            member_id = str(jsonpath.jsonpath(res,'$..id')[0])

            token_value = token_type + ' ' + token
            CaseData.token_value = token_value
            CaseData.member_id = member_id
            CaseData.token = token
        if case['interface'] == 'add':
            loan_id = str(jsonpath.jsonpath(res,'$..id')[0])
            CaseData.loan_id = loan_id

        if case['check_sql']:
            sql = "select * from futureloan.member where id={}".format(getattr(CaseData,'member_id'))
            end_amount = self.db.find_one(sql)['leave_amount']
            print('执行投资后的用户余额时：',end_amount)
            sql2 = "select * from futureloan.financeLog where pay_member_id={}".format(getattr(CaseData, 'member_id'))
            end_sum = self.db.find_count(sql2)
            print("执行投资后流水记录表中的数量是：", end_sum)
            sql3 = "SELECT * FROM futureloan.invest WHERE member_id={} and loan_id={}".format(CaseData.member_id,CaseData.loan_id)
            end_invest = self.db.find_count(sql3)
            print('投资后的投资记录条数：', end_invest)

        try:
            self.assertEqual(res['code'],expected['code'])
            # self.assertEqual(res['msg'],expected['msg'])
            if case['check_sql']:
                self.assertEqual(start_amount-end_amount,Decimal(str(data['amount'])))
                self.assertEqual(end_sum-start_sum,1)
                self.assertEqual(end_invest-start_invest,1)
                # 关于sql校验：除了以上校验外，如果达到满标（即投资额=用户可用余额，那么在回款计划表中会新增一条记录）
                # if end_amount == data['amount']:
                #     sql3 = 'select * from futureloan.repayment where invest_id={}'.format(getattr(CaseData, 'member_id'))
                #     repay_amount = self.db.find_count(sql3)
                #     self.assertEqual(repay_amount,1)
                if "满标" in case["title"]:
                    # 获取当前标所有的投资记录id
                    sql4 = "SELECT id FROM futureloan.invest WHERE loan_id={}".format(CaseData.loan_id)
                    invest_ids = self.db.find_all(sql4)
                    # 遍历该标所有的投资记录，id
                    for invest in invest_ids:
                        sql5 = "SELECT * FROM futureloan.repayment WHERE invest_id={}".format(invest["id"])
                        # 获取当前这条投资记录，生成对应的回款
                        count = self.db.find_count(sql5)
                        # 断言查询到的条数的布尔值是否为True(0的布尔值是Flase,只要不是0条，这个断言就会通过)
                        self.assertTrue(count)
        except Exception as e:
            self.excel.write_excel(row=row,column=8,value='未通过')
            log.error('测试用例{}执行未通过'.format(case['title']))
            log.exception(e)
            raise e
        else:
            self.excel.write_excel(row=row,column=8,value='通过')
            log.info('测试用例{}执行通过'.format(case['title']))