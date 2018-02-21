import socket

def InternetCheck():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("gmail.com",80))
        #print("IP: " + s.getsockname()[0])
        s.close()
        return True
        
    except Exception:
        #print("Not connected to internet")
        return False
        
if __name__ == '__main__':
    IPcheck = InternetCheck()
    
    if(IPcheck):
        print('Internet Connected')
    else:
        print('No Internet Sorry')