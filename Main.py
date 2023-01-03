
import socket,json, time, yaml,logging, os
import traceback
from Manager import Manager
from flask import Flask, jsonify, request
from ManagerExt import ext_api
from AgentHelper import AgentHelper

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

agentHelpers = {}

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
    if 'starting' in app.config:
        return {"success": False, "msg": "Already starting!"}
    app.config["starting"] = True
    debug = request.args.get('debug')
    conf = request.args.get('conf')
    request_param = request.get_json()
    logging.debug("Request body: {}".format(request_param))
    result = doStop(conf, debug)
    result = doStart(conf, request_param, debug)
    del app.config['starting']
    return result

@app.route("/register", methods=["POST"])
def register():
    logging.debug("Register an agent........")
    request_json = request.get_json()
    logging.debug("Agent params: {}".format(request_json))
    ip = request_json['agent_ip']
    agentHelper = AgentHelper()
    agentHelper.parseConfig(request_json)
    agentHelpers[ip] = agentHelper
    return {"success": True}

@app.route("/deploy")
def deploy():
    logging.debug("Begin deploy!")
    try:
        conf = request.args.get('conf')
        if not conf:
            conf = 'edgeplat'
        init('conf/' + conf + '.yml')
        app.manager.deploy(agentHelpers)
    except Exception as e:
        traceback.print_exc()
        return {"success": False, "msg": str(e)}
    return {"success": True}

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
        os.system("su - ci "+app.config['UPLOAD_FOLDER']+"/update.sh "+new_filename)
        return jsonify({"success": True, "msg": "文件上传成功!"})
    return jsonify({"success": False, "msg":"文件上传失败！未找到文件"})

@app.route('/monitor/deploy',methods = ['GET', 'POST'], strict_slashes=False)
def monitor_deploy():
    conf = request.args.get('conf')
    try:
        if conf:
            manager = Manager('conf/'+conf+'.yml')
            manager.deploy_monitor(agentHelpers)
        return {"success": True}
    except Exception as e:
        traceback.print_exc()
        return {"success": False, "msg": str(e)}

@app.route('/halcon/threshold/modify',methods = ['POST'])
def halcon_threshold_modify():
    conf = {}
    conf['0-seal_skew'] = 2
    conf['1-tooth_skew'] = 1
    conf['4-seal_skew'] = 3
    request_json = request.get_json()
    face = request_json['face']
    type = request_json['type']
    threshold = request_json['threshold']
    print("face: {}, type: {}".format(face, type))
    conf_file = '/home/ubuntu/work/models/10000/'+str(face)+'_config.json'
    try:
        with open(conf_file, 'rb') as f:
            params = json.load(f)
            print(params["area"][conf[str(face)+'-'+str(type)]]["matchFuction"]["ncc_standScore"])
            params["area"][conf[str(face)+'-'+str(type)]]["matchFuction"]["ncc_standScore"] = str(threshold)
            with open(conf_file, 'w') as r:
                # 将params写入名称为r的文件中
                json.dump(params, r, indent=4)
    except Exception as e:
        return {"success": False, "msg": str(e)}

    return {"success": True}

@app.route('/halcon/threshold/get',methods = ['POST'])
def halcon_threshold_get():
    conf = {}
    conf['0-seal_skew'] = 2
    conf['1-tooth_skew'] = 1
    conf['4-seal_skew'] = 3
    request_json = request.get_json()
    face = request_json['face']
    type = request_json['type']
    print("face: {}, type: {}".format(face, type))
    conf_file = '/home/ubuntu/work/models/10000/'+str(face)+'_config.json'
    try:
        with open(conf_file, 'rb') as f:
            params = json.load(f)
            print(params["area"][conf[str(face)+'-'+str(type)]]["matchFuction"]["ncc_standScore"])
            ncc_value = params["area"][conf[str(face)+'-'+str(type)]]["matchFuction"]["ncc_standScore"]
            return {"success": True, "threshold": ncc_value}
    except Exception as e:
        return {"success": False, "msg": str(e)}

@app.route('/halcon/threshold/getall',methods = ['GET'])
def halcon_threshold_getAll():
    result = {}
    facetypes = [(0,'seal_skew'),(1,'tooth_skew'),(4,'seal_skew')]

    for face,type in facetypes:
        ncc_standScore = get_halcon_threshold(face, type)
        result[str(face)+'-'+str(type)] = ncc_standScore
    result['success'] = True
    return result

def get_halcon_threshold(face, type):
    conf = {}
    conf['0-seal_skew'] = 2
    conf['1-tooth_skew'] = 1
    conf['4-seal_skew'] = 3
    print("face: {}, type: {}".format(face, type))
    conf_file = '/home/ubuntu/work/models/10000/' + str(face) + '_config.json'
    try:
        with open(conf_file, 'rb') as f:
            params = json.load(f)
            print(params["area"][conf[str(face) + '-' + str(type)]]["matchFuction"]["ncc_standScore"])
            ncc_value = params["area"][conf[str(face) + '-' + str(type)]]["matchFuction"]["ncc_standScore"]
            return ncc_value
    except Exception as e:
        return e

def init(conf):
    app.manager = Manager(conf)
    ext_api.manager = app.manager

if __name__ == '__main__':
    conf = 'conf/edgeplat.yml'
    init(conf)
    app.run(debug=False, host='0.0.0.0', port=9000)
