from flask import Flask, redirect,render_template,Blueprint
import _thread
import time
#不知道为什么要这样引入
import controllers.can_message as can
# import can_message as can
home = Blueprint("home",__name__)

ch = ""

@home.route("/load_home/")
def load_home():
    return render_template("views/home.html")

@home.route("/start/")
def start():
    ch = can.init()
    _thread.start_new_thread(can.run(ch))
    return render_template("views/login.html")
    

@home.route("/stop/")
def stop():
    can.stop(ch)