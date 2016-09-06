# coding=utf-8

"""
Created by yanjie on 15-7-13.
"""
from flask import Flask
from flask_mail import Mail, Message
import pudb

app = Flask(__name__)

# mail config
app.config['MAIL_SUFFIX'] = 'mail.163.com'
#app.config['MAIL_SERVER'] = '10.213.18.243'
#app.config['MAIL_PORT'] = 1234
app.config['MAIL_SERVER'] = 'smtp.163.com'
app.config['MAIL_PORT'] = 25
app.config['MAIL_DEBUG'] = True
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'lyjtest3@163.com'
app.config['MAIL_PASSWORD'] = 'intsig'
app.config['MAIL_DEFAULT_SENDER'] = '测试邮件<lyjtest3@163.com>'

mail = Mail(app)
#mail.init_app(app)



@app.route('/index')
def index():
    return "Hello"


@app.route('/send')
def send():
    msg = Message("Hello",
                  sender="lyjtest3@163.com",
                  recipients=["liyj144@163.com"])
    msg.body = "text body"
    msg.html = "<b>HTML</b>body"
    #pudb.set_trace()
    mail.send(msg)
    return "send ok"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1212, debug=True)
