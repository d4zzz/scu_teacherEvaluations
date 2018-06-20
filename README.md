# scu_teacherEvaluations
SCU one-click teacher evaluations

scu 一键评教系统，采用Python Flask。默认好评。

可以部署在服务器上

# 安装方法
使用了selenium，需要firefox内核支持，安装firefox
```sh
sudo apt install firefox
```
下载geckodriver，最新版地址为https://github.com/mozilla/geckodriver/releases
```sh
wget https://github.com/mozilla/geckodriver/releases/download/v0.21.0/geckodriver-v0.21.0-linux64.tar.gz
tar zxvf geckodriver-v0.21.0-linux64.tar.gz
cp geckodriver /usr/bin/
```
安装python依赖
```sh
pip install -r requirements.txt
```

启动
```sh
nohup python run.py &
```
