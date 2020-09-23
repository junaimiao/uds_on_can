from flask import Flask, redirect, url_for, render_template, request, abort
from controllers.login_and_register import login_and_register
from controllers.home import home

from flask_socketio import SocketIO
# 引入can报文处理文件
import controllers.can_message as can
# 引入redis包
import redis
import pickle

import os

from multiprocessing import Process



app = Flask(__name__)
app.config['SECRET_KEY'] = 'hzc'
# websocket对象实例
socketio = SocketIO(app)

# cache = redis.StrictRedis("127.0.0.1",6379)
pool = redis.ConnectionPool(host = '127.0.0.1',port=6379,db=0)
r = redis.StrictRedis(connection_pool = pool)

# 注册蓝图，并指定其对应的前缀（url_prefix）
app.register_blueprint(login_and_register, url_prefix="/login_and_register")
app.register_blueprint(home, url_prefix="/home")

def open_auto_diagnostic():
   os.system('python C:\\Users\\Administrator\\Desktop\\project_auto_uds_by_python\\uds_on_can\\auto_diagnostic_final_for_web.py')

@app.route('/')
def index():
   # r = redis.StrictRedis("127.0.0.1",6379)
   return render_template("views/home.html")

@app.route("/auto_diagnostic",methods = ["GET"])
def auto_diagnostic():
   if request.method == "GET":
      result = request.args["diagnostic_case_table_address"]
      # auto_diagnostic_final.run(result)
      # print(result)
      # os.system("cd ")
      # print('python C:\\Users\\Administrator\\Desktop\\project_auto_uds_by_python\\uds_on_can\\flask_project_use_socket\\app\\controllers\\auto_diagnostic_final.py %s' % (result))
      # 向自动诊断脚本发送excel地址
      r.set("excel_name",result)
      # os.system('python C:\\Users\\Administrator\\Desktop\\project_auto_uds_by_python\\uds_on_can\\auto_diagnostic_final_for_web.py')
      Process(target = open_auto_diagnostic()).start()
      return {"result":"good"}


#出现消息后，率先执行此处
@socketio.on('message', namespace='/Socket')
def socket(message):
   print("接受到消息:",message["data"])
   if message["data"] == "start":
      r.set("message","start")
      r.set("diagnostic_message","stop")
      ch = can.init()
      ch = can.run(ch)
   # if message["data"] == "start":
      while True:
         if str(r.get("message"),encoding="utf8") == "stop":
            ch.busOff()
            ch.close()
            print(str(r.get("message")))
            # socketio.emit("stop",{"data":"结束"},namespace="/Socket")
            break
         elif str(r.get("message"),encoding="utf8") == "start":
            result = can.getMessage(ch)
            socketio.emit("response",{"data":result},namespace="/Socket")
            # socketio.emit("response",{"data":str(r.get("message"),encoding="utf8")},namespace="/Socket")
         elif str(r.get("message"),encoding="utf8") == "send":
            r.set("message","start")
            can.sendMessage(ch)

         if str(r.get("diagnostic_message"),encoding="utf8") == "start":
            pass
      print("结束")
   elif message["data"] == "stop":
      #通过redis存储消息
      r.set("message","stop")
   elif message["data"] == "send":
      #通过redis存储消息
      r.set("message","send")
   elif message["data"] == "start_diagnostic":
      #通过redis存储开始诊断消息
      # r.set("diagnostic_message","start")
      while True:
         if r.get("diagnostic_status") != None:
            if str(r.get("diagnostic_status"),"utf-8") == "finish":
               socketio.emit("diagnostic_status",{"data":"diagnostic_stop"},namespace="/Socket")
               r.delete("diagnostic_status")
               break


#当websocket连接成功时，自动触发connect默认方法
@socketio.on("connect",namespace="/Socket")
def connect():
   print("连接建立成功。。")

#当websocket连接失败时，自动触发disconnect默认方法
@socketio.on("disconnect",namespace="/Socket")
def disconnect():
   print("连接建立失败")

if __name__ == '__main__':
   # app.run(debug=True)
   socketio.run(app, debug=True)