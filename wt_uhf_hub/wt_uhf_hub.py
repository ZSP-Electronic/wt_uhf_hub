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
#BASE_PATH = '/tmp/'
SDDIR = '/media/card/'
SDSAVEDFILESDIR = '/media/card/savedFiles/'
CREDDIR = '/media/card/Credentials.txt'
UART_PORT = '/dev/ttyO4'

DEBUG = False
ENABLE_SD = True
request = False
#InternetFlag = False

if ENABLE_SD:
    if not os.path.exists(CREDDIR):
        credFile = open(CREDDIR, 'w')
        credFile.write("JSON File Name:\n")
        credFile.write("Card Detect Pin:\n")
        credFile.write("Bucket Name:\n")
        credFile.write("Datastore Kind Name:\n")
        credFile.write("Datastore ID Name:\n")
        credFile.write("Datastore Adv ID Name:\n")
        credFile.close()
        
        print("Output to LCD: Credentials file created.\
        Input credentials and restart")
        while True:
            pass
    else:
        f = open(CREDDIR, 'r')
        information = f.readlines()
        infoArray = np.empty(6, dtype='U256')
        for index, lines in enumerate(information):
            tempinfo = lines.split(":")
            infoArray[index] = tempinfo[1].replace("\n", '')
    
        JSON_LOC = SDDIR + str(infoArray[0])
        CD_PIN = str(infoArray[1])
        BUCKET_NAME = str(infoArray[2])
        KIND = str(infoArray[3])
        ID_NAME = str(infoArray[4])
        ADV_NAME = str(infoArray[5])


client = datastore.Client.from_service_account_json(JSON_LOC)
hackrf = hackrfCtrl(DEBUG)
# SD card object declaration
if ENABLE_SD:
    GPIO.setup(CD_PIN, GPIO.IN)
    
if DEBUG:
    print("Importing UART")
    ser = serial.Serial(port=UART_PORT, baudrate=115200)
    ser.close()

''' This is the main function that runs on startup. First determines if sd card
    is inserted so device can work. Then runs a request from the Datastore 
    database if connected to internet. It then runs the HackRF and stores its 
    data in a file and stores it appropriately. '''
def main():
    global timer1, timer2
    
    print("Start Main")
    if DEBUG:
        writeToUARTln('Start Main')
        
    timer1 = time.time()
    timer2 = time.time()
    
    while True:
        #TODO Fix GPIO for real sd card CD pin
        if ENABLE_SD:
            if not GPIO.input(CD_PIN):
                dataStoreCheck()
            else:
                print('Show error to LCD')
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
            if DEBUG:
                writeToUARTln('Requesting Data from Datastore')
                        
            #Request data from database
            key_complete = client.key(KIND, ID_NAME)
            tasks = client.get(key_complete)
                        
            #Put properties of request into varaibles
            request = tasks['Request']
            minFreq = tasks['min_frequency']
            incremFreq = tasks['increment_frequency']
            maxFreq = tasks['max_frequency']
            samprate= tasks['sample_rate']
                        
            data1 = [request, minFreq, incremFreq, maxFreq, samprate]
            print(data1)
            if DEBUG:
                for element in data1:
                    writeToUART(element)
                writeToUART('\n')
                        
            #If there was a request collect hackrf data immediately
            if request == True:
                runHackrf(InternetFlag, minFreq, incremFreq, maxFreq, samprate)
                timer2 = time.time()
                            
            timer1 = time.time()
        else:
            '''This is for if not connected to internet. Nothing much
               to do besides nothing '''
            print("No Internet == Read SD card")
            if DEBUG:
                writeToUARTln('Requesting Data from SD config file')
            
            params = []
            with open(SDDIR + 'config.txt', 'r') as configFile:
                for line in configFile:
                    numbers_float = map(float, line.split(', '))
                    for number in numbers_float:
                        params.append(number)

            minFreq = params[1]
            incremFreq = params[2]
            maxFreq = params[3]
            samprate= params[4]

            data2 = [minFreq, incremFreq, maxFreq, samprate]
            print(data2)
            if DEBUG:
                for element in data2:
                    writeToUART(element)
                writeToUART('\n')
            
            timer1 = time.time()
                        
    ''' Second "if" statement is used to run the hackrf. The global 
        variables allow the database to set them and be placed into
        this function. '''
    if time.time() - timer2 > TIMER2_TIME:
        runHackrf(InternetFlag, minFreq, incremFreq, maxFreq, samprate)
                    
        timer1 = time.time()
        timer2 = time.time()


'''The Hackrf run function determines if the internet is connected. If it is
    then use the parameters passed from the database otherwise read the 
    parameters from the sd card. Run the hackrf the appropriate amount of times
    then save it to a file and save the file appropriately. '''
def runHackrf(internetflag, Start_frequency, Increment_frequency, Finish_frequency, sample_rate):
    global ENABLE_SD
    #Error = False
    #Collect the data
    center_frequency = int(Increment_frequency + (sample_rate/2))
        
    data_pts = hackrf.setParameters(center_frequency, sample_rate)
    iq, Error = hackrf.hackrf_run(5)
    
    if not Error:
        #Store data into file
        strname = str(time.strftime('%m-%d_%H-%M_', time.localtime()) + \
        str(Increment_frequency/1e6) + 'e6-' + \
        str((Increment_frequency + sample_rate)/1e6) + 'e6')
        
        if DEBUG:
            writeToUARTln(strname)
        else:
            print(strname)
        
        if internetflag:
            ''' Save npz file in tmp dir '''
            np.savez_compressed(strname, data_pts = data_pts, iq = iq)
        else:
            np.savez_compressed(os.path.join(SDSAVEDFILESDIR, strname), data_pts = data_pts, iq = iq)
            
        strname = strname + '.npz'
        
        newInternetFlag = InternetCheck()
        
        #Save file to storage or SD card
        if newInternetFlag:
            hackrf.close()
            storage_client = storage.Client.from_service_account_json(JSON_LOC)
            
            bucket = storage_client.get_bucket(BUCKET_NAME)
                        
            blob = bucket.blob(os.path.basename(strname))
            blob.upload_from_filename(strname)
            confirmation = "File {} stored via Cloud".format(strname)
            print(confirmation)
            if DEBUG:
                writeToUARTln(confirmation)
            os.remove(strname)
            
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
                if DEBUG:
                    writeToUARTln("Setting increment frequency back to minimum frequency")
                tasks['increment_frequency'] = minFreq
            else:
                tasks['increment_frequency'] = newfreq
                print('Data Updated')
                if DEBUG:
                    writeToUARTln("Data Updated")
                
            client.put(tasks)
        else:
            hackrf.close()
            if ENABLE_SD:
                confirmation = "File {} stored via SD card".format(strname)
                print(confirmation)
                if DEBUG:
                    writeToUARTln(confirmation)
                infoArray = np.empty(6)
                newfreq = Increment_frequency + sample_rate
                infoArray[0] = 0
                infoArray[1] = 420e6
                infoArray[3] = 512e6
                infoArray[4] = 2.5e6
                infoArray[5] = 0
                
                if newfreq >= Finish_frequency:
                    print("Setting increment frequency back to minimum frequency")
                    if DEBUG:
                        writeToUARTln("Setting increment frequency back to minimum frequency")
                    infoArray[2] = Start_frequency
                else:
                    infoArray[2] = newfreq
                    print('Data Updated')
                    if DEBUG:
                        writeToUARTln("Data Updated on SD card")
                        
                writeFile = open(SDDIR + 'config.txt', 'w')
                writeFile.write(str(infoArray[0]) + ', ' + str(infoArray[1]) + 
                ', ' + str(infoArray[2]) + ', ' + str(infoArray[3]) + ', ' + 
                str(infoArray[4]) + ', ' + str(infoArray[5]))
                writeFile.close()
            else:
                pass
    else:
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
        

''' Function to write string to UART '''
def writeToUART(message):
    ser.open()
    if ser.isOpen():
        ser.write(str(message))
        #print("Serial is open!")
    ser.close()


''' Same as write to UART except adds a carriage return '''
def writeToUARTln(message):
    ser.open()
    if ser.isOpen():
        ser.write(str(message) + '\n')
        #print("Serial is open!")
    ser.close()


if __name__ == '__main__':
    main()
