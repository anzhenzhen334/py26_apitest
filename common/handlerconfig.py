"""
============================
Author:ann
Date:2020/2/23
Time:13:02
E-mail:326329411@qq.com
Mobile:15821865916
============================
"""
from configparser import ConfigParser
import os
from common.handlerpath import CONF_DIR


class HandlerConfig(ConfigParser):
    def __init__(self, file_name):
        super().__init__()
        self.file_name = file_name
        self.read(file_name, encoding='utf8')

    def write_config(self, section, option, value):
        self.set(section=section, option=option, value=value)
        self.write(fp=open(self.file_name, 'wb'))


conf = HandlerConfig(os.path.join(CONF_DIR, 'config.ini'))