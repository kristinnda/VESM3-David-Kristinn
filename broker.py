# Þessi kóði er á tölvunni
import paho.mqtt.client as mqtt
import requests
from app import run
import threading

client = mqtt.Client("Tolva-Kristinsssss")

supasecret = "31415926" # Lykilorð

def on_message(user, userdata, message): # Fall sem keyrir þegar skilaboð í gegnum mqtt fara í gegn
    key = message.payload.decode("utf-8") # Afkóðar skilaboðið

    if key == supasecret: # Ef skilaboðið er það sama og lykilorðið
        print("Access Granted")
        client.publish("hurd-myndavel", "hurd") # þá er sent á raspberry pi að það eigi að opna hurð
        client.publish("Keypad-msg", "rett lykilord") # og sent á esp32 að það var rétt lykilorð
    else:
        client.publish("hurd-myndavel", "mynd") # Annars er sent á raspberrypi að það eigi að taka mynd
        client.publish("Keypad-msg", "rangt lykilord") # og sent á esp32 að það var rangt lykilorð
        print("Nuh uh bannad")
        requests.post("https://maker.ifttt.com/trigger/intruder/with/key/dOVN204OFv6WSI8RslBGhP") # Sent á síma með IFTTT að það hafi verið skrifað rangt lykilorð
    print(key)

# Setja upp mqtt
client.on_message = on_message
client.connect("10.201.48.97") # Tengir við þetta ip address
client.loop_start()
client.subscribe("Keypad-NfC") # Tekur á móti skilaboðum í með Keypad-NfC sem topic

website = threading.Thread(target = run) # Býr til thread sem keyrir vefsíðu á skjalinu "app.py"
website.start() # Keyrir vefsíðuna

while True:
    pass
# :<
