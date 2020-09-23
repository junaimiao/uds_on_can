from flask import Flask, redirect,render_template,Blueprint
#不知道为什么要这样引入
import controllers.can_message as can
# import can_message as can
login_and_register = Blueprint("login_and_register",__name__)


@login_and_register.route("/login/")
def login():
    ch = can.init()
    can.run(ch)
    return render_template("views/login.html")
    # return render_template("../login.html")
    # return redirect("../views/login2.html")

if __name__ == "__main__":
    login()
