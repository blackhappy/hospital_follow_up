import json,time
import ssl
from TTS.tts import Ws_Param
import websocket
import wave
import base64
from datetime import timedelta
from flask import request, Flask
import os
import _thread as thread
from NLP.getAs import getAnswer

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
app.config['SECRET_KEY']=os.urandom(24)
app.config['PERMANENT_SESSION_LIFETIME']=timedelta(days=1) #设置session的保存时间。

#define the params of wave
channels = 1
sampwidth = 2
framerate = 8000

frequency_begin = 1
frequency_end = 100
#define the time of wave
answer_text=''


@app.route('/zuoyue', methods=['POST', 'GET'])
def requestzuoyue():
    localtime = time.asctime(time.localtime(time.time()))
    localtime = str(time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime()))
    myjson = request.get_json()
    print(myjson)
    userid = myjson.get("userid")
    telno = myjson.get("telno")
    text = myjson.get("text")
    cdrid = myjson.get("cdrid")
    taskid = myjson.get("taskid")
    wavfile = myjson.get("wavfile")
    param1 = myjson.get("param1")
    param2 = myjson.get("param2")
    custom = myjson.get("custom")
    dtmf = myjson.get("dtmf")
    print("客户：%s" % (text))

#机器人的
    answer_text = []
    answer_text.append('您还在听吗，还有什么问题吗？')
    answer_text.append('不好意思，刚没听清楚，您能再说一遍吗？')


    # if text=='timeout':
    #     answer_text_res=answer_text[0]
    # # elif text=="" or text==None:
    # #     answer_text_res=answer_text[1]
    #NLP智能问答
    print('+++++++++++++++++++++++++++++++++++++++' + custom)
    response_list = getAnswer(url, text,custom)
    answer_text_res = response_list['response']
    uid=response_list['uid']
    print('=++++++++++++++++++++++++++++++++++++++++' + uid)
    print("机器人：%s" % (answer_text_res))
    def on_message(ws, message):
        try:
            message = json.loads(message)
            code = message["code"]
            sid = message["sid"]
            audio = message["data"]["audio"]
            audio = base64.b64decode(audio)
            status = message["data"]["status"]
            # print(message)
            if status == 2:
                # with open('./pcmfile/demo_'+localtime+'.pcm', 'rb') as f:
                #     wave_data=f.read()
                #
                # with wave.open('./pcmfile/demo_'+localtime+'.wav', 'wb') as f:
                #     f.setnchannels(channels)
                #     f.setsampwidth(sampwidth)
                #     f.setframerate(framerate)
                #         # turn the data to string
                #     f.writeframes(wave_data)
                print("ws is closed")
                ws.close()
            if code != 0:
                errMsg = message["message"]
                print("sid:%s call error:%s code is:%s" % (sid, errMsg, code))
            else:
                with open('./pcmfile/demo_'+localtime+'.pcm', 'ab+') as f:
                    f.write(audio)
                with open('./pcmfile/demo_'+localtime+'.pcm', 'rb') as f:
                    wave_data=f.read()
                with wave.open('./pcmfile/demo_'+localtime+'.wav', 'wb') as f:
                    f.setnchannels(channels)
                    f.setsampwidth(sampwidth)
                    f.setframerate(framerate)
                        # turn the data to string
                    f.writeframes(wave_data)
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
            if os.path.exists('./pcmfile/demo_'+localtime+'.pcm'):
                os.remove('./pcmfile/demo_'+localtime+'.pcm')
            if os.path.exists('./pcmfile/demo_'+localtime+'.wav'):
                os.remove('./pcmfile/demo_'+localtime+'.wav')
        thread.start_new_thread(run, ())
    print("--------------------------------------------")
    wsParam = Ws_Param(APPID='5d1ad3d5',
                       APISecret='28c7560f3d6ec49f8c8750b76002ab34',
                       APIKey='b7c216ce0834468cc372f3f00d2d7b36',
                       Text=answer_text_res)
    websocket.enableTrace(False)
    wsUrl = wsParam.create_url()
    ws = websocket.WebSocketApp(wsUrl, on_message=on_message, on_error=on_error, on_close=on_close)
    ws.on_open = on_open
    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
    local_pcm ='U:http://'+host+':'+str(port)+'/pcmfile/demo_'+localtime+'.wav'
    data={
        'queueid':'',
        'playvoice':'',
        'asrvoice':local_pcm,
        'asrtimeout':'',
        'param1':'',
        'param2':'',
        'sos_eng':'',
        'eos_eng':'',
        'eos_time':'',
        'custom':uid,
        'maxdtmf':'',
        'enddtmf':''

    }
    return json.dumps(data)

if __name__ == '__main__':
    host ='58.132.214.154'
    port = 10001
    # host='172.16.118.148'
    url = 'http://10.131.102.103:10002/robot/query'
    app.run(debug=False, host='0.0.0.0', port=8888)

