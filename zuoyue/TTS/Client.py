#!/usr/bin/python3
# -*-coding:utf-8 -*-
from socket import *
import time
import uuid
import json
import base64
import logging
from time import ctime
import sys
import requests
if len(sys.argv) < 2:
    pcm_file = "http://10.131.102.103:10001/pcmfile/demo_2021_11_09_17_13_33.wav"
else:
    pcm_file = sys.argv[1]
logger = logging.getLogger()
HOST = '172.16.115.214' #服务端ip
# host = socket.gethostname()

PORT = 21566 #服务端端口号
BUFSIZ = 1024
ADDR = (HOST, PORT)
tcpCliSock = socket(AF_INET, SOCK_STREAM) #创建socket对象
tcpCliSock.connect(ADDR) #连接服务器



def send_audio(ws):
    """
    发送二进制音频数据，注意每个帧之间需要有间隔时间
    :param  websocket.WebSocket ws:
    :return:
    """
    chunk_ms = 160  # 160ms的录音
    chunk_len = int(16000 * 2 / 1000 * chunk_ms)
    pcm=requests.get(pcm_file)
    pcm=base64.b64encode(pcm.content)
    index = 0
    total = len(pcm)
    logger.info("send_audio total={}".format(total))
    while index < total:
        end = index + chunk_len
        if end >= total:
            # 最后一个音频数据帧
            end = total
        body = {
            'taskid':'22222222222',
            'diaid':'sadasd',
            'custom_msg':{
                'username':'张三'
            },
            'data':{
                'audio':str(pcm[index:end],encoding='utf-8'),
                'status':0
            },
            "code":1,
            'mes':'success'
        }
        body=json.dumps(body)
        # body=str(body)
        body=body.encode('utf-8')
        body=pcm[index:end]
        logger.debug("try to send audio length {}, from bytes [{},{})".format(len(body), index, end))
        ws.send(body)
        index = end
        time.sleep(chunk_ms / 1000.0)  # ws.send 也有点耗时，这里没有计算
while True:
    # data = input('>>').strip()
    # if not data:
    #     break
    # tcpCliSock.send(data.encode('utf-8')) #发送消息
    send_audio(tcpCliSock)
    data = tcpCliSock.recv(BUFSIZ) #读取消息
    if not data:
        break
    print(data.decode('utf-8'))
tcpCliSock.close() #关闭客户端

