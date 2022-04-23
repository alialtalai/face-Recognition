import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import urllib.request
from datetime import datetime

class firebase:
    def __init__(self):
        cred = credentials.Certificate(
            "fir-9883e-firebase-adminsdk-trerk-a44467eab4.json")
        firebase_admin.initialize_app(cred)

    def getStudentInfo(self):
        db = firestore.client()
        docs = db.collection(u'users').stream()

        return docs

    def getTrainImages(self):
        db = firestore.client()
        users_ref = db.collection(u'users').stream()
        for doc in users_ref:
            userinfo = doc.to_dict()
            imagesUrl = userinfo['images']
            stud_id = doc.id
            print('user id was {0}'.format(stud_id))
            i = 0
            for item in imagesUrl:
                if not os.path.exists('faces/{0}'.format(stud_id)):
                    os.makedirs('faces/{0}'.format(stud_id))
                print('download')
                urllib.request.urlretrieve(
                    item, f'faces/{stud_id}/' + stud_id + '{0}'.format(i) + '.jpg')
                i += 1
                print('success'+str(i))

        print('done'+str(i))

    def addToBlackList(self,stud_id):
        db = firestore.client()
        now = datetime.now()
        docs = db.collection(u'users').document(stud_id).get()
        doc = docs.to_dict()
        print('black list '+doc['name'])
        data={
              u'name':doc['name'],
              u'numberOfDoses':doc['numberOfDoses'],
              u'stud_id':doc['stud_id'],
              u'date':str(now)
         }
        db.collection(u'blacklist').document(stud_id).set(data)
    
    def getBlackList(self):
        list=[]
        db = firestore.client()
        docs = db.collection(u'blacklist').stream()
        for doc in docs:
            list.append(doc.to_dict())

        return list
        
