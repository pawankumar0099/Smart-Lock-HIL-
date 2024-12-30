import serial
import time
import zlib
import serial.tools.list_ports

serial_port = '/dev/ttyUSB0'  #
baud_rate = 9600
count = 0
seq_num = 0
cmd_num = 2
data_to_send = "%pawan?;123456789?"

mcu = serial.Serial(serial_port, baud_rate, timeout=2)
mcu.timeout = 2


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
    # line = mcu.readline().rstrip()
    # print(line)
    # lines = mcu.readlines()
    # for line in lines:
    # print(line.decode('utf-8').rstrip())
    # time.sleep(1)


def receive_data_frame():

    start_byte = mcu.read(1)
    print(start_byte)
    if start_byte == b'\x01':
        response_frame = mcu.read(17)
        #rec_msg = mcu.read(10)
        #crc32_bytes = mcu.read(4)
        #end_byte = mcu.read(1)
        print(response_frame)
        # Validate CRC32 and end byte
        #calculated_crc32 = zlib.crc32(response_frame) & 0xFFFFFFFF
        #received_crc32 = int.from_bytes(crc32_bytes, 'big')

        # if received_crc32 == calculated_crc32 and end_byte == b'\x00':  # Assuming END_BYTE is 0x00
        return "successfull"  # Return the valid response frame

    return None


def ping_mcu():
    cmd_num = (3).to_bytes(1, byteorder='big')
    mcu.write(cmd_num)

def receive_ping():
    global conn_stat
    conn_stat = 0
    line = mcu.readline().rstrip()
    if (line == b'Connection Successful'):    
        conn_stat = 1


def user_inp():
    global seq_num
    cmd = input("Enter Cmd: ")
    if cmd == '1':
        print("Pinging MCU")
        for i in range(10):
            ping_mcu()
            receive_ping()
            if(conn_stat == 1):
                print("Res: Connected Successfully")
                break
        if(conn_stat == 0):
            print("Res: Connection Failed")
    if cmd == '2':
        send_data_frame(seq_num, cmd_num, data_to_send)
        mcu.flushInput()
        response_frame = receive_data_frame()
        #if response_frame:
            #print(f"Received response frame: {response_frame}")
        seq_num+=1

while True:
    user_inp()
    #send_data_frame(seq_num,cmd_num,data_to_send)
    #mcu.flushInput()
    #time.sleep(5)

mcu.close()
