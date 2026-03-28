# -*- coding: utf-8 -*-

import psutil
import time
import os
import yaml

''' 
For current Debian/Ubuntu, use apt-get install python3-pip to install pip3.
'''

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    
if os.geteuid() != 0:
    exit("You need to have root privileges to run this script.\nPlease try again, this time using 'sudo'. Exiting.")

print(f"Start...")

# Pfad zur YAML bestimmen (gleiches Verzeichnis wie das Skript)
base_path = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(base_path, "config.yaml")

# YAML laden
with open(config_path, "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

#Limits
limitNetz = config["limitNetz"]
limitCPU = config["limitCPU"]

#Name Netzwerkadapter
adapter = config["adapter"]

#für Übertragungsrate:
net_stat = psutil.net_io_counters(pernic=True, nowrap=True)[adapter]
net_in_1 = net_stat.bytes_recv
net_out_1 = net_stat.bytes_sent
net_lastSampleTime = round(time.time())-1

#Wartezeiten
minAllg = config["minAllg"]
minSleep = config["minSleep"]

sleep_lastSampleTime = round(time.time())

#Timer
zeitNetz = round(time.time())
zeitCPU = round(time.time())
zeitDatei = round(time.time())
zeitSleep = round(time.time())

#booleans
boolNetz = False
boolCPU = False
boolDatei = False
boolSleep = False

loopround = 0

try:
    while True:
        
        if loopround == 0:
            print(f"{bcolors.ENDC}", end='')
            print("CPU".ljust(10)+"Netz".ljust(10)+"Datei".ljust(10)+"Sleep".ljust(10))
        
        loopround += 1
        if loopround >= 10:
            loopround=0
        
        looptime = round(time.time())
        
        ##### CPU-Auslastung #####
        cpu = psutil.cpu_percent()
        #print(f"CPU-Auslastung {cpu}")
        
        if cpu <= limitCPU:
            pass #Zeit wird nicht verändert
        else:
            zeitCPU = looptime
            
        if looptime - zeitCPU >= minAllg:
            boolCPU = True
            print(f"{bcolors.OKGREEN}", end='')
        else:
            boolCPU = False
            print(f"{bcolors.WARNING}", end='')
        print(str(looptime - zeitCPU).ljust(10), end='')
        
        ##### Netzwerk-Übertragungsrate #####
        net_stat = psutil.net_io_counters(pernic=True, nowrap=True)[adapter]
        net_in_2 = net_stat.bytes_recv
        net_out_2 = net_stat.bytes_sent
             
        net_in_total = (net_in_2 - net_in_1) / 1024 #kB/s
        net_out_total = (net_out_2 - net_out_1) / 1024 #kB/s
        net_in_per_second = round(net_in_total/(looptime - net_lastSampleTime),0)
        net_out_per_second = round(net_out_total/(looptime - net_lastSampleTime),0)
        #print(f"Current net-usage: IN: {net_in_per_second} MB/s, OUT: {net_out_per_second} MB/s")
        
        net_in_1 = net_in_2
        net_out_1 = net_out_2
        net_lastSampleTime = looptime
        
        if net_in_per_second <= limitNetz and net_out_per_second <= limitNetz:
            pass #Zeit wird nicht verändert
        else:
            zeitNetz = looptime
            
        if looptime - zeitNetz >= minAllg:
            boolNetz = True
            print(f"{bcolors.OKGREEN}", end='')
        else:
            boolNetz = False
            print(f"{bcolors.WARNING}", end='')
        print(str(looptime - zeitNetz).ljust(10), end='')   
        
        ##### Prüfung, ob Datei geöffnet #####
        # Benötigt sudo: Test, ob Datei geöffnet
        fpath = config["fpath"]
        booltmp = False
        for proc in psutil.process_iter():
            try:
                for item in proc.open_files():
                    #tmp = Path(item.path)
                    #print(f"{item.path}")
                    if fpath == item.path:
                        #print(f"true")
                        booltmp = True
            except Exception:
                pass
        
        if booltmp:
            zeitDatei = looptime
            
        if looptime - zeitDatei >= minAllg:
            boolDatei = True
            print(f"{bcolors.OKGREEN}", end='')
        else:
            boolDatei = False
            print(f"{bcolors.WARNING}", end='')
        print(str(looptime - zeitDatei).ljust(10), end='')
        
        ##### Zeit seit StandBy #####
        ### Versuch, letzten StandBy zu erkennen:
        # Wenn die Schleife für 30 Sekunden nicht lief, dann vermutlich im StandBy
        
        if looptime - sleep_lastSampleTime >= 30:
            # war im StandBy
            zeitSleep = looptime
            zeitNetz = looptime
            zeitCPU = looptime
            zeitDatei = looptime

        sleep_lastSampleTime = looptime # merkt sich, wann zuletzt geprüft wurde
            
        if looptime - zeitSleep >= minSleep:
            boolSleep = True
            print(f"{bcolors.OKGREEN}", end='')
        else:
            boolSleep = False
            print(f"{bcolors.WARNING}", end='')
        print(str(looptime - zeitSleep).ljust(10), end='')
        
        print("")
        
        if boolCPU and boolNetz and boolDatei and boolSleep:
            print(f"{bcolors.WARNING}", end='')
            print("Sleep in 10 s, Abbruch mit 'STRG+C'")
            time.sleep(1)
            for c in range(10,0,-1):
                print(f"Sleep in {c} s")
                time.sleep(1)
            os.system("systemctl suspend")
        
        time.sleep(10)
  
except KeyboardInterrupt:
    pass