# Þessi kóði er á Tölvunni
from flask import Flask, flash, render_template, redirect, url_for, session, request, abort
from flask_ckeditor import CKEditor
import pyrebase
from datetime import datetime
from waitress import serve
import paho.mqtt.client as mqtt

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

app = Flask(__name__)
ckeditor = CKEditor(app)

app.config['SECRET_KEY'] = 'leyni'
app.config['UPLOAD_FOLDER'] = "tempstorage"
config = {
    "apiKey": "AIzaSyCVXBVchfY5JcMCkOPP7uAqfD9xNhcLrXs",
    "authDomain": "verkefni4-1dbbd.firebaseapp.com",
    "databaseURL": "https://verkefni4-1dbbd-default-rtdb.firebaseio.com",
    "projectId": "verkefni4-1dbbd",
    "storageBucket": "verkefni4-1dbbd.appspot.com",
    "messagingSenderId": "115205351569",
    "appId": "1:115205351569:web:041481be2303fbba9c3730"
}

fb = pyrebase.initialize_app(config)
db = fb.database()
auth = fb.auth()
storage = fb.storage()

client = mqtt.Client("WebsiteHolder")
client.connect("10.201.48.97")

# tekur úr firebase myndirnar og tímasetningarnar
def getIntruders():
    intruders = db.child("Intruders").get().val()
    betterIntruders = []
    for v in intruders.values():
        betterIntruders.append([fromUnixToDate(v), storage.child(f"VESM3_Loka/{v}.jpg").get_url(None)])

    betterIntruders = [x for x in betterIntruders[::-1]]
    return betterIntruders


def fromUnixToDate(unoTime):
    unoTime = int(round(float(unoTime)))
    return datetime.utcfromtimestamp(unoTime).strftime('%Y-%m-%d %H:%M:%S')

def toIcelandicTime(time):
    day = time.day
    month = time.month
    year = time.year
    hour = time.hour
    minute = time.minute
    second = time.second
    if hour < 10:
        hour = "0" + str(hour)
    if minute < 10:
        minute = "0" + str(minute)
    if second < 10:
        second = "0" + str(second)
    return f"{day}.{month}.{year} {hour}:{minute}:{second}"


@app.errorhandler(404)
def page_not_found(errorcode):
    return render_template("pagenotfound.html")

@app.errorhandler(500)
def unexpected_error(errorcode):
    return render_template("unexpectederror.html")

# --// Routes

@app.route("/", methods=["GET", "POST"])
def home():
    if request.form:
        print("AAAAAAAAa")
        flash("Opened door")
        client.publish("hurd-myndavel", "hurd")

    intruders = getIntruders()
    return render_template("home.html", intruders = intruders)

def run():
    serve(app, host="0.0.0.0", port = 5000)
