# Þessi kóði er á Raspberri Pi
import numpy, time
import pyrebase
import cv2
import paho.mqtt.client as mqtt
from gpiozero.pins.pigpio import PiGPIOFactory
from gpiozero import AngularServo, Device
from time import sleep

# Notad er thetta pin factory til ad hafa ekkert "jitter" hja servo-inn
Device.pin_factory = PiGPIOFactory()

# Delay i sek
maxDelay = 3
lastIntruder = time.time()

brokerAddress = "10.201.48.97"

doorOffset = 0

def door_open():
    motor.angle = 110 + doorOffset

def door_close():
    motor.angle = -30 + doorOffset

motor = AngularServo(17, min_angle=-42, max_angle=110)

#Lokar hurdina adur en forritid byrjar
door_close()

def on_message(user, userdata, msg):
    global lastIntruder
    global cam
    msg = msg.payload.decode()
    print(msg)
    if msg == "hurd":
        door_open()
        sleep(10)
        door_close()
    # Leyfir ekki spam
    elif msg == "mynd" and time.time() - lastIntruder > maxDelay:
        lastIntruder = time.time()
        ret, image = cam.read()

        timestamp = time.time()
        # Timasetninga gogn sem er sent yfir til Firebase
        db.child("Intruders").push(str(timestamp))
        cv2.imwrite('/home/pi/Desktop/testimage.jpg', image)
        
        cam.release()
        cam = cv2.VideoCapture(0)

        # Lesa inn myndina og senda yfir a Firebase
        with open('/home/pi/Desktop/testimage.jpg', "rb") as f:
            print(f)
            storage.child(f"VESM3_Loka/{str(timestamp)}.jpg").put(f)
    else:
        print(f"Ogilt gildi: {msg}")

# Stilla upp Firebase til ad senda myndir yfir
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
storage = fb.storage()

cam = cv2.VideoCapture(0)
client = mqtt.Client()

client.on_message = on_message
client.connect(brokerAddress)
client.loop_start()
client.subscribe("hurd-myndavel")

try:
    while True:
        pass
except Exception:
    testClient.loop_stop()
    #cam.release()
    #cv2.destroyAllWindows()
