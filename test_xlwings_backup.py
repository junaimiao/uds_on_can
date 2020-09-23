# Author:胡志成
# Date:2020/9/9

import xlwings as xw
from canlib import Frame, canlib

import _thread
import time

import flask_project_use_socket.app.controllers.can_message as can

import redis

import datetime

pool = redis.ConnectionPool(host = '127.0.0.1',port=6379,db=0)
r = redis.StrictRedis(connection_pool = pool)


# 初始化消息
r.set("test","stop")
r.set("status","start11")

if r.get("line_number") != None:
    r.delete("line_number")



wb = xw.Book("./uds_test2.xlsx")

sht = wb.sheets("1_1_DiagAndCommMgtFuncUnit")

number = int(sht.range("Q2").value)

print(number)

# send_data = sht.range("K11").value
# 字符串分割
# send_data = send_data.split(" ")

# print(send_data)

# for n in range(len(send_data)):
#     send_data[n] = int(send_data[n],16)


ch = can.init()

ch = can.run(ch)

# frame = Frame(id_=0x79D,
#             data=[send_data[0],send_data[1],
#              send_data[2],send_data[3], send_data[4], send_data[5], 
#              send_data[6],send_data[7]],
#             dlc=8,
#             flags=0)

# wb.close()

# for j in range(5):
#     # frame = Frame(id_=0x79D,
#     #             data=[0x02,0x10, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00],
#     #             dlc=8,
#     #             flags=0)
#     # frame = Frame(id_=0x79D,
#     #             data=[2,16, 1, 0, 0, 0, 0, 0],
#     #             dlc=8,
#     #             flags=0)
#     ch.write(frame)
#     for k in range(5):
#         frame = ch.read(timeout=500)
#         if frame.id == 0x7dd:
#             print("{id:02x}  {dlc}  {data}  {timestamp}".format(
#                 id=frame.id,
#                 dlc=frame.dlc,
#                 data=' '.join('%02x' % i for i in frame.data),
#                 timestamp=frame.timestamp
#             ))



def printMessage(threadName,ch):
    wb = xw.Book("./uds_test2.xlsx")
    sht = wb.sheets("1_1_DiagAndCommMgtFuncUnit")
    while True:
        frame = ch.read(timeout=500)
        if frame.id == 0x7dd:
            # 向发送线程设置发送等待消息
            r.set("status","wait")
            line_number = str(r.get("line_number"),encoding="utf8")
            print("{id:02x}  {dlc}  {data}  {timestamp}".format(
                    id=frame.id,
                    dlc=frame.dlc,
                    data=' '.join('%02x' % i for i in frame.data),
                    timestamp=frame.timestamp
                ))
            time.sleep(1)
            # 对接收到的数据data转化成数据串
            data = str("{data}".format(
                    data=' '.join('%02x' % i for i in frame.data)
                ))
            # 表格单元格赋值
            sht.range("%s%s" % ("N",line_number)).value = data
            # 分割刚转换的字符串数据，方便后期判断
            data = data.split(" ")
            if data[1] == "50":
                sht.range("%s%s" % ("L",line_number)).value = "肯定响应"
                sht.range("%s%s" % ("M",line_number)).value = "-"
                sht.range("%s%s" % ("O",line_number)).value = "OK"
                sht.range("%s%s" % ("P",line_number)).value = "huzhicheng"
                sht.range("%s%s" % ("Q",line_number)).value = datetime.date.today()
            print(data)
            time.sleep(1)
            # 将数据保存到表格
            wb.save()
            # 向发送线程设置发送开始消息
            r.set("status","%s%s" % ("start",str(int(line_number)+1)))
            # wb.close()
        # print("执行中")

def sendMessage(threadName,ch,number):
    wb = xw.Book("./uds_test2.xlsx")
    sht = wb.sheets("1_1_DiagAndCommMgtFuncUnit")
    # 初始化开始行数
    i = 11
    # send_data = sht.range("K11").value
    # for n in range(len(send_data)):
    #     send_data[n] = int(send_data[n],16)
    while i < 11 + number:
        if str(r.get("test"),encoding="utf8") == "start":
            if str(r.get("status"),encoding="utf8") == "%s%s" % ("start",str(i)):
                # 向第一个线程传递当前行数值
                r.set("line_number",str(i))
                send_data = sht.range("%s%s" % ("k",str(i))).value
                send_data = send_data.split(" ")
                for n in range(len(send_data)):
                    send_data[n] = int(send_data[n],16)
                frame = Frame(id_=0x79D,
                        data=[send_data[0],send_data[1],
                            send_data[2],send_data[3], send_data[4], send_data[5], 
                            send_data[6],send_data[7]],
                        dlc=8,
                        flags=0)
                ch.write(frame)
                i = i + 1
                # r.set("test","stop")
    r.set("test","stop")
    # r.delete("line_number")

try:
    _thread.start_new_thread(printMessage,("thread1",ch))
    _thread.start_new_thread(sendMessage,("thread2",ch,number))
    pass
except:
    print("线程启动错误")
    ch.busOff()
    ch.close()

while True:
    pass

# ch.busOff()
# ch.close()