#!/usr/bin/python

__description__ = 'DarkComet Traffic Generation'
__author__ = 'Kevin Breen http://malwareconfig.com'
__version__ = '0.2'
__date__ = '2015/06/03'

# Creates multiple Fake Connections to a DC Client

import socket
import struct
import random
from time import *
from optparse import OptionParser
import sys
from Crypto.Cipher import ARC4
import uuid


def recv(s):
    data = decrypt_traffic(s.recv(1024))
    #print "Recieved -> %s\n" % data
    return data
    
def send(s, text):
    #print "Sending -> %s\n" % text
    data = encrypt_traffic(text)
    s.send(data)
    
def encrypt_traffic(text, enc_key):
    cipher = ARC4.new(enc_key)
    return cipher.encrypt(text).encode('hex').upper()
    
def decrypt_traffic(text, enc_key):
    new_text = text.decode('hex')
    cipher = ARC4.new(enc_key)
    return cipher.decrypt(new_text).upper()

def unique_connection(port):
    
    campaign_name = 'BSIDESLDN'
    int_ip = '192.168.'
    int_ip += ".".join(map(str, (random.randint(1,254) for _ in range(2))))
    ext_ip = socket.inet_ntoa(struct.pack('>I', random.randint(1, 0xffffffff)))
    ram = random.randint(22,85)
    username = random.choice(['John', 'Peter', 'Flash', 'Bruce', 'Picard', 'Satan', 'Mal', 'Sarah', 'Emma', 'Jessica', 'Office'])
    hostname = '{0}s-PC'.format(username)
    idle = random.randint(0,5000)
    country = random.choice(['English (United States) US', 'ENGLISH (UNITED KINGDOM) GB'])
    country_code = country[-2:]
    os_value = random.choice(['Windows 7 Service Pack 1 [7601] 32 bit', 'Windows 7 Service Pack 1 [7601] 64 bit', 'Windows XP Service Pack 3 [2600] 32 bit', 'Windows Server 2003 Service Pack 2 [3790] 32 bit', 'Unknow [9200] 64 bit'])
    active_window = 'C:\Windows\cmd.exe'
    conn_string = 'infoes{0}|{1} / [{2}] : {3}|{4} / {5}|2495609|{6}S|{7} ( C:\ )|- (LIMITED)||{8}|{9}|{10}|{11}%|{12} /  -- |22/05/2015 AT 17:16:23|5.3.0'.format(campaign_name, ext_ip, int_ip, port, hostname, username, idle, os_value, country_code, active_window, str(uuid.uuid4()), ram, country)
    return conn_string

def run(dst_host, dst_port, enc_key):


    print "[+] Generating Fake Connections"
    print "    [-] Ctrl + c to Stop"
    
    #connecting to the server
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.connect((dst_host, dst_port))
    
    #Getting IDTYPE sent by the server
    data = s.recv(1024)
    
    #Reply to the server
    s.send(encrypt_traffic('SERVER', enc_key))
    wtf = s.recv(1024)  
            
    counter = 0
    while True:
        try:
            # send fake connection
            conn_string = unique_connection(dst_port)
            s.send(encrypt_traffic(conn_string, enc_key))
            sleep(0.3)
            counter += 1
        except KeyboardInterrupt:
            print "[+] Stopping Fake Connections after {0} connections".format(counter)
            s.close()
            sys.exit()


if __name__ == "__main__":
    parser = OptionParser(usage='usage: %prog host port\n' + __description__, version='%prog ' + __version__)
    parser.add_option("-k", dest="enc_key", help="Encryption Key")
    
    (options, args) = parser.parse_args()
    # If we dont have args quit with help page
    if len(args) > 0:
        pass
    else:
        parser.print_help()
        sys.exit()
    if len(args) == 2 and options.enc_key:
		run(args[0], int(args[1]), options.enc_key)
    else:
        parser.print_help()
        sys.exit()
    
