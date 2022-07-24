
import socket,json, time, yaml,logging
import traceback
from Manager import Manager
from flask import Flask, jsonify, request
from ManagerExt import ext_api

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
app.register_blueprint(ext_api)

@app.route("/start", methods=["POST"])
def start():
    global app
    logging.debug(request)
    debug = request.args.get('debug')
    request_param = request.get_json()
    logging.debug("Request body: {}".format(request_param))
    result = app.manager.start(request_param, debug)
    return result

@app.route('/stop', methods=['GET'])
def stop():
    global app
    # response = requests.get(plc_url + 'deviceReset')
    result = app.manager.stop()
    return jsonify(result)


if __name__ == '__main__':
    app.manager = Manager('conf/edgeplat.yml')
    ext_api.manager = app.manager
    app.run(debug=False, host='0.0.0.0', port=9000)