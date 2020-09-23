# a = 0xFF
# b = "0xFF"

# print(a)
# # print(int(a,16))
# print(int(b,16))
# print(hex(b))


# DID_dic = {"VIN":{"DID_high":0xF1,"DID_low":0x90},"VIV":{"DID_high":0xF1,"DID_low":0x90}}

# for i in range(7):
#     print(i)




# def print_message(*data):
#     print(data)
#     print(type(data[1]))
#     # pass



# print_message(1,2,3)

# print(hex(0xF0 & 0x11))
# print(type(hex(0xF0 & 0x11)))
# import time
# a = time.time()

# time.sleep(2)

# b = time.time()

# print("%0.2f"%(b-a))

# NRC_table = {0x13:"报文长度错误（13h）",0x12:"子功能不支持（12h）"}


# print(NRC_table[0x12])

# print(int(0x735))

a = [1,2,3]
b = [2,3,4]
c = []

c.append(a)
c.append(b)

print(c)
