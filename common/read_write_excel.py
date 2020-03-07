"""
============================
Author:ann
Date:2020/2/23
Time:13:03
E-mail:326329411@qq.com
Mobile:15821865916
============================
"""
import openpyxl
# from common.handlerpath import DATA_DIR
# import os

class ReadWriteExcel(object):
    def __init__(self, file_name, sheet_name):
        self.file_name = file_name
        self.sheet_name = sheet_name

    def open(self):
        self.wb = openpyxl.load_workbook(self.file_name)
        self.sh = self.wb[self.sheet_name]

    def read_excel(self):
        self.open()
        data = list(self.sh.rows)
        cases = []
        title = [i.value for i in data[0]]
        for i in data[1:]:
            value = [c.value for c in i]
            dic = dict(zip(title, value))
            cases.append(dic)
        return cases

    def write_excel(self, row, column, value):
        self.open()
        self.sh.cell(row=row, column=column, value=value)
        self.wb.save(self.file_name)

# execl = ReadWriteExcel(os.path.join(DATA_DIR,'apicases.xlsx'),'register')
# res = execl.read_excel()
# print(res)