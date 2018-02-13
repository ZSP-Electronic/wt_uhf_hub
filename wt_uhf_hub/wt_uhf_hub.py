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


JSON_LOC = './Hello World-bdfbdf4aa8d5.json'
client = datastore.Client.from_service_account_json(JSON_LOC)

hackrf = hackrfCtrl()
# SD card object declaration
    
GPIO.setup("P8_14", GPIO.IN)

Debug = False

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
        
''' This is the main function that runs on startup. First determines if sd card
    is inserted so device can work. Then runs a request from the Datastore 
    database if connected to internet. It then runs the HackRF and stores its 
    data in a file and stores it appropriately. '''
def main():
    print("Start Main")
    
    #InternetErrorFlag = InternetCheck()
    
    if Debug:
        import Adafruit_BBIO.UART as UART
        print("Importing UART")
        UART.setup("UART1")
        ser = serial.Serial(port = "/dev/ttyO1", baudrate=9600)
        ser.close()
        #ser.open()
        
    timer1 = time.time()
    timer2 = time.time()
    
    while True:
        ''' Initialize global variables to be used '''
        request = False
        minFreq = 0
        maxfreq = 0
        samprate= 0
        #TODO Fix GPIO for real sd card CD pin
        if GPIO.input("P8_14") == False:
            
            ''' First "if" statement checks if timer1 is greater than specified
                time and if connected to internet request from Datastore. '''
            if time.time() - timer1 > 15:
                InternetFlag = InternetCheck()
                if InternetFlag:
                    print('Requesting Data')
                    
                    #Request data from database
                    key_complete = client.key('mylist', 'UHF_Hub_test')
                    tasks = client.get(key_complete)
                    
                    #Put properties of request into varaibles
                    request = tasks['Request']
                    minFreq = tasks['min_frequency']
                    maxfreq = tasks['max_frequency']
                    samprate= tasks['sample_rate']
                    
                    data = [request, minFreq, maxfreq, samprate]
                    print(data)
                    
                    #If there was a request collect hackrf data immediately
                    if request == True:
                        runHackrf(InternetFlag, minFreq, maxfreq, samprate)
                        #Set Request == False when return from hackrf
                        tasks['Request'] = False
                        tasks['min_frequency'] = minFreq + samprate
                        client.put(tasks)
                        timer2 = time.time()
                        
                    timer1 = time.time()
                else:
                    #This is for if not connected to internet. Nothing much
                    #to do besides nothing
                    print("No Internet == Do Nothing")
                    timer1 = time.time()
                    
            ''' Second "if" statement is used to run the hackrf. The global 
                variables allow the database to set them and be placed into
                this function. '''
            if time.time() - timer2 > 20:
                runHackrf(InternetFlag, minFreq, maxfreq, samprate)
                
                timer1 = time.time()
                timer2 = time.time()
                    
        else:
            print('Show error')
            time.sleep(1)

'''The Hackrf run function determines if the internet is connected. If it is
    then use the parameters passed from the database otherwise read the 
    parameters from the sd card. Run the hackrf the appropriate amount of times
    then save it to a file and save the file appropriately. '''
def runHackrf(internetFlag, Start_frequency=0, Finish_frequency=0, sample_rate=0):
    
    #Collect the data
    if internetFlag:
        print("Use database perameters")
        center_frequency = int(Start_frequency + (sample_rate/2))
        
        data_pts = hackrf.setParameters(center_frequency, sample_rate)
        iq = hackrf.hackrf_run(5)
        
    else:
        print("Read config file on sd card")
        Start_frequency = 105e6
        Finish_frequency = 108e6
        sample_rate = 2.048e6
        center_frequency = int(Start_frequency + (sample_rate/2))
                
        data_pts = hackrf.setParameters(center_frequency, sample_rate)
        iq = hackrf.hackrf_run(1)
    
    #Store data into file            
    strname = str(center_frequency/1e6) + 'e6_' + \
    str(time.strftime('%m_%d_%H_%M', time.localtime()))
    
    print(strname)
    np.savez(strname, data_pts = data_pts, iq = iq)
    
    #Save file to storage or SD card            
    if internetFlag:
        storage_client = storage.Client.from_service_account_json(JSON_LOC)
        
        bucket_name = 'my_test_bucket32'
        bucket = storage_client.get_bucket(bucket_name)
                    
        blob = bucket.blob(os.path.basename(strname + '.npz'))
        blob.upload_from_filename(strname + '.npz')
        confirmation = "File {} stored via Cloud".format(strname)
        print(confirmation)
        os.remove(strname + '.npz')
        
        #Request data from database
        key_complete = client.key('mylist', 'UHF_Hub_test')
        tasks = client.get(key_complete)
                
        #Put properties of request into varaibles
        request = tasks['Request']
        minFreq = tasks['min_frequency']
        maxfreq = tasks['max_frequency']
        samprate= tasks['sample_rate']
                
        tasks['min_frequency'] = minFreq + samprate
        client.put(tasks)
        print('Data Updated')
    else:
        print("Store to sd card")
        confirmation = "File {} stored via SD card".format(strname)
        print(confirmation)
        os.remove(strname + '.npz')
    
    #For debugging out to UART            
    if Debug:
        ser.open()
        if ser.isOpen():
            ser.write(confirmation)
            print("Serial is open!")
                        
        ser.close()
    
    return


if __name__ == '__main__':
    main()