from flask import Flask, redirect,render_template,Blueprint
from flask_socketio import SocketIO
import _thread
import time
#不知道为什么要这样引入
import controllers.can_message as can
# import can_message as can
home = Blueprint("home",__name__)

socketio = SocketIO()

ch = ""

@home.route("/load_home/")
def load_home():
    return render_template("views/home.html")

# @home.route("/start/")
# def start():
#     ch = can.init()
#     _thread.start_new_thread(can.run(ch))
#     return render_template("views/login.html")
    

# @home.route("/stop/")
# def stop():
#     can.stop(ch)

@socketio.on('start', namespace='/test_conn')
def start():
    ch = can.init()
    while True:
        socketio.emit("server_response",{"data":can.getMessage(ch)},namespace="/test_conn")
    # return render_template("views/login.html")
    

@home.route("/stop/")
def stop():
    can.stop(ch)