# !/usr/bin/python3
# -*-coding:utf-8 -*-
import base64
import json
from socket import *
import string
import time
import logging
from ASR import asrserver
from NLP.getAs import getAnswer
from TTS import ttserver
COD = 'utf-8'
# HOST = '172.16.115.214' # 主机ip
HOST = '58.132.214.154' # 主机ip
PORT = 8888 # 软件端口号
BUFSIZ = 1024*2
ADDR = (HOST, PORT)
SIZE = 10
tcpS = socket(AF_INET, SOCK_STREAM) # 创建socket对象
tcpS.setsockopt(SOL_SOCKET,SO_REUSEADDR,1) #加入socket配置，重用ip和端口
tcpS.bind(ADDR) # 绑定ip端口号
tcpS.listen(SIZE)  # 设置最大链接数

logger = logging.getLogger()
class Server:
    def __init__(self):
        self.taskid=''
        self.diaid=''
        self.custommsg=dict
        self.data=dict
        self.code=0
    def send_handle(self,data):
        return data

    def asr_interact(self,audio):
        logger.info("send_audio".format(audio))
        asr=asrserver.ASR(audio)
        asr.inter()
        asr_text=asr.text
        print("asr 服务生成的文本:",  asr_text)
        return asr_text


    def nlp_interact(self,url,text,name,diaid):
        response_list = getAnswer(url, text, name, diaid)
        print(response_list)
        nlp_text = response_list['response']
        diaid = response_list['uid']
        print("nlp 服务生成的文本:", nlp_text)
        return nlp_text,diaid

    def tts_interact(self,text,taskid,diaid, ws):
        wav_file=ttserver.main(text,taskid,diaid,ws)
        print("tts 服务生成的语音文件:", wav_file)
        return wav_file



    def recv_msg_handle(self,audio,name,diaid, taskid, code, ws):
        url = 'http://10.131.102.103:10002/robot/query'
        try:
            asr_text = self.asr_interact(audio)
            nlp_text,nlp_diaid = self.nlp_interact(url,asr_text, name, diaid)
            wav_file=self.tts_interact(nlp_text,taskid,nlp_diaid,ws)
            # body = {
            #     'taskid': taskid,
            #     'diaid': self.diaid,
            #     "code": code,
            #     'wavfile': tts_res
            # }
            # message=json.dumps(body)
            message=wav_file
        except Exception as e:
            print("receive msg,but parse exception:", e)
        return message

while True:
    print("服务器启动，监听客户端链接")
    conn, addr = tcpS.accept()
    print("链接的客户端", addr)
    server = Server()
    while True:
        try:
            fin_audio = '',
            name='',
            diaid='',
            res_audio=''
            while True:
                data = conn.recv(BUFSIZ) # 读取已链接客户的发送的消息
                data = bytes.decode(data)
                if data[0:2]=='U:':
                    mes=data
                elif data[len(data)-2:]==':U':
                    mes = mes + data
                    mes = mes[2:len(mes) - 2]
                    message = json.loads(mes)
                    print("客户端发送的内容:", message)
                    status = message['data']['status']
                    audio = message['data']['audio']
                    name = message['custom_msg']['username']
                    diaid = message['diaid']
                    taskid = message['taskid']
                    code = message['code']
                    if status=="FIN_TEXT":
                        fin_audio=fin_audio+audio[2:len(audio)-1]
                        break
                    elif status == "HEARTBEAT":
                        fin_audio=audio[2:len(audio)-1]
                    else:
                        fin_audio=fin_audio+audio[2:len(audio)-1]
                    print(len(fin_audio))
                else:
                    mes = mes + data
            print(len(fin_audio))
            body = server.recv_msg_handle(fin_audio, name, diaid, taskid, code, conn)
            print("服务器返回的参数:", body)
            print('关闭客户端链接')
            conn.close()
        except Exception:
            print("断开的客户端", addr)
            break

        # if not body:
        #     break
        # msg = time.strftime("%Y-%m-%d %X") #获取结构化事件戳
        # msg1 = '[%s]:%s' % (msg, body)
        # conn.send(msg1.encode(COD)) #发送消息给已链接客户端
    conn.close() #关闭客户端链接
tcpS.closel()