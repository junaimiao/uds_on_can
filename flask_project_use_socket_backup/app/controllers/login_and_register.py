from flask import Flask, redirect,render_template,Blueprint
# import can_message as can
login_and_register = Blueprint("login_and_register",__name__)


@login_and_register.route("/login/")
def login():
    return render_template("views/login.html")
    # return render_template("../login.html")
    # return redirect("../views/login2.html")

if __name__ == "__main__":
    login()
