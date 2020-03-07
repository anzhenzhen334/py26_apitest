"""
============================
Author:ann
Date:2020/2/23
Time:13:02
E-mail:326329411@qq.com
Mobile:15821865916
============================
"""
import logging
from common.handlerpath import LOG_DIR
import os
# import datetime
from common.handlerconfig import conf



class HandlerLog(object):
    @staticmethod
    def create_logger():
        mylog = logging.getLogger('ann')
        mylog.setLevel(conf.get('log','level'))

        sh = logging.StreamHandler()
        sh.setLevel(conf.get('log','sh_level'))

        # log_name = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '.log'
        fh = logging.FileHandler(filename=os.path.join(LOG_DIR, 'py26_futureloan_apitest.log'), encoding='utf8')
        fh.setLevel(conf.get('log','fh_level'))

        mylog.addHandler(sh)
        mylog.addHandler(fh)

        formater = '%(asctime)s - [%(filename)s-->line:%(lineno)d] - %(levelname)s: %(message)s'
        fm = logging.Formatter(formater)

        sh.setFormatter(fm)
        fh.setFormatter(fm)

        return mylog


log = HandlerLog.create_logger()
