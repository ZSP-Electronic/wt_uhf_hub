def RecordSym(sec):
    if sec == "offSym":
        section = bytearray([0x00,0x0E,0x11,0x11,0x11,0x11,0x0E,0x00])
    if sec == "onSym":
        section = bytearray([0x00,0x0E,0x1F,0x1F,0x1F,0x1F,0x0E,0x00])
    if sec == "internetOn":
        section = bytearray([0x1F,0x04,0x04,0x04,0x04,0x04,0x04,0x1F])
    if sec == "internetOff":
        section = bytearray([0x1F,0x0E,0x15,0x15,0x15,0x15,0x0E,0x1F])
    return section
    
def RingofPower(stuff):
    if stuff == 'topleft':
        power = bytearray([0x00,0x0C,0x18,0x10,0x00,0x00,0x00,0x00])
    if stuff == 'topright':
        power = bytearray([0x00,0x06,0x03,0x01,0x00,0x00,0x00,0x00])
    if stuff == 'bottomright':
        power = bytearray([0x00,0x00,0x00,0x01,0x03,0x06,0x00,0x00])
    if stuff == 'bottomleft':
        power = bytearray([0x00,0x00,0x00,0x10,0x18,0x0C,0x00,0x00])
    return power
    
