from flask import Flask, redirect, url_for, render_template, request, abort
from controllers.login_and_register import login_and_register
from controllers.home import home

app = Flask(__name__)

# 注册蓝图，并指定其对应的前缀（url_prefix）
app.register_blueprint(login_and_register, url_prefix="/login_and_register")
app.register_blueprint(home, url_prefix="/home")

@app.route('/')
def hello_world():
   return 'Hello World'

@app.route("/test/")
def test():
    return render_template("views/login.html")
    # return render_template("views/login.html")
   #  return redirect(url_for("../views/login2.html"))
   # return redirect("../views/login2.html")

if __name__ == '__main__':
   app.run(debug=True)