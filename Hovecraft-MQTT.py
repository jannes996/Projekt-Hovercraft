# Import der Libraries
import time
from machine import Pin, PWM
import network
from umqtt.simple import MQTTClient
import ujson

# Variablen und PINs definieren
motor1_pin = PWM(Pin(3), freq=50)
motor2_pin = PWM(Pin(4), freq=50)
servo_pin = PWM(Pin(5), freq=50)
content = "0"

# Motor Ruhestellung
motor1_pin.duty(40)
motor2_pin.duty(40)

# Sende-/ Empfangfunktion
def send_data(topic, content):
    client.publish(topic, str(content))
    
def recv_data(topic, msg):
    global content
    content = msg.decode()

# WLAN verbinden
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect("BZTG-IoT", "WerderBremen24")

print("Verbinde mit dem WLAN...")
while not wlan.isconnected():
    time.sleep(1)
print("WLAN verbunden! IP-Adresse:", wlan.ifconfig()[0])

# MQTT-Client einrichten und verbinden
client = MQTTClient("Hovercraft", "185.216.176.124", 1883)
client.set_callback(recv_data)

client.connect()
client.subscribe("Hovercraft/Steuerung")
print("MQTT verbunden!")

while True:
    client.check_msg()
    
    if "X" in content:
        data = ujson.loads(content)
        x_value = int(data["X"])
        servo_pin.duty(x_value)
        print(x_value)
        content = "0"
        
    if "Y" in content:
        data = ujson.loads(content)
        y_value = int(data["Y"])
        print(y_value)
        motor1_pin.duty(y_value)
        content = "0"
        
    if "Motor1" in content:
        data = ujson.loads(content)
        if data["Motor1"] == "ON":
            motor1_pin.duty(115)
        elif data["Motor1"] == "OFF":
            motor1_pin.duty(40)
        content = "0"