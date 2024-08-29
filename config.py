from dotenv import load_dotenv
import os

load_dotenv('properties.env')

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    
    FIREBASE_CONFIG = {
        "apiKey": os.getenv('FIREBASE_API_KEY'),
        "authDomain": os.getenv('FIREBASE_AUTH_DOMAIN'),
        "storageBucket": os.getenv('FIREBASE_STORAGE_BUCKET'),
        "projectId": os.getenv('FIREBASE_PROJECT_ID'),
        "messagingSenderId": os.getenv('FIREBASE_MESSAGING_SENDER_ID'),
        "appId": os.getenv('FIREBASE_APP_ID'),
        "databaseURL": os.getenv('FIREBASE_DATABASE_URL')
    }
