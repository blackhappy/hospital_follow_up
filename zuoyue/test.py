import json,time
import ssl
from TTS.tts import Ws_Param
import websocket
import wave
import base64
from flask import request, Flask, jsonify
import os
import _thread as thread
from NLP.Answer import RequestNLP
app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
app.config['SECRET_KEY']=os.urandom(24)
# app.config['PERMANENT_SESSION_LIFETIME']=timedelta(days=1) #设置session的保存时间。

#define the params of wave
channels = 1
sampwidth = 2
framerate = 16000

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
    # if not request.get_data():
    #     return 'fail'
    # if request.method=='GET':
    #     userid=request.args.get('userid')
    # if request.method=='POST':
    #     if request.content_type.startswith('application/json'):
    #         userid=request.json.get('userid')
    #         text=request.json.get('text')
    #         cdrid=request.json.get('cdrid')
    #         taskid=request.json.get('taskid')
    #         wavefile=request.json.get('wavefile')
    #         param1=request.json.get('param1')
    #         param2 = request.json.get('param2')
    #         dtmf = request.json.get('dtmf')
    #         custom = request.json.get('custom')
    #         # comment=json.load(request.get_json()['name'])
    #     if request.content_type.startswith('multipart/form-data'):
    #         userid=request.form.get('userid')
    #         text = request.form.get('text')
    #         cdrid = request.form.get('cdrid')
    #         taskid = request.form.get('taskid')
    #         wavefile = request.form.get('wavefile')
    #         param1 = request.form.get('param1')
    #         param2 = request.form.get('param2')
    #         dtmf = request.form.get('dtmf')
    #         custom = request.form.get('custom')
    #     else:
    #         userid=request.values.get('userid')
    #         text = request.values.get('text')
    #         cdrid = request.values.get('cdrid')
    #         taskid = request.values.get('taskid')
    #         wavefile = request.values.get('wavefile')
    #         param1 = request.values.get('param1')
    #         param2 = request.values.get('param2')
    #         dtmf = request.values.get('dtmf')
    #         custom = request.values.get('custom')
    print("客户：%s" % (text))
    uid = 'test'
    msgtype='1'
    msg=text
    request_type=1
    # re=RequestNLP(uid,msgtype,msg,request_type)
    # answer_text=re.getNLP(url)
#机器人的
    answer_text = []
    answer_text.append('您好！请问您是王女士嘛')
    answer_text.append('我是神州医院内科的术后AI随访人员，想了解您最近的情况，看看能帮您做点什么')
    answer_text.append('请问您最近这么样，有什么不舒服吗？')
    answer_text.append('疼多长时间啦')
    answer_text.append('多会开始的？')
    answer_text.append('我非常理解您，这是术后常见的症状/并发症, 请问您术后复查过吗？')
    answer_text.append('查了哪些项目？')
    answer_text.append('复查结果怎么样？')
    answer_text.append('太好了！您术后一定要注意修养，根据您的情况您一个月后还需要复诊？')
    answer_text.append('我帮您先预约可以吗？')
    answer_text.append('好的，预约信息之后将发送到您的手机，注意查收')
    answer_text.append('不客气，祝您早日康复！再见')
#客户的
    quest_text = []
    quest_text.append("您好。")
    quest_text.append('是的我是。')
    quest_text.append('好啊谢谢。')
    quest_text.append('有腰酸背痛已经去医院看过。')
    quest_text.append("三个月。")
    quest_text.append("术后半年。")
    quest_text.append("复查过。")
    quest_text.append("查过胃镜和肿瘤标志物。")
    quest_text.append("医生说正常。")
    quest_text.append("好的。")
    quest_text.append("可以。")
    quest_text.append("非常感谢！")





    if text=='timeout' or text=="" or text==None:
        answer_text_res=answer_text[0]
    elif text == quest_text[1]:
        answer_text_res = answer_text[1]
    elif text == quest_text[2]:
        answer_text_res = answer_text[2]
    elif text == quest_text[3]:
        answer_text_res = answer_text[3]
    elif text == quest_text[0]:
        answer_text_res = answer_text[0]
    elif text == quest_text[4]:
        answer_text_res = answer_text[4]
    elif text == quest_text[5]:
        answer_text_res = answer_text[5]
    elif text == quest_text[6]:
        answer_text_res = answer_text[6]
    elif text == quest_text[7]:
        answer_text_res = answer_text[7]
    elif text == quest_text[8]:
        answer_text_res = answer_text[8]
    elif text == quest_text[9]:
        answer_text_res = answer_text[9]
    elif text == quest_text[10]:
        answer_text_res = answer_text[10]
    elif text == quest_text[11]:
        answer_text_res = answer_text[11]
    else:
        answer_text_res =answer_text[4]


    print("机器人：%s" % (answer_text_res))
    def on_message(ws, message):
        try:
            message = json.loads(message)
            code = message["code"]
            sid = message["sid"]
            audio = message["data"]["audio"]
            print(audio)
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
        'custom':'',
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

