DarkComet ToolKit
===========
Python tools for interacting with a DarkComet Controller.

Grab the slides from my site - https://techanarchy.net/?attachment_id=836

Watch the video on YouTube
https://youtu.be/tRM6HrW7BAc

###Current Tools
 - DC_TrafficGenerator.py This will create multiple fake connections with fake connection strings
 - DC_FileFetch.py This will read a file from the DarkComet Controller.
 - DC_dbparse.py Extracts information from a DarkComet DataBase file.

###Usage

- Each Script comes with its own -h option use it :)

###Password / Key
DarkComet always requires a key. The key is formed from two parts. 
- The Version Password
- The User Password
The user pass is optional and if set is apended to the version password e.g. ```#KCMDDC51#-8900123456789```

##Default Version Passwords
- #KCMDDC2#-890
- #KCMDDC4#-890
- #KCMDDC42#-890
- #KCMDDC42F#-890
- #KCMDDC5#-890
- #KCMDDC51#-890

###Future Tools

- DC_Sinkhole.py - This is designed to sit on a sinkholed domain or IP. It will log connections then optionaly issue an uninstall command to the victim.

###Credits

Full credit where credit is due. 

Shawn Denbow and Jesse Herts for their paper and POC. - http://www.matasano.com/research/PEST-CONTROL.pdf 

