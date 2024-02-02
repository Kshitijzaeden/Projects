import cv2
import os
import datetime as datetime
import numpy as np
import face_recognition
import pickle
import cvzone
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage


cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL':"https://faceattendanceinrealtime-8c72f-default-rtdb.firebaseio.com/",
    'storageBucket' : "faceattendanceinrealtime-8c72f.appspot.com"
})

bucket = storage.bucket()

cap = cv2.VideoCapture(0)
cap.set(1, 640) #width (Graphics)
cap.set(2, 480)  #height

imgBackground = cv2.imread("Resources/background.png")

foldermodepath = "Resources/Modes"
ModePathList = os.listdir(foldermodepath)
imgModelist = []
for path in ModePathList:
    imgModelist.append(cv2.imread(os.path.join(foldermodepath,path)))

# print(len(imgModelist))
    
#load the encoding file
print("Loading the encoding....")
file = open("EncodeFile",'rb')
encodingsknownwithIds = pickle.load(file)
file.close()
encodingsknown,studentIDs = encodingsknownwithIds
print("Encode file loaded")

modeType=0
counter=0
id = -1
imgStudent = []

while True:
    success, img = cap.read()

    imgS=cv2.resize(img,(0,0),None, 0.25,0.25)
    imgS=cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    #location of the images 
    faceCurFrame = face_recognition.face_locations(imgS)
    encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)

    imgBackground[162:162+480,55:55+640] = img 
    imgBackground[44:44+633,808:808+414] = imgModelist[modeType] 

    #comparing with the generated encodings whether they are matching or not
    if faceCurFrame:
        for encodeface, faceLoc in zip(encodeCurFrame, faceCurFrame):
            matches = face_recognition.compare_faces(encodingsknown, encodeface)
            facedistance = face_recognition.face_distance(encodingsknown, encodeface)

            print("matches",matches)
            print("facedistance",facedistance)

            matchIndex = np.argmin(facedistance)
            # print("Match Index", matchIndex)

            if matches[matchIndex]:
                # print("Known Face Detected...")
                y1, x2, y2, x1 = faceLoc
                y1, x2, y2, x1 = y1*4, x2*4, y2*4, x1*4
                bbox = 55 + x1, 162 + y1, x2-x1, y2-y1
                imgBackground=cvzone.cornerRect(imgBackground, bbox, rt=0)
                id = studentIDs[matchIndex]#if the face is matched the student ids will be saved invariable id
                if counter == 0:
                    cvzone.putTextRect(imgBackground,"Loading",(275,400))
                    cv2.imshow("Attendence",imgBackground)
                    cv2.waitKey(1)
                    counter = 1
                    modeType = 1

                if counter ==0:
                    counter=1
                    modeType=1

        if counter !=0:

            if counter==1:  #once we have the first iteration we will download from the next line
                #get the data
                studentInfo = db.reference(f'Students/{id}').get()
                print(studentInfo)
                #get the image from the storage
                blob = bucket.get_blob(f'Images/{id}.png')
                array = np.frombuffer(blob.download_as_string(), np.uint8)
                imgStudent = cv2.imdecode(array, cv2.COLOR_BAYER_BG2BGR)


                #updating the data of attendence
                datetimeObject = datetime.strtime(studentInfo['last_attendence_time'],"%Y-%m-%D %H-%M-%S ")
                secondsElapsed = (datetime.now() - datetimeObject).total_seconds()
                print(secondsElapsed)
                
                if secondsElapsed<30:
                    ref = db.reference(f'Students/{id}')
                    studentInfo['attendence'] +=1
                    ref.child('attendence').set(studentInfo['attendence'])  #we need to update it with these values
                    ref.child('last_attendence_time').set(datetime.now().strftime("%Y-%m-%D %H-%M-%S "))
                else:
                    modeType = 3
                    counter = 0
                    imgBackground[44:44+633,808:808+414] = imgModelist[modeType] 

            if modeType!=3:

                if 10<counter<20:
                    modeType =2

                imgBackground[44:44+633,808:808+414] = imgModelist[modeType] 

                if counter <= 10:
                    cv2.putText(imgBackground,str(studentInfo['attendence']),(861,125),cv2.FONT_HERSHEY_COMPLEX, 1, (255,255,255), 1)
                    cv2.putText(imgBackground, str(studentInfo['major']), (1006, 550),cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                    cv2.putText(imgBackground, str(id), (1006, 493),cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                    cv2.putText(imgBackground, str(studentInfo['standing']), (910, 625),cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
                    cv2.putText(imgBackground, str(studentInfo['year']), (1025, 625),cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
                    cv2.putText(imgBackground, str(studentInfo['starting_year']), (1125, 625),cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)

                    (w, h), _ = cv2.getTextSize(studentInfo['name'],cv2.FONT_HERSHEY_COMPLEX,1,1)
                    offset = (414-w)//2
                    cv2.putText(imgBackground, str(studentInfo['name']), (808, 445),
                                            cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 50), 1)
                    
                    imgBackground[175:175+216,909:909+16] = imgStudent

                counter+=1

                if counter >=20:
                    counter = 0
                    modeType = 0
                    studentInfo = []
                    imgStudent = []
                    imgBackground[44:44+633,808:808+414] = imgModelist[modeType] 
    
    else:
        modeType = 0




    cv2.imshow("Web Camera",img)
    cv2.imshow("Attendence",imgBackground)
    cv2.waitKey(1)