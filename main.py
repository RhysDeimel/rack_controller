import json
import nic
import ahtx0
import fan
import time

from server import HTTPServer
from usocket import socket
from machine import Pin, I2C

app = HTTPServer()


@app.route("GET", "/")
def get(conn, request):
    print("in GET")
    data = {
        "exhaust_temperature": f"{exhaust_sensor.temperature:.2f}",
        "exhaust_humidity": f"{exhaust_sensor.relative_humidity:.2f}",
        "intake_temperature": f"{intake_sensor.temperature:.2f}",
        "intake_humidity": f"{intake_sensor.relative_humidity:.2f}",
        "intake_fan_speed": fan.PWMFan().speed,  # the duty cycle (between 0 and 100)
    }

    response = json.dumps(data).encode("utf-8")

        
    conn.write('HTTP/1.1 200 OK\r\n')
    conn.write('Connection: close\r\n')
    conn.write("Content-Type: application/json\r\n")
    conn.write('Content-Length: %s\n\n' % len(response))
    conn.write(response)


@app.route("PUT", "/")
def update(conn, request):
    # There's a but with the WIZNET drivers where a PUT connection
    #   isn't closed properly.
    print("in PUT")
    data = request.body.decode("utf-8")
    data = json.loads(data)
    print("decoded data")
    print(data)

    print("setting fan speed")
    fan.PWMFan().speed = data["fan_speed"]

    print("writing response")
    conn.write('HTTP/1.1 204 No Content\r\n')
    conn.write('Connection: close\r\n')


if __name__ == "__main__":
    time.sleep(10)
    
    print("Setting I2C pins")
    i2c_0 = I2C(0, scl=Pin(9), sda=Pin(8))
    i2c_1 = I2C(1, scl=Pin(7), sda=Pin(6))
    
    print("Initialising sensors")
    intake_sensor = ahtx0.AHT10(i2c_0)
    exhaust_sensor = ahtx0.AHT10(i2c_1)
    
    print("Initialising NIC")
    nic.init()
    
    print("Setting intake fan to 50%")
    fan.PWMFan().speed = 50

    print("Starting webserver")
    app.start()
