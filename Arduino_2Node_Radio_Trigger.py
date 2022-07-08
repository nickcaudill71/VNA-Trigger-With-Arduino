import serial
import time
import pyvisa as visa


def limit_test():
    # Performs limit test on the current trace, VNA is triggered from Arduino
    # Waits for sweep to finish then preforms a limit test and returns the result
    CMT.write("TRIG:WAIT MEAS")
    CMT.query('*OPC?')
    CMT.write("TRIG:WAIT ENDM")
    CMT.query('*OPC?')
    limit_test_result = CMT.query("CALC:LIM:FAIL?")
    return limit_test_result


rm = visa.ResourceManager()
try:
    CMT = rm.open_resource(
        'TCPIP0::localhost::5025::SOCKET')  # Connecting to the VNA software using a socket connection at 5025
except:
    print("Failure to connect to VNA!")
    print("Check network settings")
CMT.read_termination = '\n'
CMT.timeout = 1000000000

ser = serial.Serial('COM11', 9600, timeout=1)  # Connecting to the serial port which the Arduino is connected to

CMT.write("INIT:CONT 0")  # These commands initialize the VNA software
time.sleep(2)  # wait for the serial connection to initialize
CMT.write("INIT:CONT 1")
CMT.write("CALC:LIM ON")
CMT.write("CALC:LIM:DISP ON")

while 1:
    # Loops until serial port receives something. VNA gets triggered and a limit test is ran
    # If the limit test fails replies through the serial port with a 0, and if it passes reply with a 1
    if ser.in_waiting != 0:
        buf = ser.readline()
        buf_string = buf.decode()
        buf_string = buf_string.strip()
        if buf_string == '1':
            print("Received trigger... Waiting to run limit test\n")
            value = limit_test()
            print("Limit test finished.\n")
            if value == '1':
                print("Limit failed.. Letting Arduino know!\n")
                ser.write(b'1')
            elif value == '0':
                print("Limit passed.. Letting Arduino know!\n")
                ser.write(b'0')
