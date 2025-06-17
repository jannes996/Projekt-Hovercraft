import time
from machine import Pin, PWM
import network
from umqtt.simple import MQTTClient
import ujson

# PWM Pins initialisieren
motor_heck_pin = PWM(Pin(3), freq=50)
motor_auftrieb_pin = PWM(Pin(4), freq=50)
servo_pin = PWM(Pin(5), freq=50)

# In Ruhestellung setzen
motor_heck_pin.duty(40)
motor_auftrieb_pin.duty(40)
servo_pin.duty(40)

# Steuerstatus
motor1_active = False
content = "0"

# MQTT-Funktionen
def send_data(topic, content):
    client.publish(topic, str(content))
    
def recv_data(topic, msg):
    global content
    content = msg.decode()
    print(content)

# WLAN verbinden
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect("BZTG-IoT", "WerderBremen24")

print("Verbinde mit dem WLAN...")
while not wlan.isconnected():
    time.sleep(1)
print("WLAN verbunden! IP-Adresse:", wlan.ifconfig()[0])

# MQTT einrichten
client = MQTTClient("Hovercraft", "185.216.176.124", 1883)
client.set_callback(recv_data)
client.connect()
client.subscribe("Hovercraft/Steuerung")
print("MQTT verbunden!")

# Hauptloop
while True:
    client.check_msg()
    
    # Motoren EIN/AUS
    if "Motoren" in content:
        data = ujson.loads(content)
        if data["Motoren"] == "ON":
            motor1_active = True
        elif data["Motoren"] == "OFF":
            motor_auftrieb_pin.duty(40)
            motor_heck_pin.duty(40)
            servo_pin.duty(40)
            motor1_active = False

    if motor1_active:
        # Servo X
        if "X" in content:
            data = ujson.loads(content)
            x_value = int(data["X"])
            servo_pin.duty(x_value)
            content = "0"

        # Heckmotor Y
        if "Y" in content:
            data = ujson.loads(content)
            y_value = int(data["Y"])
            motor_heck_pin.duty(y_value)
            content = "0"

        # Auftrieb
        if "auftrieb" in content:
            data = ujson.loads(content)
            pwm_value = int(data["auftrieb"])
            motor_auftrieb_pin.duty(pwm_value)
            content = "0"

    time.sleep(0.01)