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
    pcm_file = "http://10.131.102.103:10001/pcmfile/demo_2021_11_12_16_45_49.wav"
else:
    pcm_file = sys.argv[1]
logger = logging.getLogger()
# HOST = '172.16.115.214' #服务端ip
HOST = '10.131.102.103' #服务端ip
PORT = 8888 #服务端端口号
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
    chunk_ms = 320  # 160ms的录音
    chunk_len = int(16000 * 2 / 1000 * chunk_ms)
    pcm=requests.get(pcm_file)
    # print(pcm.content)
    pcm=base64.b64encode(pcm.content)
    index = 0
    total = len(pcm)
    # chunk_len=total
    print(total)
    logger.info("send_audio total={}".format(total))

    while index < total:
        end = index + chunk_len
        if end >= total:
            # 最后一个音频数据帧
            end = total
            type = "FIN_TEXT"
        elif end==chunk_len:
            type="HEARTBEAT"
        else:
            type="MID_TEXT"
        body = {
            'taskid': '22222222222',
            'diaid': '',
            'custom_msg': {
                'username': '张三'
            },
            'data': {
                'audio': str(pcm[index:end]),
                'status': type
            },
            "code": 1,
            'mes': 'success'
        }
        # print(len(pcm[index:end]))
        # # print(pcm[index:end])
        # print(len(body['data']['audio']))
        # print(body['data']['audio'])
        body = json.dumps(body)
        body='U:'+body+':U'
        body=bytes(body,'utf-8')
        print('发给服务端{}'.format(body))
        # body=str.encode(body)
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
    while True:

        data = tcpCliSock.recv(BUFSIZ) #读取消息
        data = bytes.decode(data)
        if data[0:2] == 'U:':
            mes = data
        elif data[len(data) - 2:] == ':U':
            mes = mes + data
            mes = mes[2:len(mes) - 2]
            message = json.loads(mes)
            print("接受服务端的信息:", message)
            status = message['data']['status']
            audio = message['data']['audio']
            diaid = message['diaid']
            taskid = message['taskid']
            code = message['code']
            print(len(audio))
            if status == "FIN_TEXT":
                fin_audio = fin_audio + audio
                break
            elif status == "HEARTBEAT":
                fin_audio = audio
            else:
                fin_audio = fin_audio + audio
        else:
            mes = mes + data
        if not data:
            break
    tcpCliSock.close() #关闭客户端
    break


