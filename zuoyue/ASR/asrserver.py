# -*- coding: utf-8 -*-
"""
实时流式识别
需要安装websocket-client库
使用方式 python realtime_asr.py 16k-0.pcm
"""
import base64

import websocket
import wave
import threading
import time
import uuid
import json
import logging
import sys
import requests
# 下面2个是鉴权信息
APPID = 24957088

APPKEY = "B7FWkEsC30n1TR2egQp0yXuW"

# 语言模型 ， 可以修改为其它语言模型测试，如远场普通话19362
DEV_PID = 15372

# 可以改为wss://
URI = "ws://vop.baidu.com/realtime_asr"




logger = logging.getLogger()

"""

1. 连接 ws_app.run_forever()
2. 连接成功后发送数据 on_open()
2.1 发送开始参数帧 send_start_params()
2.2 发送音频数据帧 send_audio()
2.3 库接收识别结果 on_message()
2.4 发送结束帧 send_finish()
3. 关闭连接 on_close()

库的报错 on_error()
"""

class ASR:
    def  __init__(self,audio):
        self.audio=audio
        self.text=''

    def send_start_params(self, ws):
        """
        开始参数帧
        :param websocket.WebSocket ws:
        :return:
        """
        req = {
            "type": "START",
            "data": {
                "appid": APPID,  # 网页上的appid
                "appkey": APPKEY,  # 网页上的appid对应的appkey
                "dev_pid": DEV_PID,  # 识别模型
                "cuid": "121212",  # 随便填不影响使用。机器的mac或者其它唯一id，百度计算UV用。
                "sample": 16000,  # 固定参数
                "format": "pcm"  # 固定参数
            }
        }
        body = json.dumps(req)
        ws.send(body, websocket.ABNF.OPCODE_TEXT)
        logger.info("send START frame with params:" + body)


    def send_audio(self, ws):
        """
        发送二进制音频数据，注意每个帧之间需要有间隔时间
        :param  websocket.WebSocket ws:
        :return:
        """
        chunk_ms = 160  # 160ms的录音
        chunk_len = int(16000 * 2 / 1000 * chunk_ms)
        # pcm=requests.get(self.audio)
        # pcm=pcm.content
        pcm = bytes(self.audio,encoding='utf8')
        print(len(pcm))
        pcm=base64.b64decode(pcm)
        # print(pcm)
        index = 0
        total = len(pcm)
        logger.info("send_audio total={}".format(total))
        while index < total:
            end = index + chunk_len
            if end >= total:
                # 最后一个音频数据帧
                end = total
            body = pcm[index:end]
            logger.debug("try to send audio length {}, from bytes [{},{})".format(len(body), index, end))
            ws.send(body, websocket.ABNF.OPCODE_BINARY)
            index = end
            time.sleep(chunk_ms / 1000.0)  # ws.send 也有点耗时，这里没有计算


    def send_finish(self, ws):
        """
        发送结束帧
        :param websocket.WebSocket ws:
        :return:
        """
        req = {
            "type": "FINISH"
        }
        body = json.dumps(req)
        ws.send(body, websocket.ABNF.OPCODE_TEXT)
        logger.info("send FINISH frame")


    def send_cancel(self, ws):
        """
        发送取消帧
        :param websocket.WebSocket ws:
        :return:
        """
        req = {
            "type": "CANCEL"
        }
        body = json.dumps(req)
        ws.send(body, websocket.ABNF.OPCODE_TEXT)
        logger.info("send Cancel frame")


    def on_open(self, ws):
        """
        连接后发送数据帧
        :param  websocket.WebSocket ws:
        :return:
        """

        def run(*args):
            """
            发送数据帧
            :param args:
            :return:
            """
            self.send_start_params(ws)
            self.send_audio(ws)
            self.send_finish(ws)
            logger.debug("thread terminating")
            return
        threading.Thread(target=run).start()


    def on_message(self, ws, message):
        """
        接收服务端返回的消息
        :param ws:
        :param message: json格式，自行解析
        :return:
        """
        logger.info("Response: " + message)
        message = json.loads(message)
        if message['type']=="FIN_TEXT":
            self.text=message['result']


    def on_error(self, ws, error):
        """
        库的报错，比如连接超时
        :param ws:
        :param error: json格式，自行解析
        :return:
            """
        logger.error("error: " + str(error))


    def on_close(self, ws):
        """
        Websocket关闭
        :param websocket.WebSocket ws:
        :return:
        """
        logger.info("ws close ...")
        # ws.close()

    def inter(self):
        logging.basicConfig(format='[%(asctime)-15s] [%(funcName)s()][%(levelname)s] %(message)s')
        logger.setLevel(logging.DEBUG)  # 调整为logging.INFO，日志会少一点
        logger.info("begin")
        # websocket.enableTrace(True)
        uri = URI + "?sn=" + str(uuid.uuid1())
        logger.info("uri is " + uri)
        ws_app = websocket.WebSocketApp(uri,
                                        on_open=self.on_open,  # 连接建立后的回调
                                        on_message=self.on_message,  # 接收消息的回调
                                        on_error=self.on_error,  # 库遇见错误的回调
                                        on_close=self.on_close)  # 关闭后的回调
        ws_app.run_forever()

# if __name__ == "__main__":
#     if len(sys.argv) < 2:
#         pcm_file = "http://10.131.102.103:10001/pcmfile/demo_2021_11_09_17_13_33.wav"
#     else:
#         pcm_file = sys.argv[1]
#     audio='UklGRqQkAQBXQVZFZm10IBAAAAABAAEAQB8AAIA+AAACABAAZGF0YYAkAQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEAAQACAAMAAwADAAQABQAHAAsADwAUABgAGwAdAB0AHQAdAB0AHQAbABgAEwAOAAoABgAEAAMAAgACAAIAAQAAAAAA/v/9//3//v8AAP//+//z/+r/4//g/+X/7//8/wUACwALAAgAAwABAAAAAQACAAMAAwACAAMABgAJAA0ADwAQAA8ACwAEAP7/9//z//P/9//+/wUACAAHAAIA+//1//P/9f/5//7/AQACAAMABAAHAAsAEAAVABkAGwAbABgAFQAQAAsACAAGAAUABAACAP///P/5//j//P8CAAsAFAAbACIAIwAhAB4AHAAdAB0AIwA2AEEAQABRAFoAWABKAEoASgBGAE0ATABQAE8ASABBAEIARQBHAEIAOwA1ADEALAAqACwALAAuACMAJgAnACwALAAjACYAJwAuAC8AMAAsACYAGwASAAsACAADAAEAAQAFAAQA///4//n//P/8//X/6//j/93/2v/c/+P/6v/5////DQAXACMAJwAtAD0AOQA/AEUAQwA/AD0AOQA/ADwAQwBFAFEAUgBQAEIANAA8ADgANwBEAEIAOAA9ADgAKAAyAC8AMAA7AEIARwBIAE0ASgBEADoALQAqACsANQAtACoAMgAsAC0ANQAzADYAOAA5ADwALwAjACIAIAAkACYAJQAwACUAEAAEAP7/DwAaABAADgAhADcAMwAcAAcAHAAPAAQAFwAlACcALwAsADUASgA2ACsAOABIAEoAUgBQAEQAUQA+ADAASgBPAEEATABQAEsALQAaABgAHgAQABQAGwA0AEkASQA4AD8AIwAaABkADwDr//P/JAANABQACwAAAA0AGAAKAPP//f8oAD4AKgA3AFYAZQCGAJ0AqACrANEAsAC8ALkArQCjAL4A1gDEAPcA/gDmAMMAxwCTAGUAWgBAABkAGgDZ/5D/bf9p/yP/5v7d/qT+gf5R/gL+5v38/aX9gv1l/T79Zf1b/Vr9lf2a/b39KP5N/lz+tP4X/3L/yf8YAIAACgFTAaoBIwKaAg0DhgPvA1IEqgQGBU8FhQW7BeYF+wX3BekFwAVxBREFngQcBHwD5QI3Al4BegCF/4/+bf1c/FD7NPok+Sv4Q/dU9oj10vQ59K7zUPMf8wXzGPNe88PzQ/Th9J71nPaK96742fku+4L8/P2L/yQBuAJcBPoFuwcgCYsKGQx5DaUOrA+sEEwRCBJ6EqESsxK1En4SBxJREYQQiA9TDucMaAuiCc0H3wXeA5wBQP8a/eb6mfiF9mP0WPLk8Hvvr+1X7Kfr+eoZ6rHp0+ka6lbqCuvQ69vsF+5O76XwcfJ39BT2yfcC+hj8z/3e/+QBqwOOBW4HDwl1CvgLgg2bDocP1BC9EVUSLxPGExsUaBSeFJEUlBQwFNgTXxOmEsUR2BCqD2MO5gxOC5cJswfABa0DhQFT/+n8fvom+MT1pfM68SXvpu0p7G7qVOmc6L3nfedL5wLnM+dC6BzpB+oA68Ls5O6K8AnyTvSC9rL4Gvs5/Sf/4wEnBPAF+AfpCYELIg3FDi8QTxFdEogTphQQFV8VBxZhFo4WQhbfFdMVvxXVFMoTSRNvEvQQdg/9DYIMtQrNCMgG0ATJApQAJP7L+475Kfe29NHyX/Ay7iztAOxW6U/ohegQ6Czm5eUF58jnYecn6N/pKuuS7C/u4e/38V30P/ap+BH7Sf3X/ygCMARUBhkI9gn2C5QNAA9DELkREhMhFEYUkRSyFXMW4xVBFbsVNRbFFYAUtROjE0UTjhHeD+QO8A0vDBcKFghvBm4EEgIDAL393/qN+BL3g/Qq8Vbvt+6A7MTp3uib6G/neeb15QDmuObs5jTnWuh96czqdOz87RHwCfLs84f2FPnJ+j79PwCaAjQEaQbSCKwKQAwSDpMPshBKEsYTExRPFIUVoRaVFgMW9BXeFqYWXxWJFFAUzRPrEkgRBxAhD9kN4QvkCdUHTAZoBOkBkP+E/fn6xPgU9wP0L/DN7vbuVOtr55vn6+iv5g7kjORO5tXlK+UL5m3nj+gW6lbrDu0171fxlvNB9qz4qPpJ/XEA/wItBG0GdgmgC7EMLw48ENUR3hLtE+QUbRUoFkIXWRexFpoWoBc/F/oVIBUKFZMUVxOKEZEQ1g+VDicMCwrDCBsHcwTSAd7/r/3E+s/3GPbw8oHvFO4C7droAOe554nm6eMl4/Tjq+T441PjxuSI5uLn0Ogw6ifso+8o8dDy3PXa+On60v2DAL0C4ASZBzMKvQsRDZIP2xE4EyUURhWzFnIYohjbF6wY2RliGQwYCxhkGKcXChajFQQVlBO+Eb8QGA8SDdMKKgkFBysESAGY/9H8ufiE9Tn07PDX7Dvq5ulB6HXkOeLp4h3jr+DX3vvf/eKi4pLhROMf52jorOjf6tDuHfEi8zn2XPnu+5n+hgEXBKgGsAgbC+kNJBANEcASdBWSF1kXCxiNGs0bahqBGh0c+RtbGv8ZeRr4GUwY1BZQFokVbRMNEZYPNg7MC8gIggYoBNcA4v0++7r3mPOr8GbuxesO52nkA+V24xffAN6E33TfEN2A3HPfiuEg4Xnh/uRp6IrpYuoY7ijyavQl9lb6Q/5PAIICxAZBCcEKUA2GEJYSARTrFc4Ychq1Gs0b3x3SHugdXB2yHnEfdB2mG+wbdBzCGjcYwxZcFo0UzBG3Dq8M3AqgCK8EdQGx/rX7HPcI863v/Owr6Ankj+Py4pTdxtoO3ebdVtst2djaUN7M3xbeld8Z49rmSOgi6YLrM/HX8+H10PiA/Jb/jAOpBSoIwAroDoURIxPyFF4Y2Bk/HC0e1R0xHr4huSK4HyMfPiErIowfbh0ZHRgeAxwjGUQWuRVTFIcR6wwEC/QIvQXnAPb8uPgQ9sjxFez15uXlK+Sp3gDaCtyy3D/YdtZS2braM9o32k3bNd9/4cbhoeMu6KHqRO3A7xn0CPeL+RX9/QFGAzoGgQrIDaoPOxKwFMgYaRvzGmkcpCGPIzMgfyBRJJwlrCGlH4shJSPhH5ccBhxeHQ4buhbyE3oTbBCFDMsI6QXkAev9Bvol9inwwuva6A/lQuDI3Lrakdqm2M3VX9U/2FvY09bp15jbyt0t39bf5eLC5wvqG+u47mjzqvZ3+Vv8gwDbA0oH/wmeDNMPpRSHFhQX6Rr6IKEg/h3zIP0mRybUITQhhyWIJlMi+h04Hw0h7R4MGsAXlhfRFrMSUA4FC5kIZQW/AXn8yfbN8tTwc+zk5EvgjODq3q7ZJdc52OfY+9d51h7Xctll3AzcZduB36Hk/uSB5fTpn+5w8U/z9vYY+07+bAFABMEGrAztD5cPvxLKGjgdNBsRHb0isSUFJMEhziPIJismsiJAIU8ifSIQH6MbqBsVGx0XIhSgEg0Qnwu3B4AESgDd+hL3ffJq7cPp1OUA4U/f'
#
#     asr=ASR(audio)
#     res=asr.inter()
#     print(res)
# def main(audio):
#     asr=ASR(audio)
#     asr.inter()
#     return asr.text