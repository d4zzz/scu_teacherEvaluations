# -*-coding:utf-8 -*-
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask import send_file,Flask,request,make_response,render_template,session,redirect,url_for,flash,Response
# from StringIO import StringIO
from flask import send_file,request
import urllib
import datetime
import re,os
import sqlite3
import sys
# reload(sys)
# sys.setdefaultencoding("utf-8")
#sys.path.append('D:\\anaconda\\envs\\py2\\Lib\\site-packages')
from flask_qrcode import QRcode
import requests
import time
import logging

from flask_login import LoginManager


app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI']=\
    'sqlite:///' + os.path.join(basedir,'data.db')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN']=True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=True
app.config['SECRET_KEY']='hard to guess string'
#app.add_url_rule('/favicon.ico',redirect_to=url_for('static', filename='favicon.ico'))

lm=LoginManager()
lm.init_app(app)
lm.login_view = 'login'
lm.login_message='请登录后再访问本站'
qrcode=QRcode(app)
bootstrap=Bootstrap(app)
db=SQLAlchemy(app)




# def create_app(config_name):
#     app = Flask(__name__)
#     app.config.from_object(config[config_name])
#     config[config_name].init_app(app)
#     bootstrap.init_app(app)
#     qrcode.init_app(app)
#     db.init_app(app)
#
#     # 附加路由和自定义的错误页面
#     from .main import main as main_blueprint
#     app.register_blueprint(main_blueprint)
#
#     return app
from app import views,models
