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
from i2c_lcd import I2cLcd
import customChar
import Adafruit_BBIO.GPIO as GPIO
import socket
import time
import serial
import os
#import timeit 
import numpy as np
from google.cloud import storage

def introScreen():
    ''' Intro Screen '''
    lcd.clear()
    lcd.move_to(2,0)
    lcd.putstr('Wave TechUHF')
    lcd.move_to(4,1)
    lcd.putstr('UHF Hub')
    time.sleep(3)

def mainScreen():
    ''' Main Screen '''
    lcd.custom_char(0,customChar.RecordSym('offleft'))
    lcd.custom_char(1,customChar.RecordSym('offright'))
    lcd.custom_char(2,customChar.RecordSym('onleft'))
    lcd.custom_char(3,customChar.RecordSym('onright'))
    lcd.move_to(0,0)
    lcd.putchar(chr(0))
    lcd.move_to(1,0)
    lcd.putchar(chr(1))
    lcd.move_to(5, 0)
    lcd.putstr(time.strftime('%m/%d %H:%M', time.localtime()))


LCD_I2C_ADDR = 0x3f
lcd = I2cLcd(1, LCD_I2C_ADDR, 2, 16)
introScreen()

from google.cloud import datastore

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
CONFIGDIR = '/media/card/config.txt'
UART_PORT = '/dev/ttyO4'
CD_PIN = 'P2_35'

DEBUG = False
ENABLE_SD = True
request = False


''' Section to detect if Credentials file exists. if not it creates it'''
def fileCheck():
    global JSON_LOC, BUCKET_NAME, KIND, ID_NAME, ADV_NAME
    
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
                
            # print("Output to LCD: Credentials file created.\
            # Input credentials and restart")
            while True:
                lcd.move_to(0,0)
                lcd.putstr('Credential File')
                lcd.move_to(4,1)
                lcd.putstr('Created.')
                time.sleep(5)
                lcd.clear()
                lcd.move_to(0,0)
                lcd.putstr('Input credential')
                lcd.move_to(1,0)
                lcd.putstr('and Restart')
                time.sleep(5)
        else:
            f = open(CREDDIR, 'r')
            information = f.readlines()
            infoArray = np.empty(6, dtype='U256')
            for index, lines in enumerate(information):
                tempinfo = lines.split(":")
                infoArray[index] = tempinfo[1].replace("\n", '')
            
            JSON_LOC = SDDIR + str(infoArray[0])
            #CD_PIN = str(infoArray[1])
            BUCKET_NAME = str(infoArray[2])
            KIND = str(infoArray[3])
            ID_NAME = str(infoArray[4])
            ADV_NAME = str(infoArray[5])
    else:
        pass


hackrf = hackrfCtrl(DEBUG)
lcd.clear()

# SD card object declaration
if ENABLE_SD:
    GPIO.setup(CD_PIN, GPIO.IN)
    
if DEBUG:
    #print("Importing UART")
    ser = serial.Serial(port=UART_PORT, baudrate=115200)
    ser.close()

''' This is the main function that runs on startup. First determines if sd card
    is inserted so device can work. Then runs a request from the Datastore 
    database if connected to internet. It then runs the HackRF and stores its 
    data in a file and stores it appropriately. '''
def main():
    global timer1, timer2
    
    if DEBUG:
        writeToUARTln('Start Main')
    else:
        print("Start Main")
    
    timer1 = time.time()
    timer2 = time.time()
    filecheck = False
    
    while True:
        if ENABLE_SD:
            if not GPIO.input(CD_PIN):
                if not filecheck:
                    fileCheck()
                    filecheck = True
                mainScreen()
                dataStoreCheck()
            else:
                lcd.move_to(1,0)
                lcd.putstr("Insert SD Card")
                lcd.move_to(0,1)
                lcd.putstr('Unplug to start')
                #time.sleep(5)
        else:
            mainScreen()
            dataStoreCheck()
            
            
''' This function checks the interntflag and determines if should request data
    from dataStore or to use the sd card to store file '''
def dataStoreCheck():
    global JSON_LOC, BUCKET_NAME, KIND, ID_NAME, ADV_NAME
    global timer1, timer2
    global request
    global InternetFlag
    
    data = []
    ''' First "if" statement checks if timer1 is greater than specified
    time and if connected to internet request from Datastore. '''
    if time.time() - timer1 > TIMER1_TIME:
        InternetFlag = InternetCheck()
        if InternetFlag:
            lcd.clearRow(1)
            lcd.move_to(0,1)
            lcd.putstr('Requesting Data')
            
            if DEBUG:
                writeToUARTln('Requesting Data from Datastore')
            else:
                print('Requesting Data')
            try:
                data = onlineData()
            except Exception:
                print('Datastore Timeout')
                data = offlineData()
            
                            
            timer1 = time.time()
        else:
            '''This is for if not connected to internet. Nothing much
               to do besides nothing '''
            lcd.clearRow(1)
            lcd.move_to(0,1)
            lcd.putstr('Reading Params')
            time.sleep(2)
            
            if DEBUG:
                writeToUARTln('Requesting Data from SD config file')
            else:
                print("No Internet == Read SD card")
                
            data = offlineData()
            
            timer1 = time.time()
                        
    ''' Second "if" statement is used to run the hackrf. The global 
        variables allow the database to set them and be placed into
        this function. '''
    if time.time() - timer2 > TIMER2_TIME:
        runHackrf(InternetFlag, data)
        GPIO.output("USR3", GPIO.LOW)            
        timer1 = time.time()
        timer2 = time.time()
        
def onlineData():
    #Request data from database
    client = datastore.Client.from_service_account_json(JSON_LOC)
    key_complete = client.key(KIND, ID_NAME)
    tasks = client.get(key_complete)
                        
    #Put properties of request into varaibles
    request = tasks['Request']
    advRequest = tasks['ADV_Request']
    minFreq = tasks['min_frequency']
    incremFreq = tasks['increment_frequency']
    maxFreq = tasks['max_frequency']
    samprate= tasks['sample_rate']
    lna = tasks['lna']
    vga = tasks['vga']
    numscans = tasks['Scans']
    data = [minFreq, incremFreq, maxFreq, samprate, lna, vga, numscans]
            
    lcd.clearRow(1)
    lcd.move_to(0,1)
    lcd.putstr('{} to {}'. format(incremFreq/1.0e6, (incremFreq + samprate)/1.0e6))
            
    if DEBUG:
        for element in data:
            writeToUART(element)
        writeToUART('\n')
    else:
        print(data)
                        
    #If there was a request collect hackrf data immediately
    if request == True:
        runHackrf(InternetFlag, data)
        timer2 = time.time()
    
    return data
        
def offlineData():
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

    data = [minFreq, incremFreq, maxFreq, samprate]
            
    lcd.clearRow(1)
    lcd.move_to(0,1)
    lcd.putstr('{} to {}'. format(incremFreq/1.0e6, (incremFreq + samprate)/1.0e6))
            
    if DEBUG:
        for element in data:
            writeToUART(element)
        writeToUART('\n')
    else:
        print(data)
        
    return data


'''The Hackrf run function determines if the internet is connected. If it is
    then use the parameters passed from the database otherwise read the 
    parameters from the sd card. Run the hackrf the appropriate amount of times
    then save it to a file and save the file appropriately. '''
def runHackrf(internetflag, dataParams=[]):
    global JSON_LOC, BUCKET_NAME, KIND, ID_NAME, ADV_NAME
    global ENABLE_SD
    
    ''' Start of Hackrf Func '''
    lcd.move_to(0,0)
    lcd.putchar(chr(2))
    lcd.move_to(1,0)
    lcd.putchar(chr(3))
    #Error = False
    #Collect the data
    if internetflag:
        lna = dataParams[4]
        vga = dataParams[5]
        scans = int(dataParams[6])
    else:
        lna = 16
        vga = 20
        scans = 5
    
    ''' Increment Frequency + sample rate/2 '''
    center_frequency = int(dataParams[1] + (dataParams[3]/2))
    
    data_pts = hackrf.setParameters(center_frequency, dataParams[3], lna, vga)
        
    iq, Error = hackrf.hackrf_run(scans)
    
    ''' End of Hackrf Func '''
    lcd.custom_char(0,customChar.RecordSym('offleft'))
    lcd.custom_char(1,customChar.RecordSym('offright'))
    lcd.custom_char(2,customChar.RecordSym('onleft'))
    lcd.custom_char(3,customChar.RecordSym('onright'))
    lcd.clearRow(1)
    lcd.move_to(0,0)
    lcd.putchar(chr(0))
    lcd.move_to(1,0)
    lcd.putchar(chr(1))
    lcd.move_to(0,1)
    lcd.putstr('Record Complete')
    
    if not Error:
        ''' Store data to file name '''
        strname = str(time.strftime('%m-%d_%H-%M_', time.localtime()) + \
        str(dataParams[1]/1e6) + 'e6-' + \
        str((dataParams[1] + dataParams[3])/1e6) + 'e6')
        
        if DEBUG:
            writeToUARTln(strname)
        else:
            print(strname)
        
        if internetflag:
            ''' Save npz file '''
            np.savez_compressed(os.path.join(SDSAVEDFILESDIR, strname), data_pts = data_pts, iq = iq)
        else:
            np.savez_compressed(os.path.join(SDSAVEDFILESDIR, strname), data_pts = data_pts, iq = iq)
            
        strname = strname + '.npz'
        
        ''' Perform second internet check if internet lost during hackrf capture'''
        newInternetFlag = InternetCheck()
        
        #Save file to storage or SD card
        if newInternetFlag:
            hackrf.close()
            storage_client = storage.Client.from_service_account_json(JSON_LOC)
            
            bucket = storage_client.get_bucket(BUCKET_NAME)
                        
            blob = bucket.blob(os.path.basename(SDSAVEDFILESDIR + strname))
            blob.upload_from_filename(SDSAVEDFILESDIR + strname)
            confirmation = "File {} stored via Cloud".format(strname)
            if DEBUG:
                writeToUARTln(confirmation)
            else:
                print(confirmation)
            #os.remove(strname)
            os.path.join(SDSAVEDFILESDIR, strname)
            
            #Request data from database
            client = datastore.Client.from_service_account_json(JSON_LOC)
            key_complete = client.key(KIND, ID_NAME)
            tasks = client.get(key_complete)
                    
            #Put properties of request into varibles
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
                if DEBUG:
                    writeToUARTln("Data Updated")
                else:
                    print('Data Updated')

            client.put(tasks)
            ''' Uploading ''' 
            lcd.clearRow(1)
            lcd.move_to(0,1)
            lcd.putstr('Upload Complete')
            time.sleep(3)
            lcd.clearRow(1)
        else:
            hackrf.close()
            if ENABLE_SD:
                confirmation = "File {} stored via SD card".format(strname)
                if DEBUG:
                    writeToUARTln(confirmation)
                else:
                    print(confirmation)
                infoArray = np.empty(6)
                newfreq = dataParams[1] + dataParams[3]
                infoArray[0] = 0
                infoArray[1] = 420e6
                infoArray[3] = 512e6
                infoArray[4] = 2.5e6
                infoArray[5] = 0
                
                if newfreq >= dataParams[2]:
                    if DEBUG:
                        writeToUARTln("Setting increment frequency back to minimum frequency")
                    else:
                        print("Setting increment frequency back to minimum frequency")
                    infoArray[2] = dataParams[0]
                else:
                    infoArray[2] = newfreq
                    if DEBUG:
                        writeToUARTln("Data Updated on SD card")
                    else:
                        print('Data Updated')
                        
                writeFile = open(CONFIGDIR, 'w')
                writeFile.write(str(infoArray[0]) + ', ' + str(infoArray[1]) + 
                ', ' + str(infoArray[2]) + ', ' + str(infoArray[3]) + ', ' + 
                str(infoArray[4]) + ', ' + str(infoArray[5]))
                writeFile.close()
                ''' Uploading ''' 
                lcd.clearRow(1)
                lcd.move_to(0,1)
                lcd.putstr('Update Complete')
                time.sleep(2)
                lcd.clearRow(1)
            else:
                pass
    else:
        ''' When Error is reported ''' 
        lcd.move_to(0,1)
        lcd.putstr('Reported Error')
        time.sleep(2)
        lcd.clearRow(1)
        if DEBUG:
            writeToUARTln("Reported Error")
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
