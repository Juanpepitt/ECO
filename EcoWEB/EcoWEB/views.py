from django.shortcuts import render
import pyrebase

config={
    "apiKey": "AIzaSyDuSSwDlasTMzZFoYgbKUHvAWOsG8a9lOo",
    "authDomain": "ecoweb-fc73c.firebaseapp.com",
    "databaseURL": "https://ecoweb-fc73c-default-rtdb.europe-west1.firebasedatabase.app",
    "projectId": "ecoweb-fc73c",
    "storageBucket": "ecoweb-fc73c.appspot.com",
    "messagingSenderId": "725619478235",
    "appId": "1:725619478235:web:7c49e52eead0b7e96546fe",
    "measurementId": "G-YXW94VQWHH"
}
firebase = pyrebase.initialize_app(config=config)
authe = firebase.auth()
database = firebase.database()

def home(request):
    ejemplo = database.child("Data").child("ejemplo1").get().val()
    return render(request, 'index.html', {"ejemplo":ejemplo})
