# Þessi kóði er á ESP32
from machine import Pin, PWM
from time import sleep
import machine
import time    
import ubinascii
from umqtt.simple import MQTTClient
import network
from lcd_i2c import LCD
from machine import I2C, Pin

# Fall sem keyrir þegar það koma skilaboð frá mqtt, það koma tvö skilaboð til greina, "rangt lykilord" eða "rett lykilord"
# Skrifar á lcd textann sem í gegnum mqtt
# Athugar hvort lykilorðið var rétt eða rangt og kveikjir á buzzer eftir því hvort það var
def on_message(topic, message): 
    lcd.print(message.decode("utf-8")) 
    if message.decode("utf-8") == "rangt lykilord": 
        beeper = PWM(Pin(14), freq=900, duty=512)
        sleep(5)
    else:
        beeper = PWM(Pin(14), freq=200, duty=512)
        sleep(1)
        beeper = PWM(Pin(14), freq=50, duty=512)
        sleep(1)
    lcd.clear()
    beeper.deinit()
        
# tengist við internetið
print("trying...")
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect('TskoliVESM', 'Fallegurhestur')
print("trying...")
while wlan.isconnected() == False:
    pass
print(wlan.ifconfig())
print("Running")

# Tengist við mqtt broker
MQTT_BROKER = "10.201.48.97"
CLIENT_ID = ubinascii.hexlify("ESP-Kristinsssss")

mqttClient = MQTTClient(CLIENT_ID, MQTT_BROKER, keepalive=60)
print("Connecting")
mqttClient.connect()
mqttClient.set_callback(on_message)
mqttClient.subscribe("Keypad-msg") # Tekur á móti skilaboðum með Keypad-msg sem topic

# Kóði fyrir keypad sem ég fékk á netinu
# CONSTANTS
KEY_UP   = const(0)
KEY_DOWN = const(1)

I2C_ADDR = 0x3f     # DEC 39, HEX 0x27
NUM_ROWS = 2
NUM_COLS = 16
i2c = I2C(0, scl=Pin(2), sda=Pin(1), freq=800000)
lcd = LCD(addr=I2C_ADDR, cols=NUM_COLS, rows=NUM_ROWS, i2c=i2c)

keys = [['1', '2', '3', 'A'], ['4', '5', '6', 'B'], ['7', '8', '9', 'C'], ['*', '0', '#', 'D']]

# Pin names for Pico
rows = [10,9,46,37]
cols = [8,18,17,16]

# set pins for rows as outputs
row_pins = [Pin(pin_name, mode=Pin.OUT) for pin_name in rows]

# set pins for cols as inputs
col_pins = [Pin(pin_name, mode=Pin.IN, pull=Pin.PULL_DOWN) for pin_name in cols]

def init():
    for row in range(0,4):
        for col in range(0,4):
            row_pins[row].value(0)
            
hljod = {"1": 150, "2": 200, "3": 250, "4": 300, "5": 350, "6": 400, "7": 450, "8": 500, "9": 550, "0": 600, "A": 700, "C": 800, "D": 900}
beeper = PWM(Pin(14), freq=500, duty=512)
beeper.deinit()

# Setup done

def scan(row, col):
    """ scan the keypad """

    # set the current column to high
    row_pins[row].value(1)
    key = None

    # check for keypressed events
    if col_pins[col].value() == KEY_DOWN:
        key = KEY_DOWN
    if col_pins[col].value() == KEY_UP:
        key = KEY_UP
    row_pins[row].value(0)

    # return the key state
    return key

print("starting")

# set all the columns to low
init()

flag = False
last_key_press = "blank"
colc = 0
rowc = 0

pwd = ""
lcd.begin()
# Athugar hvaða takka það er verið að ýta á og skrifað á lcd
while True:
    mqttClient.check_msg()
    for row in range(4):
        for col in range(4):
            key = scan(row, col)
            if key == KEY_DOWN and not flag:
                if keys[row][col] in hljod:
                    beeper = PWM(Pin(14), freq=hljod[keys[row][col]], duty=512)
                flag = True
                last_key_press = keys[row][col]
                colc = col
                rowc = row
                if last_key_press == "C":
                    pwd = pwd[:-1]
                elif last_key_press == "D":
                    pwd = ""
                elif last_key_press == "*" or last_key_press == "#":
                    pass
                elif last_key_press == "A":
                    mqttClient.publish("Keypad-NfC", pwd)
                    lcd.print("")
                    pwd = ""
                else:
                    if len(pwd) < 16:
                        pwd+=last_key_press
                
                lcd.clear()
                lcd.print(pwd)

    if scan(rowc, colc) == KEY_UP:
        beeper.deinit()
        flag = False
        
         
