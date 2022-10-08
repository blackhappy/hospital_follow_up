from flask import Flask
import os
import urllib
app = Flask(__name__)


@app.route('/')
def hello_world():
    url='http://172.16.115.58:9999/'
    filename='ss.txt'
    path='pcmfile/'+filename
    dir = url+path
    print(dir)
    with open(path, 'r', encoding='utf-8') as f:
        data=f.read()
        print(data)
    return dir


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=9999)