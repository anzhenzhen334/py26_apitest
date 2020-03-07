"""
============================
Author:ann
Date:2020/3/7
Time:11:28
E-mail:326329411@qq.com
Mobile:15821865916
============================
"""
import unittest
import os
import random
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
class TestMainStream(unittest.TestCase):
    excel = ReadWriteExcel(case_file, "main_stream")
    cases = excel.read_excel()
    request = HandlerRequests()

    @data(*cases)
    def test_main_stream(self, case):
        # 第一步：准备用例数据
        url = conf.get("env", "base_url") + replace_data(case["url"])
        method = case["method"]
        if case["interface"] == "register":
            # 注册接口，则随机生成一个手机号码
            CaseData.mobilephone = self.random_phone()
        data = eval(replace_data(case["data"]))
        headers = eval(conf.get("env", "headers"))

        # 判断是否是登录接口，不是登录接口则需要添加token
        if case["interface"] != "login" and case["interface"] != "register":
            headers['Authorization'] = getattr(CaseData, 'token_value')
            # headers["Authorization"] = getattr(CaseData, "token_value")
            # 在请求体中加入，时间戳和签名
            sign_info = HandleSign.generate_sign(getattr(CaseData, "token"))
            data.update(sign_info)

        expected = eval(case["expected"])
        row = case["case_id"] + 1
        # 第二步：发送请求，获取结果
        print("请求参数：", data)
        response = self.request.send_request(url=url, method=method, json=data, headers=headers)
        res = response.json()
        print("预期结果", expected)
        print("实际结果", res)
        # 发送请求后，判断是否是登陆接口
        if case["interface"].lower() == "login":
            # 提取用户id保存为类属性
            CaseData.member_id = str(jsonpath.jsonpath(res, "$..id")[0])
            token = jsonpath.jsonpath(res, "$..token")[0]
            token_type = jsonpath.jsonpath(res, "$..token_type")[0]
            # 提取token,保存为类属性
            CaseData.token_value = token_type + " " + token
            CaseData.token = token
        # 判断是否是加标的用例，如果是的则请求标id
        if case["interface"] == "add":
            CaseData.loan_id = str(jsonpath.jsonpath(res, "$..id")[0])
        # 第三步：断言（比对预期结果和实际结果）
        try:
            self.assertEqual(expected["code"], res["code"])
            self.assertIn(expected["msg"], res["msg"])
        except AssertionError as e:
            self.excel.write_excel(row=row, column=8, value="未通过")
            log.error("用例：{}，执行未通过".format(case["title"]))
            log.exception(e)
            raise e
        else:
            self.excel.write_excel(row=row, column=8, value="通过")
            log.info("用例：{}，执行未通过".format(case["title"]))

    def random_phone(self):
        phone = "139"
        n = random.randint(100000000, 999999999)
        phone += str(n)[1:]
        return phone
