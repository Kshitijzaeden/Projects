import cv2 
import face_recognition
import pickle
import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL':"https://faceattendanceinrealtime-8c72f-default-rtdb.firebaseio.com/",
    'storageBucket' : "faceattendanceinrealtime-8c72f.appspot.com"
})

foldermodepath = "Images"
PathList = os.listdir(foldermodepath)
print(PathList)
imglist = []
studentIDs= []
for path in PathList:
    imglist.append(cv2.imread(os.path.join(foldermodepath,path)))
    # print(path)
    studentIDs.append(os.path.splitext(path)[0])

     #code to send to the firebase
    fileName = f'{foldermodepath}/{path}'
    bucket = storage.bucket()
    blob = bucket.blob(fileName)
    blob.upload_from_filename(fileName)

print(studentIDs)

def findEncodings(ImagesList):
    encodings = []
    for img in ImagesList:
        img = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodings.append(encode)
    return encodings

print("encoding started")
encodingsknown = findEncodings(imglist)
encodingsknownwithIds = [encodingsknown,studentIDs]
print(encodingsknown)
print("encoding complete")

file = open("EncodeFile",'wb')
pickle.dump(encodingsknownwithIds,file)
file.close()
print("File Saved")