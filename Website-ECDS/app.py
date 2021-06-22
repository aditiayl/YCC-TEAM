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
# import nltk
# from nltk.tokenize import word_tokenize
from brisque import *
# import pickle
UPLOAD_FOLDER ='static/uploads/'
DOWNLOAD_FOLDER = 'static/downloads/'
ALLOWED_EXTENSIONS = {'jpg', 'png','.jpeg'}
app = Flask(__name__, static_url_path="/static")
#app = Flask(__name__)
#App Config
app.config['SECRET_KEY'] = 'opencv'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER
# limit upload size upto 6mb
app.config['MAX_CONTENT_LENGTH'] = 6 * 1024 * 1024

# def anamnesis(test_sentence):
#     train = [('Halo dok. Sy mau tanya, mengenai lansia penderita diabetes yang sekarang mengalami gangguang penglihatan pada salah satu matanya. Dimana salah satu matanya sudah tidak dapat melihat dengan jelas (seperti kabut putih). Bagaimana cara mengatasinya ya dok ?? Kalaupun tidak ada cara untuk mengobati, apakah masih ada cara untuk mencegah agar gangguan penglihatanya tidak bertambah buruk ?? Mohon solusinya dok ??','pos'),('Selamat malam dokMaaf saya ingin bertanya,sudah dua bulan lebih mata sebelah kiri saya kadang gelap dan samar samar kepala pun terkadang terasa sakit yang amat sakit.Saya pernah mengalami kekerasan kepala saya di hantam ke dinding dan di pukul benda keras.mata saya pernah di semprot pake obat semprot utk serangga.', 'pos'),('Selamat pagi dok...saya punya ponakan,tgl 14 Januari ini usia 2bulan.saya lihat pupil matanya berwarna putih dikedua matanya...dan pada usia ini belum sama sekali melihat apa yang ada didepannya ( mata seperti mencari-cari terus menerus)...sejak lahir sampai sekarang rewel,hanya diam bila diayun dengan ayunan kuat..saya khawatir dia mengalami gangguan penglihatan dok...mohon solusi tindak lanjut apa dok.. terimakasih...', 'pos'),('Dok saya mau tanya ini nenek saya mata nya sebelah seperti terbelalak dok dan sangat silau untuk melihat ,terus diputaran kornea nya seperti ada lingkaran berna putih .','pos'),('DOK,saya mengalami mata katarak sejak lahir,dan mata saya sebelah kiri mengecil dan sudah tidak dapat melihat dan mata yg di sebelah kanan juga sudah tidak terlalu terang dalam penglihatan sejak SD.waktu itu pernah ke doker,ttpi dokter menggatakan klo mata saya ini Katarak dalam,Bisa di operasi tetapi tidak akan terang lagi...Saya sudah tidak terlalu berharap ke mata yg sebelah kiri saya karena dokter bilang cmn sdkit kemungkinan untuk sembuh...Saya hanya inggin bertanya apa bisa mata kanan saya sembuh?terang seperti yang lain?agar saya bisa melalukan operasi pada mata kanan saya.Saya bertanya sprti ini karena saya tidak terlalu cukup dgn 1 dokter mata.TeriMakasi','pos'),('Halo dok, usia saya baru 18 tahun. Dalam beberapa kesempatan penglihatan saya sering terganggu dok, seperti ada cahaya terang yang melingkupi mata saya umumnya di ujung ujung mata kanan dan kiri. Suatu waktu saya pernah memeriksakan kondisi saya ke rumah sakit dan dokter nya berkata bahwa ada penipisan yang terjadi pada retina mata saya, kemudian saya di beri resep obat tetes mata. Ketika saya cari itu obat apa, ternyata itu obat katarak. Jika saya boleh tau, katarak saya ini termasuk katarak jenis apa ya dok? Dan bagaimana penanganan yang paling tepat. Terimakasih dok.','pos'),('Halo dok saya mau bertanya tentang mata, kenapa ya mata saya kabur sebelah lebih tepatnya mata sebelah kiri,terima kasih dok telah menjawab','pos'),('dok, saya mempunyai paman dengan penyakit kehilangan penglihatan akibatsaraf mata bagian belakang. untuk gejala hampir mirip dengan neuritis optik. belakangan ini paman saya jadi lebih sering sakit kepala hingga kemata, biasanya berobat ke malaysia tapi dengan kondisi saat ini dia tidak bisa untuk berobat kesana. mohon infonya untuk dokter syaraf mata yg bisa saya kunjungi di daerah sumatera barat dimana ya dok?','pos'),('Dok saya mau tanya, temen saya ada keluhan tentang matanya, kalau melihat sumber cahaya seperti lampu atau lainnya, di tengahnya gelap sedangkan di pinggirannya bercahaya seperti gerhana matahari, itu kenapa ya dok?Terima kasih','pos'),('Selamat Siang Dokter, saya mau bertanya kornea mata sebelah kanan saya berubah warna ke abu-abuan dan penglihatan saya sangat kabur hanya disebelah mata saya,, itu efek apa ya dokter? cara untuk mengatasinya gimana ya dokter? apakah dari makanan atau harus pakai kacamata? Mohon tanggapannya Dokter. Terima Kasih','pos'),('Dok, mata sebelah kiri ibu saya sekitar 4 tahun yg lalu di vonis glaukoma, dan akhir nya dioperasi.. Cuman sekarang yg sebelah kanan mulai kabur dok, kadang2 bahkan tidak bisa melihat sama sekali.. Apakah mungkin mata kanan nya juga glaukoma do?','pos'),('Maaf dok mau bertanya Kedua bola mata saya ada lapisan putih gtuh ada dua lapisan.,Penyebab terjadi ada lapisan putih kenapa ya dok','pos'),('dok bapak saya habis operasi katarak, lalu di kasih obat Methylprednisolone itu gimana dok???','pos'),('Halo dok,jadi mata saya ada min yang kiri 4 yang kanan 2,terus tadi pagi saya ngerasa kalau mata saya tiba² buram dan setiap ngeliat ke cahaya saya melihat seperti lingkaran pelangi,awalnya saya biarkan tapi lama² mata saya menjadi nyut²an dan membuat kepala saya ikutan sakit,terus lama² saya mual dan muntah². Itu kenapa ya dok?','pos'),('Halo dokter saya mau tanya..orang tua saya, sehari setelah operasi katarak ada gelembung angin pada daerah retinanya.Apakah hal tersebut wajar dan akan hilang sendirinya?','pos'),('Dok mau tanya, apakah bisa lensa kacamata tebel bisa jadi tipis tapi dengan ukuran minus yang sama??','neg'),('Dok saya mata minus 7,5 silinder 2, apakah saya bisa melahirkan secara caesar? Dan apakah akan berpengaruh dengan kehamilan saya ? Terima kasih sebelumnya','neg'),('Alodokter..Awal bulan lalu saya membuat kacamata baru.. Dari ukurannya memangvterjadi kenaikan drastis.. Dari minus 5 jd minus 10 silindris 2.. Awalnya memang pusing dok, tp lama2 mulai terbiasa.. Tp makin ksini saya suka merasakan klo otot mata saya sperti tertarik.. Bahkan yg terakhir hingga terasa kebas dan tidak terasa diraba di bagian kelopak mata.. Saking tdk tahan saya putuskan untuk memakai kacamata lama.. Yg ingin saya tanyakan, apakah kenaikan minus disertai silinder yg langsung silindris 2 itu normal? Krn saya hanya merasa terang tp msh sulit membaca tulisan kecil walaupun dekat. Apakah mungkin optik melakukan kesalahan dalam menulis resep, khususnya mengenai silindrisnya?Mohon penjelasannya, terimakasih..','neg'),('Dok, apakah tetes mata softlens merk O2 hanya bisa di gunakan oleh mata minus dan silinder? Gak bisa dipakai oleh mata normal?','neg'),('dok saya mau tanya, saya orangnya sulit berkonsentrasi, saat meeting buyar fikiran saya,penglihatan remang apalagi kalau di sore hari , saya sudak cek mata dan hasilnya slinder 2 , kira kira penyakit apa ya dok ?','neg'),('Mlm dok, saya jg mau nanya, sekrng saya memasuki umur 25th .akhir2 ini mata saya klo liat tulisan agak jauh dikit ga jelas? Apa itu rabun jauh? Bagaimana solusinya? Terimakasih','neg'),('Allow dokter,,,selamat pagi saya Rossa usia 25 th,,,ini kehamilan pertama saya,,,usia kehamilan 35w 5d ,,, saya sudah konsultasi ke 3 dokter bahwa saya harus melahirkan secara operasi caesar karna mata saya minus 7,hb saya jg 10,2 tergolong rendah,saya juga ambeyen ,,,, dg kondisi saya seperti itu apakah memang dan harus melahirkan secara operasi ??? Terimaksih','neg'),('Dok saya mau tanya apakah dengan mengkonsumsi vitamin A dan istirahat yang cukup secara rutin bisa membantu mengurangi mata minus?','neg'),('Dok , hari ini saya periksa mata di optik . usia saya sekarang 21 tahun dan saya baru pertama kali mengecheck kondisi mata saya .Karena di kampus, saya sudah susah melihat tulisan dari proyektor seperti berbayang gitu . Hasil dari optik kanan 1,2 dan kiri 1,5 . saya ingin bertanya? Apakah ada cara lain untuk mengurangi minus mata saya? Apakah benar jika gunakan kacamata minus bertambah/berkurang dari teman-teman yang memberi tahu saya . Apakah ada cara alami mengurangi minus dok? Minum jus wortel setiap hari/ baca al-quran bisa mengurangi minus mata . Thankyu dok','neg'),('Hallo dok.. saya eki dok, saya mau tanya saya kan kena mata minus kenapa ya dok kalo pakai kacamata mata saya terasa perih tapi kalau dilepaskan rasa perih nya hilang.. kira kira itu kenapa ya??? Terima kasih dok sebelumnya','neg'),('Dokter, saya berniat memakai softlens khusus minus saja dg pemakaian >8jam,tetapi kedua mata saya minus 5 dan silender 2. Bagaimana baiknya dok? Terimakasih','neg'),('Selamat pagi dok, saya Dimiana. Mau bertanya, saya bermata minus 1 sering ngrsa matanya cape KLO brhdpan dgn komputer terlalu lama, setiap ngrsa cape saya menggunakan Alcon tears naturalle 2, Shri bisa 2x pmkaian, skli pakai 1 tetes ATW 2. Apakah beresiko jika penggunaan nya dlm waktu lama? Lensa apa yg cocok untuk mata saya? Terimakasih','neg'),('Selamat malam dok saya aldi umur saya 20 tahun gini dok saya penderita mata rabun jauh apa ya obat untuk mata saya ini biar penglihatannya membaik dok??','neg'),('Dok kalo mata minus masuk jurusan kesehatan kayak anestesi bisa nggak dok? Saya takut hanya karena saya minus saya nggak bisa masuk di anestesi. Makasih dok.','neg'),('pagi dok, saya memiliki mata minus ,saya punya dua kacamata minus yg sesuai dengan minus saya, saya sering ganti" 2 kacamata itu,apa tidak berbahaya? Atau harus memakai 1 kacamata saja?','neg')]

#     global passage
#     all_words = set(word.lower() for passage in train for word in word_tokenize(passage[0]))
#     t = [({word: (word in word_tokenize(x[0])) for word in all_words}, x[1]) for x in train]
#     classifier = nltk.NaiveBayesClassifier.train(t)

#     # f = open('alodokter_data.pickle', 'wb')
#     # pickle.dump(classifier, f)
#     # f.close()
#     # f = open('alodokter_data.pickle', 'rb')
#     # classifier = pickle.load(f)
#     # f.close()
#     test_sent_features = {word: (word in word_tokenize(test_sentence.lower())) for word in all_words}
#     classifier.show_most_informative_features()
#     return classifier.classify(test_sent_features)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/',methods=['GET'])
def index():
    return render_template("index(edited).html",font_url='https://fonts.googleapis.com/css?family=Open+Sans:300,300i,400,400i,600,600i,700,700i|Raleway:300,300i,400,400i,500,500i,600,600i,700,700i|Poppins:300,300i,400,400i,500,500i,600,600i,700,700i')

@app.route('/submission',methods=['GET','POST'])
def upload():
    if request.method == 'POST':
        global new_xc
        global new_yc
        global new_wc
        global new_hc
        new_xc = request.form['xc']
        new_yc = request.form['yc']
        new_wc = request.form['wc']
        new_hc = request.form['hc']
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
            # print("FILE ALAMAT :")
            # print(os.path)
            extension = filename.split(".")[1]
            #extension = str(extension[1])
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
            # print(anamnesis(request.form['anamnesis']),file=sys.stderr)
            # if anamnesis(request.form['anamnesis'])=='pos':
            #     res_anamnesis = 1
            # else :
            #     res_anamnesis = 0

            if ameri==1 :
                flash("Congratulations! Your eye is relatively healthy. You should do the following to reduce the chance of developing cataracts :\n\n- Perform routine eye examinations \n- Protect your eyes from UVB rays by wearing sun glasses outside \n- Eat fruits and vegetables that contain antioxidants and maintain a healthy weight \n- Stop smoking \n- Take care of diabetes and other medical conditions","medadvice")
                flash("Normal","class")
            elif ameri==2 :
                strcatarr = ["Sorry that your eye is detected to have ",str(str_detection), ". The opacity of your eye is ", str(opacification)," %. ",str(str_detection)," is ", strdefine,"Please do further medical examination and have a nice day!"]
                strcat = "".join(strcatarr)
                str_advice = strcat
                flash(str_advice,"medadvice")
                flash("Cataract","class")
            elif ameri==3 :
                strcatarr = ["Sorry that your eye is detected to have ",str(str_detection), " cataract. The opacity of your eye is ", str(opacification)," %. ",str(str_detection)," cataract is ", strdefine,"Please do further medical examination and have a nice day!"]
                strcat = "".join(strcatarr)
                str_advice = strcat
                flash(str_advice,"medadvice")
                flash("Cataract","class")

            if img_score > 39:
            #     if (ameri==1 and res_anamnesis==1) or ((ameri==2 or ameri ==3) and res_anamnesis==0):
            #         flash('Your symptomps and pupil classification are not matched, so this result only faint predidiction! and The image quality is poor. The result maybe incorrect. Please write more symptoms, read image requirements, or select another image!',"NB")
            #     else:
            #         flash('The image quality is poor. The result maybe incorrect. Please read image requirements or select another image!',"NB")
                strimquality = "".join(["Poor (",str(img_score)," BRISQUE Score)"])
                flash(strimquality,"imgquality")
            else :
            #     if (ameri==1 and res_anamnesis==1) or ((ameri==2 or ameri ==3) and res_anamnesis==0):
            #         flash('Your symptomps is blank or not matched with pupil classification, so this result only faint predidiction! Please write more symptoms.',"NB")
                strimquality = "".join(["Good (",str(img_score)," BRISQUE Score)"])
                flash(strimquality,"imgquality")

            # if ameri!=5:
            #     firebasedata = filename
            #     pathlocal = 'static/uploads/' + filename
            #     storage.child(firebasedata).put(pathlocal)
            #     detected=str_detection
            #     detection=[detected]
            #     gsheet.insert_row(detection,2)
            # print(),file=sys.stderr)
            return render_template("submissioncompleted.html", data=data)
    else:
        return render_template("submission.html")


def process_file(path, filename):
    detect_object(path, filename)


def detect_object(path, filename):
    global ameri

    # pupil = cv2.CascadeClassifier("ssd/pupil.xml")
    font = cv2.FONT_HERSHEY_SIMPLEX
    upload_img = cv2.imread(path)
    
    input_img = upload_img.copy()
    gray_img1 = cv2.cvtColor(input_img,cv2.COLOR_BGR2GRAY)
    # equ = cv2.equalizeHist(gray_img1)
    # res = np.hstack((gray_img1,equ))
    # gray_img = res

    global new_xc
    global new_yc
    global new_wc
    global new_yc

    x_max2_w = int(float(new_xc))
    y_max2_w = int(float(new_yc))

    x2_max2_w = int(float(new_xc) + float(new_wc))
    y2_max2_w = int(float(new_yc) + float(new_hc))

    global str_detection
    pupil_detected = True
    if pupil_detected:
        croped_img2 = gray_img1[y_max2_w:y2_max2_w, x_max2_w:x2_max2_w]
        brisq = brisque.BRISQUE()
        median_img = cv2.medianBlur(croped_img2, 3)

        global img_score
        img_score = float("{0:.2f}".format(brisq.get_score(input_img)))
        # print(img_score, file=sys.stderr)

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
            str_detection = "Imature Cataract"
            strdefine = " a cataract characterized by a variable amount of opacification, present in certain areas of the lens. "
            ameri=2
        else:
            str_detection = "Mature Cataract"
            strdefine = " a cataract that is opaque, totally obscuring the red reflex. It is either white or brunescent. "
            ameri=3
    else:
        str_detection = "Pupil Undetected"
        ameri=4
    
    if(float(new_wc)>=16) :
        cv2.rectangle(input_img, (x_max2_w, y_max2_w), (x2_max2_w, y2_max2_w), (255, 0, 0), int(float(new_wc)/16))
        #cv2.putText(input_img, str_detection, (x_max2_w-int(float(new_wc)/2), y_max2_w - 2), font, float(new_wc)/100, (255, 0, 0), int(float(new_wc)/16))
    else :
        cv2.rectangle(input_img, (x_max2_w, y_max2_w), (x2_max2_w, y2_max2_w), (255, 0, 0), 2)
        #cv2.putText(input_img, str_detection, (x_max2_w-int(float(new_wc)/2), y_max2_w - 2), font, 0.38, (255, 0, 0), 2)
    cv2.imwrite(f"{DOWNLOAD_FOLDER}{filename}", input_img)
if __name__ == '__main__':
    # app.secret_key = "^A%DJAJU^JJ123"
    app.run(debug=True)
