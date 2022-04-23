from crypt import methods
import urllib.request
from flask import Flask, jsonify, render_template, Response 
import cv2
import os
import glob
import face_recognition
from PIL import ImageOps
# Initialize the Flask app
from firebase import firebase


app = Flask(__name__)

studentID=''
studentName=''
noDoses=0
allowed='Unknown'

####

fireDB = firebase()
data = fireDB.getStudentInfo()
userinfo = {}
blacklist = fireDB.getBlackList()

print('my black {0}'.format(blacklist))
def getStudentData():
    if studentID != 'unknown':
        global studentName
        global noDoses
        global allowed
        global userinfo
        for doc in data:
            if doc.id==studentID:
                  userinfo = doc.to_dict()
             

        studentName = userinfo['name']
        noDoses=userinfo['numberOfDoses']
        if noDoses>=2:
            allowed='Yes'
        else:
            allowed='No'
# imagesUrl = userinfo['images']
# i = 0
# for item in imagesUrl:
#     if not os.path.exists('faces/{0}'.format(stud_id)):
#         os.makedirs('faces/{0}'.format(stud_id))
#     print('download')
#     urllib.request.urlretrieve(item, f'faces/{stud_id}/' + stud_id + '{0}'.format(i) + '.jpg')
#     i += 1
#     print('success'+str(i))

# print('done'+str(i))

fireDB.getTrainImages()

#
# ####
camera = cv2.VideoCapture(0)

cv2.VideoCapture(0)
###
known_faces = []
known_names = []
known_faces_paths = []

registered_faces_path = 'faces/'
for name in os.listdir(registered_faces_path):
    images_mask = '%s%s/*' % (registered_faces_path, name)
    images_paths = glob.glob(images_mask)
    for imgpath in images_paths:
        print(type(imgpath))
        image = face_recognition.load_image_file(imgpath)
        try:
            encoding = face_recognition.face_encodings(image)[0]
            known_faces.append(encoding)
            known_names.append(name)
        except IndexError as e:
            print(e)

###

def gen_frames():
    while True:
        success, frame = camera.read()  # read the camera frame
        if not success:
            break
        else:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            faces = face_recognition.face_locations(frame_rgb)
            # top,right,bottm,left
            cloneStudentID=''
            global allowed
            for face in faces:
                top, right, bottom, left = face
              
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                encoding = face_recognition.face_encodings(frame_rgb, [face])[0]

                results = face_recognition.compare_faces(known_faces, encoding)
                global studentName
                global noDoses
                global allowed
                global blacklist
                if any(results):
                    global studentID
                    studentID = known_names[results.index(True)]
                    if cloneStudentID != studentID:
                         getStudentData()
                         cloneStudentID=studentID
                         if allowed=='No':
                             print('Added to black list')
                             fireDB.addToBlackList(studentID)
                             blacklist = fireDB.getBlackList()
                else:
                    studentID = 'unknown'
                    studentName= 'unknown'
                    noDoses = 0
                    allowed = 'unknown'
                
                print('hi '+str(studentID))
                cv2.putText(frame, studentID, (left, bottom + 20), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 2)
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result



@app.route('/')
def index():
    return render_template('index.html')


@app.route('/video_feed')
def video_feed():
    
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')



@app.route('/userinfo',methods=['POST'])
def userinfo():

    return jsonify('',render_template('userinfo.html',ID=studentID,Name=studentName,NoDoses=noDoses,Allowed=allowed,blacklist=blacklist))



if __name__ == "__main__":
    app.run(debug=True)
