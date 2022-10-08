from flask import Flask
import logging
import time
import os

app = Flask(__name__)
# 日志系统配置
handler = logging.FileHandler('error.log', encoding='UTF-8')
logging_format = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(lineno)s - %(message)s')

handler.setFormatter(logging_format)
app.logger.addHandler(handler)


@app.errorhandler(404)
def page_not_found(error):
    logger.error(error)

    return 'This page does not exist', 404


@app.errorhandler(500)
def special_exception_handler(error):
    app.logger.error(error)
    return '请联系管理员', 500


def page_not_found(error):
    return 'This page does not exist', 404


app.error_handler_spec[None][404] = page_not_found


@app.route('/')
def testdasdas1():
    no_thing = []
    i = no_thing[0]
    return 'Hello!'


if __name__ == '__main__':
    app.run()