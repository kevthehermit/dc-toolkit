#!/usr/bin/env python

__description__ = 'Process DarkComet DataBase File'
__author__ = 'Kevin Breen @KevTheHermit'
__version__ = '0.1'
__date__ = '2015/05/25'

import os
import sys
import sqlite3
from datetime import datetime
import hashlib
import string
import json
from optparse import OptionParser
from collections import Counter

geoip_map = '''
<html>
  <head>
    <script type="text/javascript" src="https://www.google.com/jsapi"></script>
    <script type="text/javascript">
      google.load("visualization", "1", {packages:["intensitymap"]});
      google.setOnLoadCallback(drawChart);

      function drawChart() {

        var data = google.visualization.arrayToDataTable([
          ['Country', 'Count'],
          {{replace_me}}
        ]);
        var options = {
        colors: '#3333FF'
        };
        var chart = new google.visualization.IntensityMap(document.getElementById('chart_div'));

        chart.draw(data, {});
      }
    </script>
  </head>
  <body>
    <div id="chart_div"></div>
  </body>
</html>
'''

###
# DataBase Functions
###

class Dictionary(dict):
    def __getattr__(self, key):
        return self.get(key, None)

    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

def dict_factory(cursor, row):
    d = Dictionary()
    for idx, col in enumerate(cursor.description):
        setattr(d, col[0], row[idx])
    return d

def geo_ip(res_type, ip):
    try:
        import pygeoip
        gi = pygeoip.GeoIP('GeoIP.dat')
        if res_type == 'name':
            return gi.country_name_by_addr(ip)
        if res_type == 'cc':
            return gi.country_code_by_addr(ip)
        return gi.country_code_by_addr(ip)
    except Exception as e:
        print e
        return ''

#----------------------------------------------------------------------
# Search
#----------------------------------------------------------------------
       
def get_userrows(cursor):
    result = []
    for row in cursor.execute("SELECT * FROM dc_users").fetchall():
        result.append(row)
    return result

def cc_data(user_rows):
    # get a list of all Country codes
    country = []
    cc_output = ''
    for row in user_rows:
        ext_ip = row['userIP'].split(' / ')[0]
        country.append(geo_ip('cc', ext_ip))

    country_counts = dict((i,country.count(i)) for i in country)
    for k,v in country_counts.iteritems():
        if k != '':
            cc_output += "['{0}', {1}],\n".format(k,v)
    return cc_output


def os_data():
    os_list = []
    for row in user_rows:
        os_list.append(row['userOS'].split(' [')[0])
    os_type = dict((i,os_list.count(i)) for i in os_list)
    return os_type  

def key_data(cursor):
    all_log = ''
    for row in cursor.execute("SELECT * FROM dc_keyloggers").fetchall():
        try:
            dc_uuid = row['UUID']
            date = row['name'][:-3]
            content = row['content'].decode('hex')
            all_log += '{0}\n{1} - {2}\n{3}\n{4}\n'.format('='*66,  dc_uuid, date,' -'*33, content)
        except:
            content = row['content'][:-1].decode('hex')
            all_log += '{0}\n{1} - {2}\n{3}\n{4}\n'.format('='*66,  dc_uuid, date, ' -'*33, content)
    return all_log
    

def main():
    parser = OptionParser(usage='usage: %prog [options] comet.db\n' + __description__, version='%prog ' + __version__)
    parser.add_option("-c", "--count", action='store_true', default=False, help="Count Infected Hosts")
    parser.add_option("-e", "--export", dest='export', default=False, help="Export Infected Hosts as CSV")
    parser.add_option("-g", "--geoip", action='store_true', default=False, help="Get Country Code from IP")
    parser.add_option("-H", "--heatmap", action='store_true', default=False, help="Create Google HeatMap by Country")
    parser.add_option("-k", "--keylogs", dest='keylogs', default=False, help="Extract Key Logs")
    (options, args) = parser.parse_args()
 
    if len(args) == 0:
        print "[+] You need to give me some Paths"
        parser.print_help()
        sys.exit()
 
    # Sort args
    db_file = args[0]
     
    print "[+] Connecting to DataBase File"

    try:
        conn = sqlite3.connect(db_file, timeout=60)
        conn.row_factory = dict_factory
        cursor = conn.cursor()
        conn.text_factory = str
    except:
        print "Unable to read Database. Is it comet.db?"
        return

    print "  [-] Checking for DarkComet"
    try:
        user_rows = get_userrows(cursor)
        user_count = len(user_rows)
        print "  [-] Found {0} Infected Hosts".format(user_count)
        
        # Export all Connection Details
        if options.export:
            with open(options.export, 'w') as out:
                # Header
                out.write('HostName,UserName,WAN-IP,LAN-IP,OS,CountryCode,CountryName\n')
                for row in user_rows:
                    hostname = row['userName'].split(' / ')[0]
                    username = row['userName'].split(' / ')[1]
                    wanip = row['userIP'].split(' / ')[0]
                    lanip = row['userIP'].split(' / ')[1].split(':')[0][1:-2]
                    opsys = row['userOS']
                    if options.geoip:
                        countrycode = geo_ip('cc', wanip)
                        countryname = geo_ip('name', wanip)
                    else:
                        countrycode = ''
                    write_out = '{0},{1},{2},{3},{4},{5},{6}\n'.format(hostname, username, wanip, lanip, opsys, countrycode, countryname)
                    out.write(write_out)
            
        
        # Get Keylogs
        if options.keylogs:
            print "  [-] Exporting Keylogs"
            with open(options.keylogs, 'a') as out:
                out.write(key_data(cursor))
                
        if options.heatmap:
            cc_output = cc_data(user_rows)
            with open('heatmap.html', 'w') as out:
                out.write(geoip_map.replace('{{replace_me}}', cc_output))
    except Exception as e:
        print e
        print "Unable to read Database. Is it comet.db?"
        return
        
    # Close the Connection
    print "[+] Closing Connection to Database File"
    conn.close()
 
 
if __name__ == "__main__":
    main()
             
            

    
