"""
============================
Author:ann
Date:2020/2/23
Time:13:03
E-mail:326329411@qq.com
Mobile:15821865916
============================
"""
import requests


class HandlerRequests(object):
    def __init__(self):
        self.session = requests.session()

    def send_request(self, url, method, headers=None, data=None, json=None, files=None, params=None):
        method = method.lower()
        if method == 'get':
            response = self.session.get(url=url, params=params, headers=headers)
        elif method == 'post':
            response = self.session.post(url=url, json=json, headers=headers, data=data, files=files)
        elif method == 'patch':
            response = self.session.patch(url=url, headers=headers, json=json, data=data, files=files)
        return response
