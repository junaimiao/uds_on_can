"""
Author:胡志成
Date:2020/9/11
ModificationDate:2020/9/16
note:1.该文件封装了UDS常用的服务
     2.基于kvaser设备
"""

# kvaser can通信库
from canlib import Frame, canlib
# 导入数学库
import math


class UdsLib:
    # NRC表
    NRC_table = {
        0x12:"子功能不支持（12h）",
        0x13:"报文长度错误（13h）",
        0x22:"条件未满足（22h）",
        0x24:"请求序列错误（24h）",
        0x31:"请求超出范围（31h）",
        0x33:"安全访问拒绝（33h）",
        0x35:"密钥无效（35h）",
        0x36:"超出密钥访问次数限制（36h）",
        0x37:"延迟时间未到（37h）",
        0x70:"上传/下载操作拒绝（70h）",
        0x71:"传输数据暂停（71h）",
        0x72:"一般编程错误（72h）",
        0x7E:"子功能在会话中不支持（7Eh）",
        0x7F:"服务在会话中不支持（7Fh）",
        0x73:"块序列计数器错误（73h）",
    }
    # DTC表
    DTC_table = {

    }
    def __init__(self,id=None,ch = None):
        """
        构造方法
        """
        # 初始化变量NRC
        self.NRC = None
        # can通信对象
        self.ch = ch
        # ECU地址
        self.id = id
        # 实例化TP类
        self.TP = TPService(ch,id)
        # 定义接收数据检测连续状态
        self.continuous_status = False

    def check_message_status(self,uds_service_num,data)->[bool]:
        """
        判断接受到的报文是不是积极响应报文,并调用响应数据处理方法，
        现在在一个线程中处理，后期可考虑在多线程中处理，使用redis进行数据交互
        parm:
             uds_service_num->接收到该响应前，发送的UDS服务号(例：10服务就是10)
             data->报文数组
        rerurn:
             true->积极响应报文
             false->负响应报文
        """
        self.continuous_status = self.TP.judge_continuous_frame(data)
        print("continuous_status:",self.continuous_status)
        print("uds_service_num:",uds_service_num)
        if not self.continuous_status:# 判断不是连续帧
            if int(data[1],16) == uds_service_num + 0x40:
                # 判断为27服务回复帧
                if uds_service_num == 0x27:
                    # 这里调用27服务key解析和发送密钥方法
                    pass
                if uds_service_num == 0x22:
                    # 这里调用22服务数据处理方法
                    pass

                return True
            elif int(data[1],16) == 0x7F and int(data[2],16) == uds_service_num:
                self.NRC = int(data[3],16)# 当收到负响应报文保存NRC至类成员变量NRC
                return False
        elif int(data[0],16) & 0xF0 == 0x10 or int(data[0],16) & 0xF0 == 0x20:# 判断是连续帧返回true
            return True

    def session(self,id,sub_function=0x01,fill_data = 0x00):
        """
        10 会话服务
        parm:
             sub_function->子功能(该参数具体类型待定)
             id->接收方地址(物理地址或功能地址)
             fill_data->数据填充
        return:
             10服务报文帧
        """
        frame = Frame(id_=id,
                data=[0x02,0x10,
                sub_function,fill_data,
                fill_data,fill_data,fill_data,fill_data],
                dlc=8,
                flags=0)

        return frame

    def ecu_reset(self,id,sub_function,fill_data = 0x00):
        """
        11 ECU重置服务
        parm:
             sub_function->子功能(该参数具体类型待定)
             id->接收方地址(物理地址或功能地址)
             fill_data->数据填充
        return:
             11服务报文帧
        """
        frame = Frame(id_=id,
                data=[0x02,0x11,
                sub_function,fill_data,
                fill_data,fill_data,fill_data,fill_data],
                dlc=8,
                flags=0)

        return frame

    def clear_diagnosic_info(self,id,sub_function = 0,fill_data = 0x00):
        """
        14 清除诊断信息服务
        parm:
             id->接收方地址(物理地址或功能地址)
             sub_function->子功能(该参数具体类型待定)
             fill_data->数据填充
        return:
             14服务报文帧
        """
        # ALL DTCs
        if sub_function == 0:
            frame = Frame(id_=id,
                    data=[0x04,0x14,
                    0xFF,0xFF,
                    0xFF,fill_data,fill_data,fill_data],
                    dlc=8,
                    flags=0)
        # ALL emission-related DTCs
        if sub_function == 1:
            frame = Frame(id_=id,
                    data=[0x04,0x14,
                    0x00,0x00,
                    0x00,fill_data,fill_data,fill_data],
                    dlc=8,
                    flags=0)

        return frame

    def read_dtc_info(self,id,sub_function=0x00,
                    dtc_status_mask = 0x00,
                    DTC_high = 0x00,
                    DTC_medium = 0x00,
                    DTC_low = 0x00,
                    DID = 0x00,
                    DTC_snapshot_record = 0x00,
                    DTC_extended_data_record = 0x00,
                    DTC_severity_mask = 0x00,
                    fill_data = 0x00):
        """
        19 读dtc信息
        parm:
             id->接收方地址(物理地址或功能地址)
             sub_function->子功能(该参数具体类型待定)
             dtc_status_mask->dtc状态掩码
             DTC_high->DTC高字节，默认0x00
             DTC_medium->DTC中字节，默认0x00
             DTC_low->DTC低字节，默认0x00
             DID->使用需要did的子功能需要传入该参数，默认0x00
             DTC_snapshot_record->DTC_snapshot_record
             DTC_extended_data_record->06子功能的一个参数
             DTC_severity_mask->07子功能的一个参数
             fill_data->数据填充
        return:
             19服务报文帧

        tip：该服务返回的报文是连续报文，需要写程序判断连续报文
        """
        # 保存特殊子功能号,后面要对其单独写if功能分支
        special_sub_function = [0x04,0x05,0x06,0x07,0x08,0x09,0x10]
        if sub_function not in special_sub_function:
            frame = Frame(id_=id,
                    data=[0x03,0x19,
                    sub_function,dtc_status_mask,
                    fill_data,fill_data,fill_data,fill_data],
                    dlc=8,
                    flags=0)
        else:
            # report DTC snapshot record by DTC number
            if sub_function == 0x04:
                frame = Frame(id_=id,
                        data=[0x06,0x19,
                        sub_function,DTC_high,
                        DTC_medium,DTC_low,DTC_snapshot_record,fill_data],
                        dlc=8,
                        flags=0)
            # report DTC snapshot record by record number 
            if sub_function == 0x05:
                frame = Frame(id_=id,
                        data=[0x03,0x19,
                        sub_function,DTC_snapshot_record,
                        fill_data,fill_data,fill_data,fill_data],
                        dlc=8,
                        flags=0)
            # report DTC extended data record by DTC number or report mirror memory DTC extendes data record by ...
            if sub_function == 0x06 or sub_function == 0x10:
                frame = Frame(id_=id,
                        data=[0x06,0x19,
                        sub_function,DTC_high,
                        DTC_medium,DTC_low,DTC_extended_data_record,fill_data],
                        dlc=8,
                        flags=0)
            # report number of DTC by severity mask record or report DTC severity mask record
            if sub_function == 0x07 or sub_function == 0x08:
                frame = Frame(id_=id,
                        data=[0x04,0x19,
                        sub_function,DTC_severity_mask,
                        dtc_status_mask,fill_data,fill_data,fill_data],
                        dlc=8,
                        flags=0)
            # report severity information of DTC
            if sub_function == 0x09:
                frame = Frame(id_=id,
                        data=[0x05,0x19,
                        sub_function,DTC_high,
                        DTC_medium,DTC_low,fill_data,fill_data],
                        dlc=8,
                        flags=0)
        
        return frame

    def read_data_by_did(self,id,DID_dic = {}):
        """
        22 通过DID读取数据
        parm:
             id->接收方地址(物理地址或功能地址)
             DID_dic->字典，举例DID_dic = {"VIN":{"DID_high":0xF1,"DID_low":0x90}}
        return:
             22服务报文帧
        """
        if len(DID_dic) < 4:
            i = 0
            DID = [0x00,0x00,0x00,0x00,0x00,0x00]
            for key in DID_dic:
                DID[i] = DID_dic[key]["DID_high"]
                DID[i+1] = DID_dic[key]["DID_low"]
                i+=2
            frame = Frame(id_=id,
                data=[len(DID_dic)*2+1,0x22,
                DID[0],DID[1],
                DID[2],DID[3],DID[4],DID[5]],
                dlc=8,
                flags=0)
            return frame
        else:
            # 需要分多帧，还会涉及到流控，有待研究
            pass

    def security_access(self,id,sub_function,*key):
        """
        27 安全访问
        这个服务暂时还没想好怎么写
        """
        if sub_function % 2 == 0:# 发送key
            pass
        else:# 请求种子
            frame = Frame(id_=id,
                data=[0x02,0x27,
                sub_function,0x00,
                0x00,0x00,0x00,0x00],
                dlc=8,
                flags=0)
        return frame

    def security_access_calculate_key(self,id,seed):
        """
        用于通过seed计算key
        """
        # seed_length = len(seed)
        """
        这里写key计算算法
        """
        frame = Frame(id_=id,
            data=[0x06,0x27,
            0x02,0x00,
            0x00,0x00,0x00,0x00],
            dlc=8,
            flags=0)

        return frame

    def communication_control(self,id,sub_function = 0x00,*data):
        """
        28 通信控制
        这个服务暂时还没想好怎么写
        """
        pass

    def write_data_by_did(self,id,sub_function,*data):
        """
        2E 通过DID写数据
        这个服务暂时还没想好怎么写
        """
        pass

    def io_control_by_did(self,id,sub_function,*data):
        """
        2F io控制服务
        这个服务暂时还没想好怎么写
        """
        pass

    def routine_control(self,id,sub_function,*data):
        """
        31 服务
        这个服务暂时还没想好怎么写
        """
        pass

    def request_download(self,id,sub_function,*data):
        """
        34 请求下载服务
        这个服务暂时还没想好怎么写
        """
        pass

    def transfer_data(self,id,sub_function,*data):
        """
        36 数据传输服务
        这个服务暂时还没想好怎么写
        """
        pass

    def request_transfer_exit(self,id,sub_function,*data):
        """
        37 数据传输退出
        这个服务暂时还没想好怎么写
        """
        pass

    def tester_present(self,id,sub_function,*data):
        """
        3E 待机握手服务
        这个服务暂时还没想好怎么写
        """
        pass

    def control_dtc_setting(self,id,sub_function,*data):
        """
        85 服务
        这个服务暂时还没想好怎么写
        """
        pass

class TPService:
    """
    TP层服务
    """
    # 连续帧有效字节个数变量
    continuous_data_number = 0
    # 后续连续帧个数
    continuous_frame_number = 0
    # 连续帧数据合并数组
    continuous_data = []

    def __init__(self,ch,id):
        """
        构造方法
        parm:
             ch->can通信对象
             id->接收数据的ECU地址
        """
        # can通讯对象
        self.ch = ch
        # ECU地址
        self.id = id

    def check_flow_control_frame(self,data)->[bool,int,int,int]:
        """
        流控帧检查
        parm:
             data->接收到的数据数组，值为字符串
        return:
             
        """
        if int(data[0],16) & 0xF0 == 0x30:
            flow_state = int(data[0],16) & 0x0F
            block_size = int(data[1],16)
            STmin = int(data[2],16) 
            return [True,flow_state,block_size,STmin]
        else:
            return [False,0,0,0]

    def send_flow_control_frame(self,id,STmin = 0x14):
        """
        发送流控帧
        parm:
             id->接收地址
             STmin->帧最小间隔时间(默认20ms)
        rules:
             ISO15765
        """
        frame = Frame(id_=id,
            data=[0x30,0x00,
            STmin,0x00,
            0x00,0x00,0x00,0x00],
            dlc=8,
            flags=0)
        # 发送流控帧
        self.ch.write(frame)

    def judge_continuous_frame(self,data)->[bool]:
        """
        连续帧判断，并保存帧数据
        parm:
             data->接收到的数据
        return:
             True->判断为连续帧
             False->判断不是连续帧
        rules:
             ISO15765
        """
        # 判断首帧
        if int(data[0],16) & 0xF0 == 0x10:
            # 保存连续帧有效字节个数
            self.continuous_data_number = (int(data[0],16) & 0x0F)*255 + int(data[1],16)
            # 计算后续连续帧个数
            self.continuous_frame_number =  math.ceil((self.continuous_data_number - 6)/7)
            # 将连续帧有效字节数据保存
            for i in range(4):
                self.continuous_data.append(data[i+4])
            # 发送流控帧
            self.send_flow_control_frame(id = self.id)
            return True
        # 判断后续连续帧
        if int(data[0],16) & 0xF0 == 0x20:
            if int(data[0],16) & 0x0F == self.continuous_frame_number:# 连续帧的最后一帧
                for i in range((self.continuous_data_number - 6)%7):
                    self.continuous_data.append(data[i+1])
                print("continuous_data:",self.continuous_data)
            else:# 其它连续帧
                for i in range(7):
                    self.continuous_data.append(data[i+1])
            return True
        # 不是连续帧返回false
        return False

    def separate_frame_and_send(self,data_dic = {}):
        """
        要发送的数据超出一个can帧可承载的能力，需要对数据进行分帧处理
        parm:
             data_dic->接收到的需要分帧的数据(类型：字典)
        """
        pass
        