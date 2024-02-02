import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL':"https://faceattendanceinrealtime-8c72f-default-rtdb.firebaseio.com/",
    'storageBucket': "faceattendanceinrealtime-8c72f.appspot.com"
})

ref = db.reference("Students") #makes a directory

#now we will add the data
data = {
    "321654":
    {
        "name":"Murtaza Hasaan",
        "major":"robotics",
        "starting_year":2017,
        "attendence": 6,
        "standing":"G",
        "year": 4,
        "last_attendence_time": "2022-12-11 00:54:34"    
    },

    "852741":
    {
        "name":"Emily Blunt",
        "major":"Acting",
        "starting_year":2014,
        "attendence": 12,
        "standing":"G",
        "year": 2,
        "last_attendence_time": "2022-12-11 00:51:34"    
    },

    "963852":
    {
        "name":"Elon Musk",   #you can change the parameters according to your testing
        "major":"Scientist",
        "starting_year":2014,
        "attendence": 15,
        "standing":"G",
        "year": 3,
        "last_attendence_time": "2022-12-11 00:44:34"   #time will be automatically updated from main code 
    }
}


#sending the data to database:
for key,value in data.items():
    ref.child(key).set(value)#sending the value to db