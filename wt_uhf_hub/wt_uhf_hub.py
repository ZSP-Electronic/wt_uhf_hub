# Texas A&M University
# Electronic Systems Engineering Technology
# ESET-420 Capstone II
# Author: Zachary Pina
# File: main.py
# --------
# Main is the heart of the program that runs the code. The code will determine
# if it connected to the internet then request data from the google Datastore
# database then run the hackrf and collect its data. Depending on the internet
# connection the file be stored either on the sd card or google Storage

from pylibhackrf import hackrfCtrl
import Adafruit_BBIO.GPIO as GPIO
from google.cloud import storage
from google.cloud import datastore
import socket
import time
import serial
import os
#import timeit 
import numpy as np
# import SD card 

#Initialize global variables to be used 
minFreq = 0
maxFreq = 0
samprate= 0
incremFreq = 0
timer1 = 0
timer2 = 0
TIMER1_TIME = 15
TIMER2_TIME = 20
BASE_PATH = '/tmp/'


# PUT CREDENTIALS BELOW!
# Put JSON file name here include ./ at beginning if in same directory as this program:
JSON_LOC = './Hello World-bdfbdf4aa8d5.json'
#Put chip detect pin name here:
CD_PIN = "<PIN NAME>"
# Put bucket name here for Google Storage:
BUCKET_NAME = 'second_test_bucket123'
# Put names for Google Datastore here:
KIND = 'mylist'
ID_NAME = 'UHF_Hub_test'
ADV_NAME = 'advanceSetting'
# Put UART port names here
UART_PORT = '/dev/ttyO4'

DEBUG = False
ENABLE_SD = False
request = False
#InternetFlag = False



client = datastore.Client.from_service_account_json(JSON_LOC)
hackrf = hackrfCtrl()
# SD card object declaration
if ENABLE_SD:
    GPIO.setup(CD_PIN, GPIO.IN)

''' This is the main function that runs on startup. First determines if sd card
    is inserted so device can work. Then runs a request from the Datastore 
    database if connected to internet. It then runs the HackRF and stores its 
    data in a file and stores it appropriately. '''
def main():
    global timer1, timer2
    
    print("Start Main")
    
    if DEBUG:
        import Adafruit_BBIO.UART as UART
        print("Importing UART")
        UART.setup(UART_NAME)
        ser = serial.Serial(port = UART_PORT, baudrate=9600)
        ser.close()
        
    timer1 = time.time()
    timer2 = time.time()
    
    while True:
        #TODO Fix GPIO for real sd card CD pin
        if ENABLE_SD:
            if GPIO.input(CD_PIN) == False:
                dataStoreCheck()
            else:
                print('Show error')
                time.sleep(1)
        else:
            dataStoreCheck()
            
            
''' This function checks the interntflag and determines if should request data
    from dataStore or to use the sd card to store file '''
def dataStoreCheck():
    global timer1, timer2
    global request
    global minFreq, maxFreq, incremFreq
    global samprate
    global InternetFlag
    ''' First "if" statement checks if timer1 is greater than specified
    time and if connected to internet request from Datastore. '''
    if time.time() - timer1 > TIMER1_TIME:
        InternetFlag = InternetCheck()
        if InternetFlag:
            print('Requesting Data')
                        
            #Request data from database
            key_complete = client.key(KIND, ID_NAME)
            tasks = client.get(key_complete)
                        
            #Put properties of request into varaibles
            request = tasks['Request']
            minFreq = tasks['min_frequency']
            maxFreq = tasks['max_frequency']
            samprate= tasks['sample_rate']
            incremFreq = tasks['increment_frequency']
                        
            data = [request, minFreq, incremFreq, maxFreq, samprate]
            print(data)
                        
            #If there was a request collect hackrf data immediately
            if request == True:
                runHackrf(InternetFlag, incremFreq, maxFreq, samprate)
                timer2 = time.time()
                            
            timer1 = time.time()
        else:
            '''This is for if not connected to internet. Nothing much
               to do besides nothing '''
            print("No Internet == Do Nothing")
            timer1 = time.time()
                        
    ''' Second "if" statement is used to run the hackrf. The global 
        variables allow the database to set them and be placed into
        this function. '''
    if time.time() - timer2 > TIMER2_TIME:
        print(InternetFlag)
        runHackrf(InternetFlag, incremFreq, maxFreq, samprate)
                    
        timer1 = time.time()
        timer2 = time.time()


'''The Hackrf run function determines if the internet is connected. If it is
    then use the parameters passed from the database otherwise read the 
    parameters from the sd card. Run the hackrf the appropriate amount of times
    then save it to a file and save the file appropriately. '''
def runHackrf(internetflag, Start_frequency=0, Finish_frequency=0, sample_rate=0):
    global ENABLE_SD
    #Error = False
    #Collect the data
    if internetflag:
        print("Use database perameters")
        center_frequency = int(Start_frequency + (sample_rate/2))
        
        data_pts = hackrf.setParameters(center_frequency, sample_rate)
        iq, Error = hackrf.hackrf_run(5)
        
    else:
        print("Read config file on sd card")
        Start_frequency = 105e6
        Finish_frequency = 108e6
        sample_rate = 2.048e6
        center_frequency = int(Start_frequency + (sample_rate/2))
                
        data_pts = hackrf.setParameters(center_frequency, sample_rate)
        iq, Error = hackrf.hackrf_run(1)
    
    if Error != True:
        #Store data into file
        hackrf.close()
        strname = str(time.strftime('%m|%d_%H|%M_', time.localtime()) + \
        str(Start_frequency/1e6) + 'e6|' + \
        str((Start_frequency + sample_rate)/1e6) + 'e6')
        
        print(strname)
        np.savez_compressed(os.path.join(BASE_PATH, strname), data_pts = data_pts, iq = iq)
        
        #Save file to storage or SD card
        if internetflag:
            storage_client = storage.Client.from_service_account_json(JSON_LOC)
            
            bucket = storage_client.get_bucket(BUCKET_NAME)
                        
            blob = bucket.blob(os.path.basename(BASE_PATH + strname + '.npz'))
            blob.upload_from_filename(BASE_PATH + strname + '.npz')
            confirmation = "File {} stored via Cloud".format(strname)
            print(confirmation)
            os.remove(BASE_PATH + strname + '.npz')
            
            #Request data from database
            key_complete = client.key(KIND, ID_NAME)
            tasks = client.get(key_complete)
                    
            #Put properties of request into varaibles
            request = tasks['Request']
            minFreq = tasks['min_frequency']
            maxFreq = tasks['max_frequency']
            samprate= tasks['sample_rate']
            incremFreq = tasks['increment_frequency']
            
            newfreq = incremFreq + samprate
            
            if newfreq >= maxFreq:
                print("Setting increment frequency back to minimum frequency")
                tasks['increment_frequency'] = minFreq
            else:
                tasks['increment_frequency'] = newfreq
                print('Data Updated')
                
            client.put(tasks)
        else:    
            if ENABLE_SD:
                writeToSD(BASE_PATH + strname)
        
        #For debugging out to UART
        if DEBUG:
            writeToUART(confirmation)
    else:
        hackrf.close()
        print("I reported an error")
        
    return
        
        
''' The internetCheck function sees if the device can connected to gmail.com
    and if uncommented, will print out the IP address since there is a socket
    setup between the internet device and gmail '''
def InternetCheck():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("gmail.com",80))
        #print("IP: " + s.getsockname()[0])
        s.close()
        return True
        
    except Exception:
        print("Not connected to internet")
        return False
        
        
''' Function to store file to sd card '''
def writeToSD(file):
    print("Store to sd card")
    confirmation = "File {} stored via SD card".format(file)
    print(confirmation)
    os.remove(BASE_PATH + file + '.npz')


''' Function to write string to UART '''
def writeToUART(message):
    ser.open()
    if ser.isOpen():
        ser.write(message)
        #print("Serial is open!")
    ser.close()


if __name__ == '__main__':
    main()
