"""
Author:胡志成
Date:2020/9/10
ModificationDate:2020/9/16

note:1.该代码使用了多线程处理，线程之间的同步和消息传递使用redis
       数据库实现
     2.该脚本是自动化诊断脚本

消息功能表
| 消息名 | 功能              |   值       |
| ------|-------------------|------------|
| test | 启动读excel并发送包 | start/stop |
| status | 标志发送的报文所在行(例:start11->发送第11行上的报文) |  ->用于使两个线程交叉处理数据
| line_number | 保存当前发送的报文所在行 | 11~11+number |        ->用于使两个线程交叉处理数据
| service_number | 保存当前发送的服务号(例10服务为10) |  |
| service_subfunction | 保存当前发送的服务号的子功能(例10 02为02) |  |
| print_message_status | 接收并打印包数据的开启和关闭状态 | start/stop |
| receive_flow_control_flag | 接收到ECU发送的流控帧设置该信息为1 | 1/0 |
| diagnostic_status | 通知web诊断结束 | finish |
"""
import sys
# 处理excel的库
import xlwings as xw
# kvaser can通信库
from canlib import Frame, canlib
# 线程库
import threading
# 时间库
import time
# 自封装的can通信函数库文件
import controllers.can_message as can
# 自封装UDS服务库
from controllers.uds_lib import UdsLib
# redis数据库
import redis
# 日期库
import datetime

# 脚本初始化函数
def init(excel_name,sheet_name):
    # 第一次开始行数变量
    start_line_number = 11

    # 初始化消息
    r.set("test","stop")# 发送线程开始消息
    # r.set("status","start11")# 线程同步消息，线程交叉执行
    r.set("status","%s%s"%("start",str(start_line_number)))# 线程同步消息，线程交叉执行
    r.set("print_message_status","start")
    r.set("receive_flow_control_flag",0)
    # 判断数据库中有没有line_number数据，若有，先删除
    if r.get("line_number") != None:
        r.delete("line_number")

    if r.get("service_number") != None:
        r.delete("service_number")
    
    if r.get("service_subfunction") != None:
        r.delete("service_subfunction")

    try:
        # 实例化excel文件处理对象
        wb = xw.Book(excel_name)
        # 实例化具体的表格对象
        sht = wb.sheets(sheet_name)
        # 获取该表格的设置的用例数
        # number = int(sht.range("Q2").value)
    except:
        print("初始化读取excel表格错误")
        sys.exit(1)
    # 获取当天日期
    date_today = datetime.date.today()

    # print(number)
    # 初始化can通讯和运行can通讯
    try:
        ch = can.init()
        ch = can.run(ch)
    except:
        print("can卡启动错误")
        sys.exit(-1)

    return [wb,sht,date_today,ch,start_line_number]

# 打印can数据和向excel表格中保存诊断数据
def printMessage(threadName,ch,physical_id = 0x79D,function_id = 0x760,excel_name=None,sheet_name=None):
    # 这个对象需要重新实例化
    wb = xw.Book(excel_name)
    sht = wb.sheets(sheet_name)
    # 保存接收到的不同的包地址的集合
    different_can_message_address_by_receive = set()
    # 初始化一个空字典，用于保存间隔时间计算结果
    init_dic = {}
    # 实例化uds服务对象
    uds = UdsLib(ch=ch,id=physical_id)
    while True:
        # 启动信号
        if str(r.get("print_message_status"),encoding="utf-8") == "start":
            try:
                frame = ch.read(timeout=500)
            except:
                # print("can通讯异常")
                ch = can.init()
                ch = can.run(ch)
                continue
                # break
            # print("{id:02x}  {dlc}  {data}  {timestamp}".format(
            #             id=frame.id,
            #             dlc=frame.dlc,
            #             data=' '.join('%02x' % i for i in frame.data),
            #             timestamp=frame.timestamp
            #         ))
            # 接收到响应报文
            if frame.id == response_id:
                # 向发送线程设置发送等待消息
                r.set("status","wait")
                line_number = str(r.get("line_number"),encoding="utf-8")
                # print("{id:02x}  {dlc}  {data}  {timestamp}".format(
                #         id=frame.id,
                #         dlc=frame.dlc,
                #         data=' '.join('%02x' % i for i in frame.data),
                #         timestamp=frame.timestamp
                #     ))
                # time.sleep(1)
                # 对接收到的数据data转化成数据串
                data = str("{data}".format(
                        data=' '.join('%02x' % i for i in frame.data)
                    ))
                # 表格单元格赋值
                sht.range("%s%s" % (current_sheet_table_title_dic["响应数据"],line_number)).value = data
                # 分割刚转换的字符串数据，方便后期判断
                data = data.split(" ")
                # uds服务
                check_result = uds.check_message_status(int(str(r.get("service_number"),encoding="utf-8")),data)
                if check_result:
                    if int(data[1],16) == 0x67 and int(data[2],16) % 2 == 1:
                        # 判断接收到了27服务请求种子的肯定响应
                        sht.range("%s%s" % (current_sheet_table_title_dic["响应方式"],line_number)).value = "肯定响应"
                        sht.range("%s%s" % (current_sheet_table_title_dic["故障码类型"],line_number)).value = "-"
                        sht.range("%s%s" % (current_sheet_table_title_dic["OK/NG"],line_number)).value = "OK"
                        sht.range("%s%s" % (current_sheet_table_title_dic["测试人员"],line_number)).value = "huzhicheng"
                        sht.range("%s%s" % (current_sheet_table_title_dic["测试时间"],line_number)).value = date_today
                        # 将数据保存到表格
                        wb.save()
                        # 种子数组
                        seed = []
                        seed.append(int(data[3],16))
                        seed.append(int(data[4],16))
                        seed.append(int(data[5],16))
                        seed.append(int(data[6],16))
                        print("seed:",seed)
                        ch.write(uds.security_access_calculate_key(id=physical_id,seed=seed))
                    elif int(data[1],16) == 0x67 and int(data[2],16) % 2 == 0:
                        # 判断接收到了解锁肯定响应
                        sht.range("%s%s" % (current_sheet_table_title_dic["备注"],line_number)).value = "解锁成功"
                        # 将数据保存到表格
                        wb.save()
                        # 向发送线程设置下一个报文发送开始消息
                        r.set("status","%s%s" % ("start",str(int(line_number)+1)))
                    elif uds.continuous_status == True and int(data[0],16) & 0x0F == uds.TP.continuous_frame_number:
                        # 判断检测到连续帧的最后一帧,执行不同的保存数据内容
                        sht.range("%s%s" % (current_sheet_table_title_dic["响应方式"],line_number)).value = "肯定响应"
                        sht.range("%s%s" % (current_sheet_table_title_dic["故障码类型"],line_number)).value = "-"
                        sht.range("%s%s" % (current_sheet_table_title_dic["OK/NG"],line_number)).value = "OK"
                        sht.range("%s%s" % (current_sheet_table_title_dic["测试人员"],line_number)).value = "huzhicheng"
                        sht.range("%s%s" % (current_sheet_table_title_dic["测试时间"],line_number)).value = date_today
                        sht.range("%s%s" % (current_sheet_table_title_dic["响应数据"],line_number)).value = str(uds.TP.continuous_data)
                        print("continuous_data:",uds.TP.continuous_data)
                        print("continuous_data_number",uds.TP.continuous_data_number)
                        print("continuous_frame_number",uds.TP.continuous_frame_number)
                        # 将数据保存到表格
                        wb.save()
                        # 向发送线程设置下一个报文发送开始消息
                        r.set("status","%s%s" % ("start",str(int(line_number)+1)))
                        # 重置连续帧标志
                        uds.continuous_status = False
                        # 重置uds.TP.continuous_data
                        uds.TP.continuous_data = []
                        pass
                    elif not uds.continuous_status:
                        # 一般的肯定响应
                        sht.range("%s%s" % (current_sheet_table_title_dic["响应方式"],line_number)).value = "肯定响应"
                        sht.range("%s%s" % (current_sheet_table_title_dic["故障码类型"],line_number)).value = "-"
                        sht.range("%s%s" % (current_sheet_table_title_dic["OK/NG"],line_number)).value = "OK"
                        sht.range("%s%s" % (current_sheet_table_title_dic["测试人员"],line_number)).value = "huzhicheng"
                        sht.range("%s%s" % (current_sheet_table_title_dic["测试时间"],line_number)).value = date_today
                        # 将数据保存到表格
                        wb.save()
                        # 向发送线程设置下一个报文发送开始消息
                        r.set("status","%s%s" % ("start",str(int(line_number)+1)))
                elif uds.NRC == 0x78:
                    uds.NRC = None
                    time.sleep(0.01)# 等待10ms
                elif int(data[1],16) == 0x7f:
                    sht.range("%s%s" % (current_sheet_table_title_dic["响应方式"],line_number)).value = "否定响应"
                    sht.range("%s%s" % (current_sheet_table_title_dic["故障码类型"],line_number)).value = "-"
                    sht.range("%s%s" % (current_sheet_table_title_dic["OK/NG"],line_number)).value = "OK"
                    sht.range("%s%s" % (current_sheet_table_title_dic["测试人员"],line_number)).value = "huzhicheng"
                    sht.range("%s%s" % (current_sheet_table_title_dic["测试时间"],line_number)).value = date_today
                    sht.range("%s%s" % (current_sheet_table_title_dic["故障码类型"],line_number)).value = uds.NRC_table[uds.NRC]
                    # 将数据保存到表格
                    wb.save()
                    # 向发送线程设置下一个报文发送开始消息
                    r.set("status","%s%s" % ("start",str(int(line_number)+1)))
                else:#既不是肯定响应也不是否定响应
                    # 判断s是否接收到ECU发来的流控帧
                    [flow_control_flag,flow_state,block_size,STmin] = uds.TP.check_flow_control_frame(data)
                    if flow_control_flag:# 判断检测到流控帧
                        r.set("receive_flow_control_flag",1)
                # 打印响应报文
                print("{id:02x}  {dlc}  {data}  {timestamp}".format(
                        id=frame.id,
                        dlc=frame.dlc,
                        data=' '.join('%02x' % i for i in frame.data),
                        timestamp=frame.timestamp
                    ))
                # wb.close()
            # print("执行中")
            else:
                """
                第一种使用time库计算报文间隔时间的方法，该方法不怎么准
                """
                # 以下代码用于计算包间隔时间
                # id = "{id:02x}".format(id = frame.id)
                # if id not in different_can_message_address_by_receive:
                #     # 将包id字符串添加入different_can_message_address_by_receive集合中
                #     different_can_message_address_by_receive.add(id)
                #     begin_time = time.time()
                #     dic = {"begin_time":begin_time,"run_time":0.0}
                #     init_dic[id] = dic
                # # elif float(str(r.hget(id,"run_time"),encoding="utf8")) == 0.0:
                # elif init_dic[id]["run_time"] == 0.0:
                #     end_time = time.time()
                #     run_time = end_time - init_dic[id]["begin_time"]
                #     init_dic[id]["run_time"] = run_time
                # print(init_dic)
                """
                第二种使用接收到包的时间戳计算报文间隔时间的方法，建议使用该方法
                """
                id = "{id:02x}".format(id = frame.id)
                if id not in different_can_message_address_by_receive:
                    # 将包id字符串添加入different_can_message_address_by_receive集合中
                    different_can_message_address_by_receive.add(id)
                    dic = {"begin_time":float("{timestamp}".format(timestamp = frame.timestamp)),"run_time":0.0}
                    init_dic[id] = dic
                elif init_dic[id]["run_time"] == 0.0:
                    run_time = float("{timestamp}".format(timestamp = frame.timestamp)) - init_dic[id]["begin_time"]
                    init_dic[id]["run_time"] = run_time
                    print(init_dic)
                # print("{id:02x}  {dlc}  {data}  {timestamp}".format(
                #         id=frame.id,
                #         dlc=frame.dlc,
                #         data=' '.join('%02x' % i for i in frame.data),
                #         timestamp=frame.timestamp
                #     ))
        else:
            break


# 读取excel中的数据并发送can报文
def sendMessage(threadName,ch,number,start_line_number = 11,physical_id = 0x79D,function_id = 0x760,excel_name=None,sheet_name=None):
    # 这个对象需要重新实例化
    wb = xw.Book(excel_name)
    sht = wb.sheets(sheet_name)
    # 初始化发送包当前时间
    send_frame_time = 0.0
    # 实例化UDS服务对象
    uds = UdsLib(id=physical_id,ch=ch)
    # 初始化开始行数
    i = start_line_number
    while i < start_line_number + number:
        if str(r.get("test"),encoding="utf8") == "start":
            if str(r.get("status"),encoding="utf8") == "%s%s" % ("start",str(i)):
                try:
                    # 读取测试用例中当前会话状态，并主动发送会话切换报文，以确保当前实际会话状态为用例要求的状态
                    if sht.range("%s%s" % (current_sheet_table_title_dic["会话状态"],str(i))).value == "默认会话":
                        ch.write(uds.session(id=physical_id,sub_function=0x81))
                        time.sleep(0.01)
                    elif sht.range("%s%s" % (current_sheet_table_title_dic["会话状态"],str(i))).value == "扩展会话":
                        ch.write(uds.session(id=physical_id,sub_function=0x81))
                        time.sleep(0.01)
                        ch.write(uds.session(id=physical_id,sub_function=0x83))
                        time.sleep(0.01)
                    elif sht.range("%s%s" % (current_sheet_table_title_dic["会话状态"],str(i))).value == "编程会话":
                        ch.write(uds.session(id=physical_id,sub_function=0x81))
                        time.sleep(0.1)
                        ch.write(uds.session(id=physical_id,sub_function=0x83))
                        time.sleep(0.01)# 等待10ms
                        ch.write(uds.session(id=physical_id,sub_function=0x82))
                        time.sleep(0.02)# 等待20ms
                except:
                    print("can通讯异常")
                    break
                # 根据测试用例设置当前使用物理地址还是功能地址
                if sht.range("%s%s" % (current_sheet_table_title_dic["请求方式"],str(i))).value == "物理请求":
                    current_id = physical_id
                else:
                    current_id = function_id

                print("current_id:",current_id)
                # 向第一个线程传递当前行数值
                r.set("line_number",str(i))
                send_data = sht.range("%s%s" % (current_sheet_table_title_dic["Data"],str(i))).value
                send_data = send_data.strip().split(" ") # 去除字符串前后空格并分割成数组
                print(send_data)
                for n in range(len(send_data)):
                    send_data[n] = int(send_data[n],16)
                # 保存service_number
                r.set("service_number",send_data[1])
                # 保存子功能号
                # r.set("service_subfunction",send_data[2])
                if send_data[0] & 0xF0 == 0x10:
                    # 保存service_number,如果是连续帧首帧，service_number是第三个字节
                    r.set("service_number",send_data[2])
                    frame_data = []
                    # 帧个数
                    frame_number = int(len(send_data)/8)
                    # 将数据分帧
                    for j in range(frame_number):
                        offset = j*8
                        frame_data.append([send_data[0+offset],send_data[1+offset],
                                        send_data[2+offset],send_data[3+offset],
                                        send_data[4+offset],send_data[5+offset],
                                        send_data[6+offset],send_data[7+offset]])
                    # 发送首帧
                    send_frame_time = time.time() # 发送该报文的程序时间
                    ch.write(Frame(id_=current_id,data=frame_data[0],dlc=8,flags=0))
                    # 等待接收到的流控信息
                    while True:
                        # 接收到流控消息，跳出等待
                        if int(str(r.get("receive_flow_control_flag"),encoding="utf-8")):
                            break
                        break
                    # 连续发送后续帧
                    for j in range(frame_number - 1):
                        send_frame_time = time.time() # 发送该报文的程序时间
                        ch.write(Frame(id_=current_id,data=frame_data[j+1],dlc=8,flags=0))
                        time.sleep(0.005)# 等待5ms
                    # 重置接收到流控消息标志
                    r.set("receive_flow_control_flag",0)
                else:
                    frame = Frame(id_=current_id,
                            data=[send_data[0],send_data[1],
                                send_data[2],send_data[3], send_data[4], send_data[5], 
                                send_data[6],send_data[7]],
                            dlc=8,
                            flags=0)
                    try:
                        # 当检测到需要切换到编程会话时，先进入默认，后进去扩展，最后进入编程会话
                        # if send_data[1] == 0x10 and send_data[2] == 0x02:
                        #     ch.write(uds.session(id=physical_id,sub_function=0x81))
                        #     time.sleep(0.1)
                        #     ch.write(uds.session(id=physical_id,sub_function=0x83))
                        #     time.sleep(0.1)# 等待100ms
                        send_frame_time = time.time() # 发送该报文的程序时间
                        ch.write(frame)
                    except:
                        print("can通讯异常")
                        break
                # 下一行
                i += 1
                # r.set("test","stop")
            else:
                receive_response_time = time.time() # 未接收到响应报文的时间
                if receive_response_time - send_frame_time > 30.0:
                    # 超时判断为无响应
                    sht.range("%s%s" % (current_sheet_table_title_dic["响应方式"],str(i-1))).value = "无响应"
                    sht.range("%s%s" % (current_sheet_table_title_dic["故障码类型"],str(i-1))).value = "-"
                    sht.range("%s%s" % (current_sheet_table_title_dic["OK/NG"],str(i-1))).value = "OK"
                    sht.range("%s%s" % (current_sheet_table_title_dic["测试人员"],str(i-1))).value = "huzhicheng"
                    sht.range("%s%s" % (current_sheet_table_title_dic["测试时间"],str(i-1))).value = date_today
                    sht.range("%s%s" % (current_sheet_table_title_dic["响应数据"],str(i-1))).value = "-"
                    # 设置开始发送下一行报文的消息
                    r.set("status","%s%s" % ("start",str(i)))
    # r.set("test","stop")
    # r.delete("line_number")
    # 等待10s
    time.sleep(10)
    # 结束打印线程
    r.set("print_message_status","stop")

# 自定义线程类
class myThread(threading.Thread):
    def __init__(self,threadID,name,ch,number,
                start_line_number = 11,
                physical_id = 0x79D,
                function_id = 0x760,
                excel_name = None,
                sheet_name = None):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.ch = ch
        self.number = number
        self.start_line_number = start_line_number
        self.physical_id = physical_id
        self.function_id = function_id
        self.excel_name = excel_name
        self.sheet_name = sheet_name
    def run(self):
        print ("开始线程：" + self.name)
        if self.name == "printMessage":
            printMessage(self.name,self.ch,
                        physical_id=self.physical_id,
                        function_id=self.function_id,
                        excel_name=self.excel_name,
                        sheet_name=self.sheet_name)
        if self.name == "sendMessage":
            sendMessage(self.name,self.ch,self.number,
                        start_line_number=self.start_line_number,
                        physical_id=self.physical_id,
                        function_id=self.function_id,
                        excel_name=self.excel_name,
                        sheet_name=self.sheet_name)
        print ("结束线程：" + self.name)
        
# 程序开始执行的地方
if __name__ == "__main__":
    # excel_name = "./uds_test2.xlsx"
    # excel_name = sys.argv[1]

    # 连接redis数据库
    pool = redis.ConnectionPool(host = '127.0.0.1',port=6379,db=0)
    try:
        r = redis.StrictRedis(connection_pool = pool)
    except:
        print("redis数据库连接错误")
        sys.exit(1)
    
    while True:
        if r.get("excel_name") != None:
            excel_name = str(r.get("excel_name"),"utf-8")
            r.delete("excel_name")
            break


    sheet_table = ["1_1_DiagAndCommMgtFuncUnit",
                "1_2_DataTransFuncUnit",
                "1_3_StoredDataTransFuncUnit"]
    # sheet_table = ["1_3_StoredDataTransFuncUnit"]
    sheet_table_title_dic = {
        "1_1_DiagAndCommMgtFuncUnit":{
            "会话状态":"F",
            "安全状态":"G",
            "请求方式":"H",
            "Data":"K",
            "响应方式":"L",
            "故障码类型":"M",
            "响应数据":"N",
            "OK/NG":"O",
            "测试人员":"P",
            "测试时间":"Q",
            "备注":"S"
        },
        "1_2_DataTransFuncUnit":{
            "会话状态":"F",
            "安全状态":"G",
            "请求方式":"H",
            "Data":"K",
            "响应方式":"L",
            "故障码类型":"M",
            "响应数据":"N",
            "OK/NG":"O",
            "测试人员":"P",
            "测试时间":"Q",
            "备注":"S"
        },
        "1_3_StoredDataTransFuncUnit":{
            "会话状态":"F",
            "安全状态":"G",
            "请求方式":"I",
            "Data":"M",
            "响应方式":"N",
            "故障码类型":"O",
            "响应数据":"P",
            "OK/NG":"Q",
            "测试人员":"R",
            "测试时间":"S",
            "备注":"U"
        }
    }
    test_case_number_title_dic = {
        "1_1_DiagAndCommMgtFuncUnit":"Q2",
        "1_2_DataTransFuncUnit":"Q2",
        "1_3_StoredDataTransFuncUnit":"S2"
    } 
    for i in range(len(sheet_table)):# 切换不同sheet
        # 自动诊断脚本初始化(必须初始化的内容)
        # print("excel_name:%s,sheet_name:%s"%(excel_name,sheet_table[i]))
        current_sheet_table_title_dic = sheet_table_title_dic[sheet_table[i]]
        [wb,sht,date_today,ch,start_line_number] = init(excel_name,sheet_table[i])
        # 将自动切换sheet后，自动发送启动消息
        if i > 0:
            r.set("test","start")
            pass

        # excel对象需要重新实例化
        wb = xw.Book(excel_name)
        sht = wb.sheets(sheet_table[i])
        # 获取用例数
        number = int(sht.range(test_case_number_title_dic[sheet_table[i]]).value)

        physical_id = 0x79D
        function_id = 0x760
        # physical_id = 0x735 # 物理id
        # function_id = 0x7DF # 功能id
        # UDS报文响应ID
        response_id = 0x7dd
        # response_id = 0x73D
        try:
            # 创建新线程
            thread_print_message = myThread(1,"printMessage",ch,number,
                                            physical_id=physical_id,function_id=function_id,
                                            excel_name=excel_name,
                                            sheet_name=sheet_table[i])
            thread_send_message = myThread(2,"sendMessage",ch,number,
                                            start_line_number=start_line_number,
                                            physical_id=physical_id,function_id=function_id,
                                            excel_name=excel_name,
                                            sheet_name=sheet_table[i])
            # 启动线程
            thread_print_message.start()
            thread_send_message.start()

            thread_send_message.join()
            thread_print_message.join()

            ch.busOff()
            ch.close()
        except:
            print("线程启动错误")
            ch.busOff()
            ch.close()
    # 向WEB发送诊断结束消息
    r.set("diagnostic_status","finish")
