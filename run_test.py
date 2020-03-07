"""
============================
Author:ann
Date:2020/3/5
Time:14:12
E-mail:326329411@qq.com
Mobile:15821865916
============================
"""
import unittest
import os
from common.handler_email import send_email
from common.handlerpath import CASE_DIR,REPORT_DIR
from HTMLTestRunnerNew import HTMLTestRunner
from datetime import datetime

from BeautifulReport import BeautifulReport
# 先在cmd中pip install BeautifulReport

date = datetime.now().strftime("%Y-%m-%d")
# strftime("%Y-%m-%d %H:%M:%S")
# 按照年月日时分秒的格式展示当前时间，为后面生成报告时做区分，不使用这个的话，每次生的报告名字是一样的，就覆盖掉了

suite = unittest.TestSuite()
# 如下是根据测试用例在的路径，默认只要以test开头的用例就执行
loader = unittest.TestLoader()
suite.addTest(loader.discover(CASE_DIR))

# from testcases import test_main_stream
# loader = unittest.TestLoader()
# suite.addTest(loader.loadTestsFromModule(test_main_stream))

file_name = date + 'py26_apitest_report.html'
report_file = os.path.join(REPORT_DIR,file_name)

runner = HTMLTestRunner(stream=open(report_file,'wb'),
                        title='测试项目全接口测试报告',
                        description='futureloan项目全部接口对应的测试报告',
                        tester='ann')
runner.run(suite)


# 生成的报告比较漂亮（有饼图，可单独查看每个用例的情况，更友好）
# br = BeautifulReport(suite)
# file_name = date + 'py26_apitest_report.html'
# br.report(description='使用beautifulreport生成接口测试报告',filename=file_name,report_dir=REPORT_DIR)


send_email(filename=report_file,title='接口测试报告发送邮件-全部接口-v3校验')

