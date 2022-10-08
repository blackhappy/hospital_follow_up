from Answer import RequestNLP
import ssl
from tts import Ws_Param
import websocket
import websocket
import datetime
import hashlib
import base64
import hmac
import json
from urllib.parse import urlencode
import time
from wsgiref.handlers import format_date_time
from datetime import datetime
from time import mktime
import _thread as thread
import os
import wave

#define the params of wave
channels = 1
sampwidth = 2
framerate = 8000

frequency_begin = 1
frequency_end = 100
#define the time of wave
time = 1


def on_message(ws, message):
    try:
        message =json.loads(message)
        code = message["code"]
        sid = message["sid"]
        audio = message["data"]["audio"]
        audio = base64.b64decode(audio)
        status = message["data"]["status"]
        print(message)
        if status == 2:
            print("ws is closed")
            ws.close()
        if code != 0:
            errMsg = message["message"]
            print("sid:%s call error:%s code is:%s" % (sid, errMsg, code))
        else:


            # with open('./pcmfile/demo_3.pcm', 'wb') as f:
            #     f.write(audio)
            # with open('./pcmfile/demo_3.pcm', 'rb') as f:
            #     wave_data=f.read()
            with wave.open('./pcmfile/demo.wav', 'wb') as f:
                f.setnchannels(channels)
                f.setsampwidth(sampwidth)
                f.setframerate(framerate)
                # turn the data to string
                f.writeframes(audio)



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
    def run(*args):
        d = {"common": wsParam.CommonArgs,
             "business": wsParam.BusinessArgs,
             "data": wsParam.Data,
             }
        d = json.dumps(d)
        print("------>开始发送文本数据")
        ws.send(d)
        if os.path.exists('./pcmfile/demo_3.pcm'):
            os.remove('./pcmfile/demo_3.pcm')
        if os.path.exists('./pcmfile/demo.wav'):
            os.remove('./pcmfile/demo.wav')

    thread.start_new_thread(run, ())


if __name__ == "__main__":
# def ResponseZY():
    # 测试时候在此处正确填写相关信息即可运行
    url = 'http://172.16.115.181:9999/robot/query'
    uid = 'test'
    msgtype = '1'
    msg = '我肚子疼'
    request_type = 1
    # re = RequestNLP(uid, msgtype, msg, request_type)
    # answer_text=json.load(re.getNLP(url))
    # print("对话文本是：%s" % (answer_text))
    # print(re.getNLP(url))
    # answer_text=re.getNLP(url)
    answer_text = '我很好谢谢，服务很满意'
    print("对话文本是：%s" % (answer_text))
    wsParam = Ws_Param(APPID='5d1ad3d5',
                       APISecret='28c7560f3d6ec49f8c8750b76002ab34',
                       APIKey='b7c216ce0834468cc372f3f00d2d7b36',
                       Text=answer_text)
    websocket.enableTrace(False)
    wsUrl = wsParam.create_url()
    ws = websocket.WebSocketApp(wsUrl, on_message=on_message, on_error=on_error, on_close=on_close)
    ws.on_open = on_open
    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})


