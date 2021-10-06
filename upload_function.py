from flask import Flask,render_template,request,redirect,url_for,make_response,jsonify, Response
from werkzeug.utils import secure_filename
import os,cv2,time,sys
from datetime import timedelta
import numpy as np
img_size=[100,100]
last_frame=None
video_alive=False
upload_path=''
#File formats allowed to upload
ALLOWED_EXTENSIONS = {'png', 'jpg', 'JPG', 'PNG', 'bmp','mp4','ts'}
def gen():
    i=1
    while i<10:
        yield (b'--frame\r\n'
            b'Content-Type: text/plain\r\n\r\n'+str(i)+b'\r\n')
        i+=1

def get_frame(upload_path):

    camera_port=0

    ramp_frames=100
    camera = cv2.VideoCapture(upload_path)
    size = (int(camera.get(cv2.CAP_PROP_FRAME_WIDTH)/2), int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT)/2))
    i=1
    while True:
        retval, im = camera.read()
        if retval:
            im = cv2.resize(im, size)
            imgencode=cv2.imencode('.jpg',im)[1]
            stringData=imgencode.tostring()
            yield (b'--frame\r\n'
                b'Content-Type: text/plain\r\n\r\n'+stringData+b'\r\n')
            i+=1
        else:
            camera.release()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

app = Flask(__name__)

app.send_file_max_age_default = timedelta(seconds=1)


@app.route('/', methods=['POST', 'GET'])
def upload():
    if request.method == 'POST':
        f = request.files['file']
        if not (f and allowed_file(f.filename)):
            return jsonify({"error": 1001, "msg": "we can only upload png、PNG、jpg、JPG、bmp、ts"})

        user_input = request.form.get("name") 

        
        global upload_path  
        basepath = os.path.dirname(sys.argv[1])  # input a path in the terminal, and it will be the path we load the file
        global upload_path 
        upload_path = os.path.join(basepath, f.filename)
        print ("name is %s, path is %s"%(f.filename,upload_path))
        f.save(upload_path)
        print ("finished upload")
        return render_template('after_upload.html', userinput=user_input, val1=time.time())
       

    return  render_template('before_upload.html')

@app.route('/video_feed')
def video_feed():
    return Response(get_frame(upload_path), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(debug=True)
    
