#-*-coding:utf-8 -*-
from selenium import webdriver
from flask import send_file,Flask,request,make_response,render_template,redirect
from app import  app
from .forms import rateForm


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

