def from_bytes(bytes_message):
    status = bytes_message[0]
    data1 = None
    data2 = None
    command = bytes_message[0] & 0xF0
    channel = None
    
    if len(bytes_message) > 1:
        data1 = bytes_message[1]
    if len(bytes_message) == 3:
        data2 = bytes_message[2]
    
    if command >= 0x80 and command <= 0xE0:
        channel = (status & 0x0F) + 1

    return {
        'status': status,
        'command': command,
        'data1': data1,
        'data2': data2,
        'channel': channel,
    }

def get_channel(bytes_message):
    status = bytes_message[0]
    command = status & 0xF0
   
    if command >= 0x80 and command <= 0xE0:
        return (status & 0x0F) + 1
    
    return None

def to_bytes(message):
    status = message['status']
    if message['channel'] != None:
        status = (message['command'] | message['channel']) - 1

    if message['data1'] != None and message['data2'] != None:
        return [status, message['data1'], message['data2']]
    elif message['data1'] != None:
        return [status, message['data1']]
    else:
        return [status]