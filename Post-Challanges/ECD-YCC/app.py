import os
from flask import *
from werkzeug.utils import secure_filename
import bcrypt
import cv2
import numpy as np
import imutils #For Translation, Rotation, Resizing, and Skeletonization
import math #Operates Funcions
import sys
import random
import string
from brisque import *
from twilio.rest import Client

UPLOAD_FOLDER ='static/uploads/'
DOWNLOAD_FOLDER = 'static/downloads/'
ALLOWED_EXTENSIONS = {'jpg', 'png','.jpeg'}
app = Flask(__name__, static_url_path="/static")
app.config['SECRET_KEY'] = 'opencv'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 6 * 1024 * 1024
app.secret_key = 'otp'
global otp
otp = 0

global s
s = 1

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/',methods=['GET'])
def index():
    return render_template("index(edited).html",font_url='https://fonts.googleapis.com/css?family=Open+Sans:300,300i,400,400i,600,600i,700,700i|Raleway:300,300i,400,400i,500,500i,600,600i,700,700i|Poppins:300,300i,400,400i,500,500i,600,600i,700,700i')

@app.route('/register')
def register():
    global otp
    global s
    if otp == s:
        return render_template("submission.html")
    else :
        return render_template("register.html")

@app.route('/getOTP', methods = ['POST'])
def getOTP():
    global fullname
    number = request.form['number']
    fullname = request.form['Name']

    val = getOTPApi(number)
    if val:
        return render_template('enterOTP.html')

def generateOTP():
    return  random.randrange(100000,999999)

def getOTPApi(number):
    account_sid = 'ACccf57caa01b158681f5600c620b05ded'
    auth_token = '4e4a89393f64b478583cf54812f57c1b'
    client = Client(account_sid, auth_token)
    otp = generateOTP()
    session['response'] = str(otp)
    body = 'Your OTP is ' + str(otp)
    message = client.messages.create(
        from_='+15717891190', 
        body=body, 
        to=number
        )
    if message.sid:
        return True
    else:
        False

@app.route('/validateOTP', methods = ['POST'])
def validateOTP():
    global otp
    otp = request.form['otp'] 
    if 'response' in session:
        global s
        s = session['response']
        session.pop('response', None)
        if s == otp:
            flash(fullname,"fullname")
            return render_template('submission.html')
        else:
            return render_template('enterOTP.html')

@app.route('/submission',methods=['GET','POST'])
def upload():
    if request.method == 'POST':

        if 'file' not in request.files:
            flash('No file attached in request')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No file selected')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, filename))

            extension = filename.split(".")[1]

            strname = "".join(random.choices(string.ascii_uppercase + string.digits, k=4))

            source = UPLOAD_FOLDER + "/" + filename
            destination = UPLOAD_FOLDER + "/" + strname + "." + extension

            os.rename(source, destination)
            filename = strname + "." + extension
            process_file(os.path.join(UPLOAD_FOLDER, filename), filename)

            data = {
                "processed_img": 'static/downloads/' + filename,
                "uploaded_img": 'static/uploads/' + filename
            }

            global opacification
            global strdefine
            global str_detection
            global ameri
            global fullname
            global img_score

            flash(fullname,"fullname")
            if ameri==1 :
                flash("Congratulations! Your eye is relatively healthy. You should do the following to reduce the chance of developing cataracts :\n\n- Perform routine eye examinations \n- Protect your eyes from UVB rays by wearing sun glasses outside \n- Eat fruits and vegetables that contain antioxidants and maintain a healthy weight \n- Stop smoking \n- Take care of diabetes and other medical conditions","medadvice")
                flash(str_detection,"class")
            elif ameri==2 :
                strcatarr = ["Sorry that your eye is detected to have cataract. The opacity of your eye is ", str(opacification)," %. ","Imature cataract"," is ", strdefine,"Please do further medical examination and have a nice day!"]
                strcat = "".join(strcatarr)
                str_advice = strcat
                flash(str_advice,"medadvice")
                flash(str_detection,"class")
            elif ameri==3 :
                strcatarr = ["Sorry that your eye is detected to have cataract. The opacity of your eye is ", str(opacification)," %. ","Mature cataract"," cataract is ", strdefine,"Please do further medical examination and have a nice day!"]
                strcat = "".join(strcatarr)
                str_advice = strcat
                flash(str_advice,"medadvice")
                flash(str_detection,"class")

            if img_score > 39:

                strimquality = "".join(["Poor (",str(img_score)," BRISQUE Score)"])
                flash(strimquality,"imgquality")
            else :

                strimquality = "".join(["Good (",str(img_score)," BRISQUE Score)"])
                flash(strimquality,"imgquality")


            return render_template("submissioncompleted.html", data=data)
    else:
        return render_template("submission.html")


def process_file(path, filename):
    detect_object(path, filename)


def detect_object(path, filename):
    global ameri

    pupil = cv2.CascadeClassifier("ssd/pupil.xml")
    font = cv2.FONT_HERSHEY_SIMPLEX
    upload_img = cv2.imread(path)
    
    input_img = upload_img.copy()
    gray_img1 = cv2.cvtColor(input_img,cv2.COLOR_BGR2GRAY)

    global str_detection
    width = 300
    height = int(upload_img.shape[0] * 300/upload_img.shape[1])
    dimension = (width, height)
    input_img = cv2.resize(upload_img, dimension, interpolation = cv2.INTER_AREA)

    gray_img = cv2.cvtColor(input_img, cv2.COLOR_BGR2GRAY) 

    max_w = 0
    max_w_index = 0
    pupil_detected = False

    pupils_detected = pupil.detectMultiScale3(
            gray_img,
            scaleFactor=1.1,
            minNeighbors=3,
            minSize=(10, 10),
            flags = cv2.CASCADE_SCALE_IMAGE,
            outputRejectLevels = True
        )

    rects_pupils = pupils_detected[0]
    weights_pupils = pupils_detected[2]

    index = -1
    
    x_max2_w = 25
    y_max2_w = 25
    
    x2_max2_w = 0
    y2_max2_w = 0

    for (x,y,w,h) in rects_pupils:
        index = index + 1
        
        if (weights_pupils[index] > max_w):
            max_w_index = index
            pupil_detected = True
            x_max2_w = x
            y_max2_w = y

            x2_max2_w = x + w
            y2_max2_w = y + h

    cv2.rectangle(input_img,(x_max2_w,y_max2_w),(x2_max2_w,y2_max2_w),(0,255,255),2)
    madvice_result = 2

    if pupil_detected :
        croped_img2 = input_img[y_max2_w:y2_max2_w,x_max2_w:x2_max2_w]
        brisq = brisque.BRISQUE()
        median_img = cv2.medianBlur(croped_img2, 3)

        global img_score
        img_score = float("{0:.2f}".format(brisq.get_score(input_img)))

        mean_img = cv2.mean(median_img)[0]

        global opacification
        opacification = float("{0:.2f}".format(100*mean_img/255))

        result_Regresi = 0.918183201 + (0.0127839853 * mean_img)

        global str_detection
        global strdefine
        if (result_Regresi >= 0 and result_Regresi < 1.5):
            str_detection = "Normal"
            ameri=1
        elif (result_Regresi >= 1.5 and result_Regresi < 2.5):
            str_detection = "Cataract"
            strdefine = " a cataract characterized by a variable amount of opacification, present in certain areas of the lens. "
            ameri=2
        else:
            str_detection = "Cataract"
            strdefine = " a cataract that is opaque, totally obscuring the red reflex. It is either white or brunescent. "
            ameri=3
    else:
        str_detection = "Pupil Undetected"
        ameri=4
    

    cv2.imwrite(f"{DOWNLOAD_FOLDER}{filename}", input_img)
if __name__ == '__main__':
    app.run(debug=True)
