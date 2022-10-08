# -*- coding:utf-8 -*-
#
#   author: iflytek
#
#  本demo测试时运行的环境为：Windows + Python3.7
#  本demo测试成功运行时所安装的第三方库及其版本如下：
#   cffi==1.12.3
#   gevent==1.4.0
#   greenlet==0.4.15
#   pycparser==2.19
#   six==1.12.0
#   websocket==0.2.1
#   websocket-client==0.56.0
#   合成小语种需要传输小语种文本、使用小语种发音人vcn、tte=unicode以及修改文本编码方式
#  错误码链接：https://www.xfyun.cn/document/error-code （code返回错误码时必看）
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
from threading import Thread
import websocket
import datetime
import hashlib
import base64
import hmac
import json
from urllib.parse import urlencode

import ssl
from wsgiref.handlers import format_date_time
from datetime import datetime
from time import mktime
import time
import _thread as thread
import os
import wave
from flask import Flask
from flask import Response
app = Flask(__name__)

#define the params of wave
channels = 1
sampwidth = 2
framerate = 8000

frequency_begin = 1
frequency_end = 100
#define the time of wave
STATUS_FIRST_FRAME = 0  # 第一帧的标识
STATUS_CONTINUE_FRAME = 1  # 中间帧标识
STATUS_LAST_FRAME = 2  # 最后一帧的标识
localtime = time.asctime(time.localtime(time.time()))
localtime = str(time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime()))
host ='58.132.214.154'
port = 10001

class Ws_Param(object):
    # 初始化
    def __init__(self, APPID, APIKey, APISecret, Text):
        self.APPID = APPID
        self.APIKey = APIKey
        self.APISecret = APISecret
        self.Text = Text

        # 公共参数(common)
        self.CommonArgs = {"app_id": self.APPID}
        # 业务参数(business)，更多个性化参数可在官网查看
        self.BusinessArgs = {"aue": "raw", "auf": "audio/L16;rate=16000", "vcn": "x2_yifei", "speed": 50, "volume": 50, "pitch": 50, "tte": "utf8"}
        # self.BusinessArgs = {"aue": "raw", "auf": "audio/L16;rate=16000", "vcn": "xiaoyan", "tte": "utf8"}
        self.Data = {"status": 2, "text": str(base64.b64encode(self.Text.encode('utf-8')), "UTF8")}
        #使用小语种须使用以下方式，此处的unicode指的是 utf16小端的编码方式，即"UTF-16LE"”
        #self.Data = {"status": 2, "text": str(base64.b64encode(self.Text.encode('utf-16')), "UTF8")}


    # 生成url
    def create_url(self):
        url = 'wss://tts-api.xfyun.cn/v2/tts'
        # 生成RFC1123格式的时间戳
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))

        # 拼接字符串
        signature_origin = "host: " + "ws-api.xfyun.cn" + "\n"
        signature_origin += "date: " + date + "\n"
        signature_origin += "GET " + "/v2/tts " + "HTTP/1.1"
        # 进行hmac-sha256进行加密
        signature_sha = hmac.new(self.APISecret.encode('utf-8'), signature_origin.encode('utf-8'),
                                 digestmod=hashlib.sha256).digest()
        signature_sha = base64.b64encode(signature_sha).decode(encoding='utf-8')

        authorization_origin = "api_key=\"%s\", algorithm=\"%s\", headers=\"%s\", signature=\"%s\"" % (
            self.APIKey, "hmac-sha256", "host date request-line", signature_sha)
        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')
        # 将请求的鉴权参数组合为字典
        v = {
            "authorization": authorization,
            "date": date,
            "host": "ws-api.xfyun.cn"
        }
        # 拼接鉴权参数，生成url
        url = url + '?' + urlencode(v)
        # print("date: ",date)
        # print("v: ",v)
        # 此处打印出建立连接时候的url,参考本demo的时候可取消上方打印的注释，比对相同参数时生成的url与自己代码生成的url是否一致
        # print('websocket url :', url)
        return url

res_audio=[]
def main(text,taskid,diaid,conn):

    def on_message(ws, message):

        try:
            message = json.loads(message)
            print(message)
            code = message["code"]
            sid = message["sid"]
            audio = message["data"]["audio"]
            # audio = base64.b64decode(audio)
            status = message["data"]["status"]
            # print(message)
            if status == 2:
                print("ws is closed")
                ws.close()
            if code != 0:
                errMsg = message["message"]
                print("sid:%s call error:%s code is:%s" % (sid, errMsg, code))
            else:
                # with open('./pcmfile/demo_' + localtime + '.pcm', 'ab+') as f:
                #     f.write(audio)
                # with open('./pcmfile/demo_' + localtime + '.pcm', 'rb') as f:
                #     wave_data = f.read()
                # with wave.open('./pcmfile/demo_' + localtime + '.wav', 'wb') as f:
                #     f.setnchannels(channels)
                #     f.setsampwidth(sampwidth)
                #     f.setframerate(framerate)
                #     # turn the data to string
                #     f.writeframes(wave_data)
               res_audio.append(audio)
        except Exception as e:
            print("receive msg,but parse exception:", e)
        # 收到websocket错误的处理

    def on_error(ws, error):
        print("### error:", error)

        # 收到websocket关闭的处理

    def on_close(ws):
        print("### closed ###")

        # 收到websocket连接建立的处理

    def on_open(ws):
        din_audio=''
        def run(*args):
            d = {"common": wsParam.CommonArgs,
                 "business": wsParam.BusinessArgs,
                 "data": wsParam.Data,
                 }
            d = json.dumps(d)
            print("------>开始发送文本数据")
            ws.send(d)
            if os.path.exists('./pcmfile/demo_' + localtime + '.pcm'):
                os.remove('./pcmfile/demo_' + localtime + '.pcm')
            if os.path.exists('./pcmfile/demo_' + localtime + '.wav'):
                os.remove('./pcmfile/demo_' + localtime + '.wav')

        thread.start_new_thread(run, ())

    print("--------------------------------------------")
    wsParam = Ws_Param(APPID='5d1ad3d5',
                       APISecret='28c7560f3d6ec49f8c8750b76002ab34',
                       APIKey='b7c216ce0834468cc372f3f00d2d7b36',
                       Text=text)
    websocket.enableTrace(False)
    wsUrl = wsParam.create_url()
    ws = websocket.WebSocketApp(wsUrl, on_message=on_message, on_error=on_error, on_close=on_close)
    ws.on_open = on_open
    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
    local_pcm = 'U:http://' + host + ':' + str(port) + '/pcmfile/demo_' + localtime + '.wav'
    i=0
    if res_audio:
        code=1
    else:
        code=0
    while i<len(res_audio):
        if i==len(res_audio)-1:
            # 最后一个音频数据帧
            type = "FIN_TEXT"
        elif i==0:
            type = "HEARTBEAT"
        else:
            type = "MID_TEXT"
        body = {
            'taskid': taskid,
            'diaid': diaid,
            "code": code,
            'data': {
                'audio': res_audio[i],
                'status': type
            },
        }
        message = json.dumps(body)
        message = 'U:'+message+':U'
        print("------>开始发送语音数据{}".format(message))
        conn.send(message.encode('utf-8'))
        i+=1

    return local_pcm
# if __name__ == "__main__":
#     host ='58.132.214.154'
#     port = 10001
#     text='我爱你，一直爱'
#     main(text)

