# -*-coding:utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField,PasswordField
import sys
#reload(sys)
#sys.setdefaultencoding('utf8')


class rateForm(FlaskForm):
    zjh=StringField('学号')
    mm=PasswordField('密码')
    submit=SubmitField('提交')    
