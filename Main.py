
import socket,json, time, yaml,logging
import traceback
from flask import Flask, jsonify, request
from Manager import Manager

edgenodes = {}
debug=False

log_file_format = "[%(levelname)s] - %(asctime)s - %(name)s - : %(message)s in %(pathname)s:%(lineno)d"
log_console_format = "[%(levelname)s] - %(asctime)s - %(pathname)s:%(lineno)d : %(message)s"
main_logger = logging.getLogger()
main_logger.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(logging.Formatter(log_console_format))
main_logger.addHandler(console_handler)


app = Flask(__name__)

@app.route("/start", methods=["POST"])
def start():
    global app
    print(request)
    print("Debug: {}".format(request.args.get('debug')))
    request_param = request.get_json()
    print("Request body: {}".format(request_param))
    app.manager.start(request_param)
    return jsonify({'success':True})


if __name__ == '__main__':
    app.manager = Manager('conf/test/edge-ciga.yml')
    # startPlc()
    app.run(debug=False, host='0.0.0.0', port=9000)