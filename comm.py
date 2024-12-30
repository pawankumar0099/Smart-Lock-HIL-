import serial
import time
import zlib
from kafka import KafkaConsumer, KafkaProducer
import json
import threading
import board
import busio
import adafruit_tcs34725
import RPi.GPIO as GPIO


# Serial setup
serial_port = '/dev/ttyUSB0'
baud_rate = 9600
seq_num = 0
cmd_num = 2

mcu = serial.Serial(serial_port, baud_rate, timeout=2)
mcu.timeout = 2

pin1 = 17
pin2 = 27
pin3 = 22

GPIO.setup(pin1, GPIO.OUT)
GPIO.setup(pin2, GPIO.OUT)
GPIO.setup(pin3, GPIO.OUT)

GPIO.output(pin1, 1)  # Set pin1 (MSB)
GPIO.output(pin2, 0)  # Set pin2
GPIO.output(pin3, 0) 

# RGB values
r = 0
g = 0
b = 0
c = 0

# Create a lock for synchronizing access to RGB values
rgb_lock = threading.Lock()

# Kafka Consumer setup
consumer = KafkaConsumer(
    'colo',  # Replace with your Kafka topic
    bootstrap_servers='192.168.0.23:9092',
    auto_offset_reset='latest',  # Start from the earliest message
    enable_auto_commit=True,
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

# Kafka Producer setup
producer = KafkaProducer(
    bootstrap_servers='192.168.0.23:9092',
    value_serializer=lambda x: json.dumps(x).encode('utf-8')
)

# Create I2C bus
i2c = busio.I2C(board.SCL, board.SDA)

# Create a sensor object
sensor = adafruit_tcs34725.TCS34725(i2c)

# Set sensor integration time (optional, default is 2.4ms)
sensor.integration_time = 50  # You can set it between 2.4ms and 614ms

# Set gain (optional, default is 1x)
sensor.gain = 16  # Options: 1x, 4x, 16x, 60x

# Enable LED (optional)
sensor.led = True

# Function to get color data
def read_color():
    global r, g, b, c
    while True:
        # Read the color values
        r_raw, g_raw, b_raw, c_raw = sensor.color_raw
        with rgb_lock:  # Acquire the lock before updating RGB values
            r, g, b, c = r_raw, g_raw, b_raw, c_raw
        # print(f"Red: {r}, Green: {g}, Blue: {b}")
        time.sleep(1)

def calculate_crc32(data):
    crc32_value = zlib.crc32(data.encode('utf-8'))
    return crc32_value

def send_data_frame(seq, cmd, data):
    start_byte = (1).to_bytes(1, byteorder='big')
    length_bytes = len(data).to_bytes(2, byteorder='big')
    end_byte = (0).to_bytes(1, byteorder='big')
    crc32_value = calculate_crc32(data).to_bytes(4, byteorder='big')

    # Create the data frame
    data_frame = start_byte + seq.to_bytes(1, byteorder='big') + cmd.to_bytes(
        1, byteorder='big') + length_bytes + data.encode('utf-8') + crc32_value + end_byte

    mcu.write(data_frame)
    print(f"Sent data: {data}")

def receive_data_frame():
    start_byte = mcu.read(1)
    if start_byte == b'\x01':  # Check for start byte
        length_bytes = mcu.read(2)
        length = int.from_bytes(length_bytes, byteorder='big')
        data_received = mcu.read(length)
        crc32_bytes = mcu.read(4)
        end_byte = mcu.read(1)
        
        # Validate CRC32 and end byte
        calculated_crc32 = zlib.crc32(data_received) & 0xFFFFFFFF
        received_crc32 = int.from_bytes(crc32_bytes, byteorder='big')

        if received_crc32 == calculated_crc32 and end_byte == b'\x00':
            print(f"Received data: {data_received.decode('utf-8')}")
            return "successful"
    
    return None

def consume_data_from_kafka():
    global seq_num
    for message in consumer:
        # Assuming the Kafka message contains the data as a JSON key-value pair
        print(f"Received data from Kafka: {message.value}")
        # print(f"dsdsd {message.value['fff']}")
        if 'msr' in message.value:
            data_to_send = message.value['msr']  # Assuming the key in the message is 'data'

        # Send the data received from Kafka to the MCU
            send_data_frame(seq_num, cmd_num, data_to_send)
            mcu.flushInput()  # Clear the buffer
            response_frame = receive_data_frame()  # Optionally handle response if needed
            seq_num += 1  # Increment sequence number after each send
        elif 'rfid' in message.value:
            # print(f"Received data from Kafka: {message.value['rfid']}")
            bin_value = format(message.value['rfid'], '03b') 
            print (bin_value)
            GPIO.output(pin1, int(bin_value[0]))  # Set pin1 (MSB)
            GPIO.output(pin2, int(bin_value[1]))  # Set pin2
            GPIO.output(pin3, int(bin_value[2])) 
            time.sleep(1)
            GPIO.output(pin3, 1) 
            # publish_data()
            
def publish_data():
    global r, g, b, c
    while True:
        topic_to_publish = 'ha'  # Replace with your desired Kafka topic
        with rgb_lock:  # Acquire the lock before reading RGB values
            # Debugging output to check current RGB values
            
            if r > 20200 and g < 2000 and b < 3500:
                data_to_publish = {"led": "red"}  # Replace with actual data to publish
                producer.send(topic_to_publish, value=data_to_publish)  # Send data to Kafka
                time.sleep(1)  # Sleep for some time before publishing again # Sleep for some time before publishing again
            elif r<19000 and g>19000 and b >18000:
                data_to_publish = {"led": "green"}  # Replace with actual data to publish
                producer.send(topic_to_publish, value=data_to_publish)  # Send data to Kafka
                time.sleep(6)  # Sleep for some time before publishing again # Sleep for some time before publishing again               
        # time.sleep(0.5)
# Start the Kafka consumer in a separate thread
consumer_thread = threading.Thread(target=consume_data_from_kafka)
consumer_thread.start()

# Start the data publishing thread
publish_thread = threading.Thread(target=publish_data)
publish_thread.start()

# Start the color sensor reading thread
color_sensor = threading.Thread(target=read_color)
color_sensor.start()

# Optionally join threads if you want to wait for them to finish
color_sensor.join()
consumer_thread.join()
publish_thread.join()

mcu.close()
