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
import time
import ssl
from wsgiref.handlers import format_date_time
from datetime import datetime
from time import mktime
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
time = 1
STATUS_FIRST_FRAME = 0  # 第一帧的标识
STATUS_CONTINUE_FRAME = 1  # 中间帧标识
STATUS_LAST_FRAME = 2  # 最后一帧的标识


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
# class ctts:
#     def __init__(self,wsParam):
#         self.wsParam=wsParam
#     def on_message(self,ws, message):
#         try:
#             message = json.loads(message)
#             code = message["code"]
#             sid = message["sid"]
#             audio = message["data"]["audio"]
#             audio = base64.b64decode(audio)
#             status = message["data"]["status"]
#             print(message)
#             if status == 2:
#                 print("ws is closed")
#                 ws.close()
#             if code != 0:
#                 errMsg = message["message"]
#                 print("sid:%s call error:%s code is:%s" % (sid, errMsg, code))
#             else:
#
#                 # with open('./pcmfile/demo_3.pcm', 'wb') as f:
#                 #     f.write(audio)
#                 # with open('./pcmfile/demo_3.pcm', 'rb') as f:
#                 #     wave_data=f.read()
#                 with wave.open('./pcmfile/demo_2.wav', 'wb') as f:
#                     f.setnchannels(channels)
#                     f.setsampwidth(sampwidth)
#                     f.setframerate(framerate)
#                     # turn the data to string
#                     f.writeframes(audio)
#
#
#
#         except Exception as e:
#             print("receive msg,but parse exception:", e)
#
#     # 收到websocket错误的处理
#     def on_error(self,ws, error):
#         print("### error:", error)
#
#     # 收到websocket关闭的处理
#     def on_close(self,ws):
#         print("### closed ###")
#
#     # 收到websocket连接建立的处理
#     def on_open(self,ws):
#         def run(*args):
#             d = {"common": wsParam.CommonArgs,
#                  "business": wsParam.BusinessArgs,
#                  "data": wsParam.Data,
#                  }
#             d = json.dumps(d)
#             print("------>开始发送文本数据")
#             ws.send(d)
#             if os.path.exists('./pcmfile/demo_3.pcm'):
#                 os.remove('./pcmfile/demo_3.pcm')
#             if os.path.exists('./pcmfile/demo_2.wav'):
#                 os.remove('./pcmfile/demo_2.wav')
#
#         thread.start_new_thread(run(), ())
#
#     def connect(self,trace=False):
#         websocket.enableTrace(trace)
#         # self.wsParam = Ws_Param(self.APPID,
#         #                    self.APISecret,
#         #                    self.APIKey,
#         #                    self.Text)
#         self.wsUrl = self.wsParam.create_url()
#         self.ws = websocket.WebSocketApp(self.wsUrl, on_open=self.on_open, on_message=self.on_message, on_error=self.on_error, on_close=self.on_close)
#         # self.thread=Thread(target=self.ws.run_forever())
#         # self.thread.start()
#         # self.ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
#
#
# if __name__ == "__main__":
#     answer_text = '我很好谢谢，服务很满意'
#     wsParam = Ws_Param(APPID='5d1ad3d5',
#                        APISecret='28c7560f3d6ec49f8c8750b76002ab34',
#                        APIKey='b7c216ce0834468cc372f3f00d2d7b36',
#                        Text=answer_text)
#     ct=ctts(wsParam)
#     ct.connect(wsParam)

