#!/usr/bin/python3
# -*-coding:utf-8 -*-
from socket import *
import time
from ASR import asrserver
from NLP.getAs import getAnswer
from TTS import ttserver
import json
import base64

COD = 'utf-8'
HOST = '172.16.115.214' # 主机ip

PORT = 21566 # 软件端口号
BUFSIZ = 1024
ADDR = (HOST, PORT)
SIZE = 10
tcpS = socket(AF_INET, SOCK_STREAM) # 创建socket对象
tcpS.setsockopt(SOL_SOCKET,SO_REUSEADDR,1) #加入socket配置，重用ip和端口
tcpS.bind(ADDR) # 绑定ip端口号
tcpS.listen(SIZE)  # 设置最大链接数
class Server:
    # def __init__(self,TaskId,DiaId,customMsg,data, code ):
    #     self.taskid=TaskId
    #     self.diaid=DiaId
    #     self.custommsg=customMsg
    #     self.data=data
    #     self.code=code


    def send_handle(self,data):
        return data
    def recv_msg_handle(self,message,ws):
        # message = bytes.decode(message)
        # message = json.loads(message)
        # code = message["code"]
        # taskid = message["taskid"]
        # diaid = message["diaid"]
        # username=message["custom_msg"]["username"]
        # audio = message["data"]["audio"]
        # audio = base64.b64decode(audio)
        # status = message["data"]["status"]
        # try:
        #     if status == 2:
        #         print("ws is closed")
        #         ws.close()
        #     if code != 0:
        #         errMsg = message["message"]
        #         print("sid:%s call error:%s code is:%s" % (taskid, errMsg, code))
        #     else:
        #         asr_text = self.asr_interact(audio)
        #         nlp_text = self.nlp_interact(asr_text)
        #         local_pcm = self.tts_interact(nlp_text)
        #         data = {
        #             'taskid':taskid,
        #             'code':code,
        #             'diaid':diaid,
        #             'wavfile':local_pcm
        #
        #         }
        #         return json.dumps(data)
        # try:
        #     mes=base64.b64decode(message)
            print(message)
        # except Exception as e:
        #     print("over", e)

    def asr_interact(self,audio):
        asr_text=asrserver.main(audio)
        return asr_text


    def nlp_interact(self,url,text):
        response_list = getAnswer(url, text, self.custommsg.name)
        nlp_text = response_list['response']
        self.diaid = response_list['uid']
        return nlp_text

    def tts_interact(self,text):
        wav_file=ttserver.main(text)
        return wav_file




while True:
    print("服务器启动，监听客户端链接")
    conn, addr = tcpS.accept()
    server=Server
    print("链接的客户端", addr)
    while True:
        try:
            data = conn.recv() # 读取已链接客户的发送的消息
            print(data)
            # return_data=server.recv_msg_handle(data,conn)
        except Exception:
            print("断开的客户端", addr)
            break
        print("客户端发送的内容:",data)
        if not data:
            break
        msg = time.strftime("%Y-%m-%d %X") #获取结构化事件戳
        msg1 = '[%s]:%s' % (msg, data)
        conn.send(msg1.encode(COD)) #发送消息给已链接客户端
    conn.close() #关闭客户端链接
tcpS.closel()