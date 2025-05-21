import network
import socket
import time
from machine import Pin, PWM

# Access Point
ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid="Team-Untergang", password="12345678", authmode=network.AUTH_WPA2_PSK)

# GPIO konfigurieren
motor1_pin = PWM(Pin(32), freq=50)
motor2_pin = PWM(Pin(33), freq=50)
servo_pin = PWM(Pin(4), freq=50)

# Motoren Ruhestellung
motor1_pin.duty(40)
motor2_pin.duty(40)

# HTML-Seite
html = """<!DOCTYPE html>
<html>
<head>
    <title>Hovercraft Steuerung</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial; text-align: center; }
        button { padding: 10px; margin: 5px; font-size: 20px; }
    </style>
</head>
<body>
<h1>Hovercraft Steuerung</h1>

    <h1>Motor 1</h1>
    <input type="range" id="motor1_slider" min="40" max="100" step="10" value="40" oninput="updateStatus('motor1_status', this.value)">
    <button onclick="sendSliderValue('MOTOR1', 'motor1_slider')">Setzen</button>
    <br>
    <button onclick="sendButton('MOTOR1_CALIBRATE')">Motor Kalibrieren</button>

    <br>---

    <h1>Motor 2</h1>
    <input type="range" id="motor2_slider" min="40" max="100" step="10" value="40" oninput="updateStatus('motor2_status', this.value)">
    <button onclick="sendSliderValue('MOTOR2', 'motor2_slider')">Setzen</button>
    <br>
    <button onclick="sendButton('MOTOR2_CALIBRATE')">Motor Kalibrieren</button>

    <br>---

    <h1>Lenkung</h1>
    <button onclick="sendButton('SERVO_LEFT', 'status_lenkung')">LINKS</button>
    <button onclick="sendButton('SERVO_MID', 'status_lenkung')">GERADE</button>
    <button onclick="sendButton('SERVO_RIGHT', 'status_lenkung')">RECHTS</button>

    <script>
        function sendButton(action, statusId) {
            fetch('/button?action=' + action);
        }
        function sendSliderValue(prefix, sliderId) {
            let value = document.getElementById(sliderId).value;
            fetch('/button?action=' + prefix + '_SET_' + value);
        }
    </script>
    
</body>
</html>
"""

# Webserver starten
def web_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', 80))
    s.listen(5)
    print("Webserver läuft... IP:", ap.ifconfig()[0])
    conn_pin = PWM(Pin(2))

    while True:
        conn, addr = s.accept()
        request = conn.recv(1024).decode('utf-8')

        if '/button?action=MOTOR1_SET' in request:
            first_line = request.split("\n")[0]
            value = first_line.split("_")[-1].split(" ")[0]
            value = int(value)
            motor1_pin.duty(value)

        elif '/button?action=MOTOR1_CALIBRATE' in request:
            motor1_pin.duty(115)
            time.sleep(2)
            motor1_pin.duty(40)

        elif '/button?action=MOTOR2_SET' in request:
            first_line = request.split("\n")[0]
            value = first_line.split("_")[-1].split(" ")[0]
            value = int(value)
            motor2_pin.duty(value)
            
        elif '/button?action=MOTOR2_CALIBRATE' in request:
            motor2_pin.duty(115)
            time.sleep(2)
            motor2_pin.duty(40)
            
        elif '/button?action=SERVO_LEFT' in request:
            servo_pin.duty(50)
            
        elif '/button?action=SERVO_MID' in request:
            servo_pin.duty(72)
            
        elif '/button?action=SERVO_RIGHT' in request:
            servo_pin.duty(100)

        # HTML-Seite zurücksenden
        conn.send("HTTP/1.1 200 OK\n")
        conn.send("Content-Type: text/html\n\n")
        conn.send(html)
        conn.close()
        
def calibrate_servo():
    servo_pin.duty(100)
    time.sleep(1)
    servo_pin.duty(50)
    time.sleep(1)
    servo_pin.duty(72)
    
calibrate_servo()
web_server()