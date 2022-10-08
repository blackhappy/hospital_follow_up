from flask import Flask
from flask import Response
import os

app = Flask(__name__)
folder = './pcmfile'


@app.route('/pcmfile/<file_key>')
def stream_mp3(file_key):
    def generate():
        path = os.path.join(folder, file_key)
        with open(path, 'rb') as video:
            data = video.read(1024)
            while data:
                yield data
                data = video.read(1024)

    return Response(generate(), mimetype="video")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10001)