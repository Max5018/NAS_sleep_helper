# -*- coding: utf-8 -*-

import psutil
import time
import os

''' Nützliches
While-Schleife mit Tastatur beenden
    https://stackoverflow.com/questions/13180941/how-to-kill-a-while-loop-with-a-keystroke
Zahl runden:
    https://www.programiz.com/python-programming/methods/built-in/round
Zeit messen:
    https://stackoverflow.com/questions/7370801/how-to-measure-elapsed-time-in-python
kombiniert:
    round(time.time())
PC zu sleep:
    https://gist.github.com/zkneupper/8c1faed1296ff0eb8923e6f2ee6fb74c
    import os
    os.system("systemctl suspend")
Skript Pause / Sleep
    time.sleep(zeit)
Zeit seit Systemstart (nicht Standby-Aufwachen)
    https://stackoverflow.com/questions/42471475/fastest-way-to-get-system-uptime-in-python-in-linux
    time.time() - psutil.boot_time()
print mit Farben
    https://stackoverflow.com/questions/287871/how-to-print-colored-text-to-the-terminal
    test = "\033[95mtest\ttest\t\033[96mhallo\t\033[0mtest"
    print(test)
    print(f"{bcolors.WARNING}Warning:")
print ohne neue Zeile
    https://stackoverflow.com/questions/493386/how-to-print-without-a-newline-or-space
    print('xyz', end='')
print('\033[94mxyz', end='')
print('\033[0mxyz', end='')
    


For current Debian/Ubuntu, use
apt-get install python3-pip
to install pip3.
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

#Limits
limitNetz = 10 #kB/s
limitCPU = 30 # in %

#Name Netzwerkadapter
# "wlp4s0" WLAN
# "enp2s0" LAN
#adapter = "wlp4s0"
adapter = "enp2s0"

#für Übertragungsrate:
net_stat = psutil.net_io_counters(pernic=True, nowrap=True)[adapter]
net_in_1 = net_stat.bytes_recv
net_out_1 = net_stat.bytes_sent
net_lastSampleTime = round(time.time())-1

#Wartezeiten
minAllg = 10*60
minSleep = 5*60

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
        # https://stackoverflow.com/questions/276052/how-to-get-current-cpu-and-ram-usage-in-python
        cpu = psutil.cpu_percent()
        #print(f"CPU-Auslastung {cpu}")
        # CPU-Auslastung 7.3
        
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
        # https://stackoverflow.com/questions/62020140/psutil-network-monitoring-script
        #inf = "wlp4s0"
        #net_stat = psutil.net_io_counters(pernic=True, nowrap=True)[adapter]
        #net_in_1 = net_stat.bytes_recv
        #net_out_1 = net_stat.bytes_sent
        #time.sleep(1)
        net_stat = psutil.net_io_counters(pernic=True, nowrap=True)[adapter]
        net_in_2 = net_stat.bytes_recv
        net_out_2 = net_stat.bytes_sent
        
        #net_in = round((net_in_2 - net_in_1) / 1024 / 1024, 3) #MB/s
        #net_out = round((net_out_2 - net_out_1) / 1024 / 1024, 3) #MB/s
        #net_in = round((net_in_2 - net_in_1) / 1024, 3) #kB/s
        #net_out = round((net_out_2 - net_out_1) / 1024, 3) #kB/s
        #print(f"Current net-usage: IN: {net_in} MB/s, OUT: {net_out} MB/s")
        # IN: 0.0 MB/s, OUT: 0.0 MB/s
        
        net_in_total = (net_in_2 - net_in_1) / 1024 #kB/s
        net_out_total = (net_out_2 - net_out_1) / 1024 #kB/s
        net_in_per_second = round(net_in_total/(looptime - net_lastSampleTime),0)
        net_out_per_second = round(net_out_total/(looptime - net_lastSampleTime),0)
        
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
        fpath = "/media/Daten/Freigabe/file.ext"
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
        # Wenn die Schleife für 5 Minuten nicht lief, dann vermutlich im StandBy
        
        if looptime - sleep_lastSampleTime >= 300:
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