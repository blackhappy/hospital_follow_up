import requests, json
from flask import Flask,session
from flask import Response
import os



class RequestNLP:
    def __init__(self,uid,msgtype,msg,username,request_type):
        self.uid=uid
        self.msg_type=msgtype
        self.msg=msg
        self.user_name=username
        self.request_type=request_type
        self.data=json.dumps({"uid":self.uid, "msg":self.msg,"msg_type":self.msg_type, "user_name":self.user_name, "request_type":self.request_type})
    def getNLP(self,url):
        print(self.data)
        response=requests.post(url,data=self.data)
        # print(response.json())
        res=response.json()
        return res

    # def getAnswer(self,url,text):
    #     if session.get('uid'):
    #         uid = session.get('uid')
    #     else:
    #         uid = ''
    #     msgtype = ''
    #     msg = text
    #     request_type = 6
    #     username = '一菲'
    #     re = RequestNLP(uid, msgtype, msg, username, request_type)
    #     response_list = re.getNLP(url)
    #     answer_text_res = response_list['response']
    #     print('1111111111111111' + response_list['uid'])
    #     session['uid'] = response_list['uid']
    #     session.permanent = True
    #     return answer_text_res


# if __name__ == "__main__":
#     url='http://10.131.102.103:9999/robot/query'
#     uid=''
#     msgtype=''
#     msg=''
#     request_type=6
#     username='张三'
#     re=RequestNLP(uid,msgtype,msg,username,request_type,)
#     print(re.getNLP(url))

