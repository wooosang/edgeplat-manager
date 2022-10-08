
import socket,json, time, yaml,logging, os
import traceback
from Manager import Manager
from flask import Flask, jsonify, request
from ManagerExt import ext_api

edgenodes = {}
debug=False

log_file_format = "[%(levelname)s] - %(asctime)s - %(name)s - : %(filename)s:%(lineno)d : %(message)s"
log_console_format = "[%(levelname)s] - %(asctime)s - %(pathname)s:%(lineno)d : %(message)s"
main_logger = logging.getLogger()
main_logger.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(logging.Formatter(log_console_format))
main_logger.addHandler(console_handler)

handler = logging.FileHandler("manager.log")
handler.setLevel(logging.DEBUG)#可以不设，默认是WARNING级别
formatter = logging.Formatter(log_file_format)
handler.setFormatter(formatter) #设置文件的log格式
main_logger.addHandler(handler)



app = Flask(__name__)
app.register_blueprint(ext_api)

def doStart(conf=None, request_param={}, debug=False):
    logging.debug("Start starting..............")
    global app
    try:
        if conf is not None:
            init('conf/'+conf+'.yml')
    except Exception as e:
        traceback.print_exc()
        return {"success": False, "msg": str(e)}
    result = app.manager.start(request_param, debug)
    return result


@app.route("/start", methods=["POST"])
def start():
    logging.debug(request)
    debug = request.args.get('debug')
    conf = request.args.get('conf')
    request_param = request.get_json()
    logging.debug("Request body: {}".format(request_param))
    result = doStop(conf, debug)
    return doStart(conf, request_param, debug)

def doStop(conf=None, debug=False):
    logging.debug("Start stopping................")
    global app
    try:
        if conf is not None:
            init('conf/'+conf+'.yml')
    except Exception as e:
        traceback.print_exc()
        return {"success": False, "msg": str(e)}
    try:
        result = app.manager.stop(conf, debug)
    except Exception as e:
        return {"success": False, "msg": str(e)}
    logging.debug("Stop succeed!")
    return result

@app.route('/stop', methods=['GET'])
def stop():
    logging.debug(request)
    debug = request.args.get('debug')
    conf = request.args.get('conf')
    result = doStop(conf, debug)
    return jsonify(result)

@app.route('/startorstop/<action>', methods=['GET'])
def startorstop(action):
    if action == '1':
        return doStart()
    else:
        return doStop()

@app.route('/reload', methods=['GET','POST'])
def reload():
    conf = request.args.get('conf')
    logging.info('Reload conf {}'.format(conf))
    init(conf)

app.config['UPLOAD_FOLDER'] = '/upgrade_files'

@app.route('/upload', methods=['POST'], strict_slashes=False)
def upload():
    print('uploading...................')
    f = request.files['file']  # 从表单的file字段获取文件，file为该表单的name值
    if f:
        fname = f.filename
        ext = fname.rsplit('.', 1)[1]  # 获取文件后缀
        unix_time = int(time.time())
        new_filename = str(unix_time) + '.' + ext  # 修改文件名
        f.save(os.path.join(app.config['UPLOAD_FOLDER'], new_filename))  # 保存文件到upload目录
        return jsonify({"success": True, "msg": "文件上传成功!"})
    return jsonify({"success": False, "msg":"文件上传失败！未找到文件"})

def init(conf):
    app.manager = Manager(conf)
    ext_api.manager = app.manager

if __name__ == '__main__':
    # ext_api.manager = app.manager
    conf = 'conf/edgeplat.yml'
    init(conf)
    app.run(debug=False, host='0.0.0.0', port=9000)
