import json
from flask import request, Flask, jsonify,session
import os
from datetime import timedelta
from Answer import RequestNLP
app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
app.config['SECRET_KEY']=os.urandom(24)
app.config['PERMANENT_SESSION_LIFETIME']=timedelta(days=1) #设置session的保存时间。

# @app.route('/zuoyue', methods=['POST','GET'])
def getAnswer(url,text,username,uid):
    # myjson = request.get_json()
    # text = myjson.get("text")
    msgtype = ''
    msg = text
    request_type = 6
    re = RequestNLP(uid, msgtype, msg, username, request_type)
    response_list = re.getNLP(url)
    # answer_text_res = response_list['response']
    # print('1111111111111111' + response_list['uid'])
    # session['uid'] = response_list['uid']
    # print('+++++++++++=======+++++++++++++'+session.get('uid'))
    # session.permanent = True
    return response_list
#
# if __name__ == '__main__':
#     url = 'http://10.131.102.103:10002/robot/query'
#     app.run(host="0.0.0.0", port=8080)