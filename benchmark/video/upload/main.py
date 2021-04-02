import flask, os,sys,time,json
from flask import request, send_from_directory

interface_path = os.path.dirname(__file__)
sys.path.insert(0, interface_path)  


server = flask.Flask(__name__)


#get method for downloading
@server.route('/download', methods=['get'])
def download():
    fpath = request.values.get('path', '') #read file path
    fname = request.values.get('filename', '')  #read file name
    if fname.strip() and fpath.strip():
        print(fname, fpath)
        if os.path.isfile(os.path.join(fpath,fname)) and os.path.isdir(fpath):
            return send_from_directory(fpath, fname, as_attachment=True) 
        else:
            return '{"message":"incorrect parameters!"}'
    else:
        return '{"message":"please input the parameters!"}'


# post method for uploading
@server.route('/upload', methods=['post'])
def upload():
    print('OK')
    request_data = json.load(request.files['data'])
    request_file = request.files['document']
    request_store = {
        "file_name": request_data['file_name'],
        "request_id": request_data['request_id'],
        "item": request_file
    }
    if os.path.isdir('../'+str(request_store['request_id'])) == True:
        return '{"message": "Already processing or done!"}'
    else: os.mkdir('../'+str(request_store['request_id']))
    print(request_store)
    if request_store:
        new_file_item = r'../'+str(request_store['request_id']) +'/'+ request_store['file_name']
        request_file.save(new_file_item)
        return '{"code": "ok"}'
    else:
        return '{"message": "Please first upload a file!"}'


server.run(port=10000, debug=True,host='0.0.0.0')