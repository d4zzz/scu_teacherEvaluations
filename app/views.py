#-*-coding:utf-8 -*-
from selenium import webdriver
from flask import send_file,Flask,request,make_response,render_template,session,redirect,url_for,flash,Response,g
from flask_qrcode import QRcode
from flask import send_file,request
from wtforms.widgets.core import TextArea
import datetime
import re,os
import sqlite3
import sys
#reload(sys)
#sys.setdefaultencoding('utf8')
import requests
import time
import logging
from app import  lm,db,app
from .forms import rateForm,QueryCourse,VerifyForm,NoVerifyForm,SelectCourse,SelectForm4,SelectForm3,SelectForm2,SelectForm1,IndexForm,SelectForm,RescheduleForm,LoginForm,PayForm,CommentForm
from .models import User,Ticket,Comment
from .crawler import URP,URPSELECT
from flask_login import current_user,login_required,logout_user,login_user
import hashlib
# reload(sys)
# sys.setdefaultencoding("utf-8")
#
# basedir = os.path.abspath(os.path.dirname(__file__))
# app=Flask(__name__)
# qrcode=QRcode(app)
# app.config['SQLALCHEMY_DATABASE_URI']=\
#     'sqlite:///' + os.path.join(basedir,'data.sqlite')
# app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN']=True
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=True
# app.config['SECRET_KEY']='hard to guess string'
# bootstrap=Bootstrap(app)
# db=SQLAlchemy(app)



##路由
@lm.user_loader
def load_user(id):
    return User.query.filter_by(id=id).first()

@app.before_request
def before_request():
    g.user = current_user

@app.route('/login',methods=['GET','POST'])
def login():
    user=g.user
    if user is not None and user.is_authenticated:
        return redirect(url_for('index '))
    form = LoginForm()
    if form.validate_on_submit():
        zjh=form.zjh.data
        mm=form.mm.data
        session['zjh']=zjh
        session['mm']=mm
        #session['remember_me'] = form.remember_me.data
        urp = URP(zjh, mm)
        if urp.login() == True:
            u = User.query.filter_by(stu_id=form.zjh.data).first()
            if u is None:
                user = User(stu_id=form.zjh.data)#, password=form.mm.data)
                db.session.add(user)
                db.session.commit()
                login_user(user,remember=form.remember_me.data)
                #session['known'] = False
            else:
                #session['known'] = True
                u.timestamp=datetime.datetime.now()
                db.session.commit()
                login_user(u,remember=form.remember_me.data)


            #session['zjh'] = form.zjh.data

            resp = make_response(redirect(url_for('index')))
            outdate = datetime.datetime.today() + datetime.timedelta(days=30)
            resp.set_cookie('zjh', zjh, expires=outdate)
            return resp
        elif urp.login() == False:
            flash('账号或密码不正确')
            return render_template('login.html', form=form)
    return render_template('login.html',form=form)

@app.route('/',methods=['GET','POST'])
@app.route('/index',methods=['GET','POST'])
@login_required
def index():
    if g.user is None:
        return redirect(url_for('login'))
    form=IndexForm()
    # t = request.cookies.get('zjh')
    # if t != None and t == session['zjh']:
    if form.submit1.data :
        data = Ticket.query.filter_by(stu_id=g.user.stu_id).first()
        if data is not None and data.paid is True and data.used is False:
            flash('你已经预定了一张车票')
            return redirect(url_for('show'))
        return redirect(url_for('booking'))
    if form.submit2.data:
        return redirect(url_for('show'))
    if form.submit3.data:
        t= Ticket.query.filter_by(stu_id=g.user.stu_id,paid=True,used=False).first()
        if t is not None:
            flash('你的车票有效')
            return redirect(url_for('show'))
        else:
            flash('你没有有效车票')
            return redirect(url_for('index'))
    if form.submit4.data:
        return redirect(url_for('comment'))
    if form.submit5.data:
        return redirect(url_for('sel_cou'))
    if form.submit6.data:
        return redirect(url_for('que_cou'))
    #else:
        #redirect(url_for('login'))
    return render_template('index.html',form=form,zjh=g.user.stu_id)

@app.route('/booking',methods=['GET','POST'])
@login_required
def booking():
    #try:
            form=SelectForm()
        # t=request.cookies.get('zjh')
        # if t!= None and t==session['zjh']: #读取session
            data = Ticket.query.filter_by(stu_id=g.user.stu_id,used=False).first()
            if form.validate_on_submit():
                # data=User.query.filter_by(place=form.site.data).first()
                # if data is None:
                #     p=User.query.filter_by(username=session['zjh']).first()
                #     p.place=form.site.data
                #     g.user.ticket.
                #     db.session.commit()
                #     session['known']==False
                # else:
                #     session['known']==True

                site = form.site.data
                # form.site.data=''
                tk=Ticket()
                tk.stu_id=g.user.stu_id
                tk.trip=site
                tk.used=False
                tk.paid=False
                db.session.add(tk)
                db.session.commit()
                if site=='江安->望江':
                    return redirect(url_for('sel_time1'))
                elif site=='望江->江安':
                    return redirect(url_for('sel_time2'))
                elif site=='江安->华西':
                    return redirect(url_for('sel_time3'))
                elif site=='华西->江安':
                    return redirect(url_for('sel_time4'))
            if data is not None:
                if data.paid is True :
                    flash('你已经预定了一张车票了')
                    return redirect(url_for('show'))
                elif data.paid is False :
                    return redirect(url_for('pay'))

            else :
                return render_template('booking.html',form=form,zjh=g.user.stu_id)


        #else:
            #return redirect(url_for('index'))
    #except KeyError as e:
        #return redirect(url_for('index'))
            return render_template('booking.html', form=form)

@app.route('/show',methods=['GET','POST'])
@login_required
def show():
    # try:
        form=RescheduleForm()
        #t=request.cookies.get('zjh')
        #if t!=None and t == session['zjh']:
        data = Ticket.query.filter_by(stu_id=g.user.stu_id,used=False).first()
        if form.submit1.data:
            db.session.delete(data)
            db.session.commit()
            return redirect(url_for('index'))

            #qrzjh=session['zjh']
        if data is not None :
            if data.paid is True:
                url='http://101.132.99.228:5000/verify/'+data.tk_code
                return render_template('show.html',form=form,zjh=data.stu_id,time=data.time,trip=data.trip,info=url)
            else :
                flash('你还有车票没付款')
                return redirect(url_for('pay'))
        else :
            flash('你还没有订票')
            return redirect(url_for('index'))
        return render_template('show.html',form=form,zjh=g.user.stu_id)

    #except KeyError as e:
        #return redirect(url_for('index'))



    # elif form.submit2.data:
    #     return redirect(url_for('select'))

@app.route('/verify/<ticket_code>',methods=['GET','POST'])
def verify(ticket_code):
    v=False
    ticket_code=ticket_code.split('?')[0]
    t=Ticket.query.filter_by(tk_code=ticket_code).first()
    form=VerifyForm()
    #form2=NoVerifyForm()
    if form.validate_on_submit():
        #if form.verify.data :
        t.used=True
        db.session.commit()
        flash('这张票已经使用')
        return redirect(url_for('index'))
    if t is not None:
        v =True
        return render_template('verify.html',form=form,ver=v)
    else :
        v=False
    return redirect(url_for('index'))
    #return render_template('verify.html',form=form2,ver=v)
    #if form2.validate_on_submit():
        #if form.noverify.data :
#       flash('这张票已经失效，请重新购票')
#       return redirect(url_for('index'))
    #return render_template('verify.html',ver=v)

# @app.route('/select0',methods=['GET','POST'])
# def select0():
#     form=SelectForm()
#     return render_template()


@app.route('/SelectCourse',methods=['GET','POST'])
@login_required
def sel_cou():
    form=SelectCourse()
    #t=request.cookies.get('zjh')
    #if t!=None and t==session['zjh']:
    flash('请输入信息开始选课')
    if form.validate_on_submit():
        kch=form.kch.data
        cxkxh=form.cxkxh.data
            #print kch,cxkxh
        urps=URPSELECT(session['zjh'],session['mm'],kch,cxkxh)

        #print urps.sc()
        if urps.sc()==True:
            flash('选课成功!')
        elif urps.sc()==False:
            flash('选课失败，请重新选课!')
    return render_template('selectcourse.html',form=form)

@app.route('/CourseTable',methods=['GET','POST'])
@login_required
def cou_tab():
    return render_template('coursetable.html')
@app.route('/QueryCourse',methods=['GET','POST'])
@login_required
def que_cou():
    form=QueryCourse()
    if form.submit.data:
        return redirect(url_for('cou_tab'))
    #t=request.cookies.get('zjh')
    #if t!=None and t==session['zjh']:
    #if form.validate_on_submit():
    #    kch=form.kch.data
    #    cxkxh=form.cxkxh.data
            #print kch,cxkxh
    #    urps=URPSELECT(session['zjh'],session['mm'],kch,cxkxh)

        #print urps.sc()
    #    if urps.sc()==True:
    #        flash('选课成功!')
    #    elif urps.sc()==False:
    #        flash('选课失败，请重新选课!')
    return render_template('querycourse.html',form=form,zjh=session['zjh'])


# def _serve_pil_image(a):
#     data = a
#     return send_file(qrcode(data, mode='raw'),mimetype='image/png')

@app.route('/logout',methods=['GET','POST'])
def logout():
    session.pop('zjh',None)
    flash('你已经退出登录')
    logout_user()
    return redirect(url_for('login'))



@app.route('/sel_time1',methods=['GET','POST'])
@login_required
def sel_time1():
    # try:
    #     t=request.cookies.get('zjh')
    #     if t!=None and t==session['zjh']:
    #         form=SelectForm1()
            form=SelectForm1()

            if form.validate_on_submit():
                t = Ticket.query.filter_by(stu_id=g.user.stu_id).first()
                t.time=form.time.data
                db.session.commit()
                return redirect(url_for('pay'))
            return render_template('sel_time1.html',form=form,zjh=g.user.stu_id)
                #t=User.query.filter_by(time=form.time1.data).first()
                # if t is None:
                #     t=User.query.filter_by(username=session['zjh']).first()
                #     t.time=form.time1.data
                #     db.session.commit()
                #     session['known']==False
                # else:
                #     session['known']==True
                # return redirect(url_for('pay'))
    #     else:
    #         return redirect(url_for('index'))
    # except KeyError as e:
    #     return redirect(url_for('index'))


@app.route('/sel_time2',methods=['GET','POST'])
@login_required
def sel_time2():
    # try:
    #     t=request.cookies.get('zjh')
    #     if t!=None and t==session['zjh']:
    #
    #         form=SelectForm2()
    #         if form.validate_on_submit():
    #             tk = Ticket(trip=g.user.ticket.trip, time=form.time.data, valid=True, owner=g.user.stu_id)
    #             db.session.add(tk)
    #             db.session.commit()
    #             return redirect(url_for('pay'))
    #             # t=User.query.filter_by(time=form.time2.data).first()
    #             # if t is None:
    #             #     t=User.query.filter_by(username=session['zjh']).first()
    #             #     t.time=form.time2.data
    #             #     db.session.commit()
    #             #     session['known']==False
    #             # else:
    #             #     session['known']==True
    #             #
    #             # return redirect(url_for('pay'))
    #
    #     else:
    #         return redirect(url_for('index'))
    # except KeyError as e:
    #     return redirect(url_for('index'))
    # return render_template('sel_time2.html',form=form)
    form = SelectForm2()
    if form.validate_on_submit():
        t = Ticket.query.filter_by(stu_id=g.user.stu_id).first()
        t.time = form.time.data
        db.session.commit()
        return redirect(url_for('pay'))
    return render_template('sel_time2.html', form=form,zjh=g.user.stu_id)

@app.route('/sel_time3',methods=['GET','POST'])
@login_required
def sel_time3():
    # try:
    #     t=request.cookies.get('zjh')
    #     if t!=None and t==session['zjh']:
    #
    #         form=SelectForm3()
    #         if form.validate_on_submit():
    #             tk = Ticket(trip=g.user.ticket.trip, time=form.time.data, valid=True, owner=g.user.stu_id)
    #             db.session.add(tk)
    #             db.session.commit()
    #             return redirect(url_for('pay'))
    #             # t=User.query.filter_by(time=form.time3.data).first()
    #             # if t is None:
    #             #     t=User.query.filter_by(username=session['zjh']).first()
    #             #     t.time=form.time3.data
    #             #     db.session.commit()
    #             #     session['known']==False
    #             # else:
    #             #     session['known']==True
    #             #
    #             # return redirect(url_for('pay'))
    #     else:
    #         return redirect(url_for('index'))
    # except KeyError as e:
    #     return redirect(url_for('index'))
    # return render_template('sel_time3.html',form=form)
    form = SelectForm3()
    if form.validate_on_submit():
        t = Ticket.query.filter_by(stu_id=g.user.stu_id,paid=False).first()
        t.time = form.time.data
        db.session.commit()
        return redirect(url_for('pay'))
    return render_template('sel_time3.html', form=form,zjh=g.user.stu_id)

@app.route('/sel_time4',methods=['GET','POST'])
@login_required
def sel_time4():
    # try:
    #     t=request.cookies.get('zjh')
    #     if t!=None and t==session['zjh']:
    #         form=SelectForm4()
    #         if form.validate_on_submit():
    #             tk = Ticket(trip=g.user.ticket.trip, time=form.time.data, valid=True, owner=g.user.stu_id)
    #             db.session.add(tk)
    #             db.session.commit()
    #
    #             # t=User.query.filter_by(time=form.time4.data).first()
    #             # if t is None:
    #             #     t=User.query.filter_by(username=session['zjh']).first()
    #             #     t.time=form.time4.data
    #             #     db.session.commit()
    #             #     session['known']==False
    #             # else:
    #             #     session['known']==True
    #
    #             return redirect(url_for('pay'))
    #
    #     else:
    #         return redirect(url_for('index'))
    # except KeyError as e:
    #     return redirect(url_for('index'))
    # return render_template('sel_time4.html',form=form)
    form = SelectForm4()
    if form.validate_on_submit():
        t = Ticket.query.filter_by(stu_id=g.user.stu_id,paid=False).first()
        t.time = form.time.data
        db.session.commit()
        return redirect(url_for('pay'))
    return render_template('sel_time1.html', form=form,zjh=g.user.stu_id)

@app.route('/pay',methods=['GET','POST'])
@login_required
def pay():
    form=PayForm()
    data=Ticket.query.filter_by(stu_id=g.user.stu_id,paid=False,used=False).first()
    if form.validate_on_submit():
        if data is not None:
            data.paid=True
            data.date=datetime.datetime.today().date()
            data.timestamp=datetime.datetime.now()
            t=data.timestamp
            h=hashlib.md5(str(t))
            h.update(data.stu_id)
            data.tk_code=h.hexdigest()
            db.session.commit()
            return redirect(url_for('show'))
        return redirect(url_for('show'))
    return render_template('pay.html',form=form,zjh=g.user.stu_id)

#@app.route('/comment',methods=['GET','POST'])
#@login_required
#def comment():
#    form=CommentForm()
#    if form.validate_on_submit():
#        text=form.commt.data
#        flash('感谢您的建议')
#        return redirect(url_for('index'))
#    return render_template('comment.html',form=form)


@app.route('/driver',methods=['GET','POST'])
def driver():
    d=datetime.datetime.today().date()
    ticket=Ticket.query.filter_by(date=d)
    if ticket is None:
        return render_template('driver.html',any=False)
    jtw=Ticket.query.filter_by(trip=u'江安->望江').count()
    wtj=Ticket.query.filter_by(trip=u'望江->江安').count()
    jth=Ticket.query.filter_by(trip=u'江安->华西').count()
    htj=Ticket.query.filter_by(trip=u'华西->江安').count()
    return render_template('driver.html',any=True,jtw=jtw,wtj=wtj,jth=jth,htj=htj)

@app.route('/comment',methods=['GET','POST'])
@login_required
def comment():
    form=CommentForm()
    sno=session['zjh']
    nickname=form.nickname.data
    content=form.content.data
    t=request.cookies.get('zjh')
    if t!=None and t==session['zjh']:
        if form.submit.data:
            comment=Comment(sno,nickname,content)
            db.session.add(comment)
            db.session.commit()
            return redirect(url_for('comment_list'))
    return render_template('write_comment.html',form=form)

@app.route('/comment_list',methods=['GET'])
@login_required
def comment_list():
    comments=Comment.query.all()
    return render_template('comment_list.html',comments=comments)

@app.route('/rate',methods=['GET','POST'])
def rate():
    form=rateForm()
    if form.submit.data:
        zjh=form.zjh.data
        mm=form.mm.data
        options=webdriver.FirefoxOptions()
        options.set_headless()
        options.add_argument('--disable-gpu')
        broswer=webdriver.Firefox(firefox_options=options)
        broswer.get('http://zhjw.scu.edu.cn')
        broswer.find_element_by_name('zjh').send_keys(zjh)
        broswer.find_element_by_name('mm').send_keys(mm)
        broswer.find_element_by_id('btnSure').click()
        broswer.get('http://zhjw.scu.edu.cn/jxpgXsAction.do?oper=listWj')
        broswer.find_element_by_css_selector(".pageAlign > div:nth-child(2) > table:nth-child(1) > tbody:nth-child(1) > tr:nth-child(1) > td:nth-child(1) > select:nth-child(5) > option:nth-child(8)").click()
        for i in range(1,100):
            try:
                broswer.find_element_by_xpath('/html/body/form/table[4]/tbody/tr/td/table/tbody/tr['+str(i)+']/td[5]/img').click()
                if '提交' not in broswer.page_source:
                    broswer.get('http://zhjw.scu.edu.cn/jxpgXsAction.do?oper=listWj')
                    broswer.find_element_by_css_selector(".pageAlign > div:nth-child(2) > table:nth-child(1) > tbody:nth-child(1) > tr:nth-child(1) > td:nth-child(1) > select:nth-child(5) > option:nth-child(8)").click()
                    continue
            except Exception:
                continue
            ckb=".fieldsettop > tbody:nth-child(1) > tr:nth-child(1) > td:nth-child(1) > table:nth-child(2) > tbody:nth-child(1) > tr:nth-child(2) > td:nth-child(2) > table:nth-child(1) > tbody:nth-child(1) > tr:nth-child(1) > td:nth-child(1) > table:nth-child(1) > tbody:nth-child(1) > tr:nth-child(1) > td:nth-child(2) > table:nth-child(1) > tbody:nth-child(1) > tr:nth-child({}) > td:nth-child(1) > input:nth-child(1)"
            for i in range(2,23,3):
                try:
                    broswer.find_element_by_css_selector(ckb.format(i)).click()
                except Exception:
                    continue
            broswer.find_element_by_name('zgpj').send_keys('很好')
            broswer.find_element_by_css_selector('.fieldsettop > tbody:nth-child(1) > tr:nth-child(1) > td:nth-child(1) > table:nth-child(4) > tbody:nth-child(1) > tr:nth-child(1) > td:nth-child(1) > img:nth-child(1)').submit()
            try:
                broswer.find_element_by_xpath("//*[@id='alert']/input").click()
            except Exception:
                pass
            broswer.get('http://zhjw.scu.edu.cn/jxpgXsAction.do?oper=listWj')
            broswer.find_element_by_css_selector(".pageAlign > div:nth-child(2) > table:nth-child(1) > tbody:nth-child(1) > tr:nth-child(1) > td:nth-child(1) > select:nth-child(5) > option:nth-child(8)").click()
        flash('评教完成')
        broswer.close()
        return render_template('rate.html',form=form)
    return render_template('rate.html',form=form)

@app.errorhandler(404)
def internal_error(error):
    return render_template('404.html'),404

@app.errorhandler(401)
def auth_error(error):
    return redirect(url_for('login'))

@app.errorhandler(500)
def server_error(error):
    return render_template('500.html'),500
