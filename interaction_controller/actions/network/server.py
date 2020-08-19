from flask import Flask, request
from gevent.pywsgi import WSGIServer

proxy = Flask(__name__)
proxy.debug = False

@proxy.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    file.save('upload/' + file.filename)
    return ('OK', 200)

if __name__ == '__main__':
    server = WSGIServer(('10.2.64.8', 12345), proxy)
    server.serve_forever()

