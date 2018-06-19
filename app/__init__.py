# -*-coding:utf-8 -*-

from flask import Flask

#实例化一个应用
app = Flask(__name__)

#导入视图模块
from app import views
