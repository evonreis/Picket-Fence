#!/usr/bin/env python

from pcaspy import Driver, SimpleServer
from gpstime import gpsnow, gpstime
from socket import gethostname
import os
import time
import threading

start_gps = 0


def gps_to_str(gps: float):
    "convert a gps epoch into a UTC string"
    return gpstime.fromgps(int(gps)).strftime("%Y-%m-%d %H:%M:%S %Z")


def delta_seconds_to_readable(sec_f: float) -> str:
    """
    Convert a delta-seconds value into a human readable string.
    """

    sec = int(sec_f)
    sign = ""
    if sec < 0:
        sec = -sec
        sign = "-"
    if sec < 120:
        return f"{sign}{sec} sec."
    mins = sec // 60
    if mins < 120:
        return f"{sign}{mins} min."
    hours = mins // 60
    if hours < 48:
        return f"{sign}{hours} hours"
    days = hours//24
    if days < 14:
        return f"{sign}{days} days"
    weeks = days // 7
    months = days // 30
    if months < 2:
        return f"{sign}{weeks} weeks"
    years = int(days / 365.24)
    if years < 2:
        return f"{sign}{months} months"
    return f"{sign}{years} years"


class myDriver(Driver):
    def  __init__(self):
        super(myDriver, self).__init__()
        tid = threading.Thread(target=self.process)
        tid.setDaemon(True)
        tid.start()


    def process(self):
        global start_gps
        while True:
            now_gps = gpsnow()

            # handle IOC variables
            self.setParam("IOC_GPS", now_gps)
            uptime_sec = int(now_gps - start_gps)
            self.setParam("IOC_UPTIME_SEC", uptime_sec)
            self.setParam("IOC_UPTIME_STR", delta_seconds_to_readable(uptime_sec))

            # handle some server variables
            server_start_gps = self.getParam("SERVER_START_GPS")
            self.setParam("SERVER_START_STR", gps_to_str(server_start_gps))
            server_gps = self.getParam("SERVER_GPS")
            server_uptime_sec = int(server_gps - server_start_gps)
            self.setParam("SERVER_UPTIME_SEC", server_uptime_sec)
            self.setParam("SERVER_UPTIME_STR", delta_seconds_to_readable(server_uptime_sec))
            last_process_gps = self.getParam("LAST_PROCESS_GPS")
            self.setParam("LAST_PROCESS_STR", gps_to_str(last_process_gps))
            since_last_process_sec = int(now_gps - last_process_gps)
            self.setParam("SINCE_LAST_PROCESS_SEC", since_last_process_sec)
            self.setParam("SINCE_LAST_PROCESS_STR", delta_seconds_to_readable(since_last_process_sec))

            if since_last_process_sec > 60:
                # lagged out!  Not updating regularly
                self.setParam("SERVER_RUNNING", 2)
            elif since_last_process_sec >= 0:
                # running ok
                self.setParam("SERVER_RUNNING", 1)
            else:
                # invalid
                self.setParam("SERVER_RUNNING", 0)
            self.updatePVs()
            time.sleep(0.1)


def func(n):  ## creates all our EPIC variables
    dicts = []
    for i in range(1, n+1):
        dic = {}
        starter = f"STATION_0{i}_" if i < 10 else f"STATION_{i}_"
        dic[starter + "LON"] = {'prec' : 3}  ## longitude
        dic[starter + "LAT"] = {'prec' : 3}  ## latitude
        dic[starter + "MIN"] = {'prec' : 3}  ## min value of station
        dic[starter + "MAX"] = {'prec' : 3}  ## max value of station
        dic[starter + "MEAN"] = {'prec' : 3}  ## mean value of station
        dic[starter + "ID"] = {'type' : 'int'}  ## hex value of string
        dic[starter + "NAME"] = {'type' : 'str'}  ## string version of ID
        dicts.append(dic)
    dic = {}
    dic["NETWORK_PEAK"] = {'type' : 'int'}  ## max absolute value from all stations
    dicts.append(dic)
    dic = {}
    dic["NETWORK_STATION_NUM"] = {'type' : 'int'}  ## which station the max came from
    dicts.append(dic)
    dic = {}
    dic["NETWORK_STATION_NAME"] = {'type' : 'str'}  ## which station the max came from
    dicts.append(dic)
    dic = {}
    dic["NETWORK_AUX1"] = {'type' : 'int'}
    dicts.append(dic)
    dic = {}
    dic["NETWORK_AUX2"] = {'type' : 'int'}
    dicts.append(dic)
    dic = {}
    dic["NETWORK_AUX3"] = {'type' : 'int'}
    dicts.append(dic)
        
    #heartbeat to check the uptime of the picket fence code
    dic = {}
    dic["SERVER_START_GPS"] = {'type' : 'int'}
    dicts.append(dic)
    dic = {}
    dic["SERVER_GPS"] = {'type' : 'int'}
    dicts.append(dic)
    dic = {}
    dic["SERVER_START_STR"] = {'type': 'str'}
    dic["SERVER_UPTIME_SEC"] = {'type': 'int'}
    dic["SERVER_UPTIME_STR"] = {'type': 'str'}
    dic["LAST_PROCESS_GPS"] = {'type': 'int'}
    dic["LAST_PROCESS_STR"] = {'type': 'str'}
    dic["SINCE_LAST_PROCESS_SEC"] = {'type': 'int'}
    dic["SINCE_LAST_PROCESS_STR"] = {'type': 'str'}
    dic["SERVER_RUNNING"] = {'type': 'int'}
    dicts.append(dic)

    # IOC tracking channels
    dic = {}
    dic["IOC_START_GPS"] = {'type': 'int'}
    dic["IOC_GPS"] = {'type': 'int'}
    dic["IOC_START_STR"] = {'type': 'str'}
    dic["IOC_UPTIME_SEC"] = {'type': 'int'}
    dic["IOC_UPTIME_STR"] = {'type': 'str'}
    dic["IOC_HOSTNAME"] = {'type': 'str'}
    dic["IOC_PROCESS"] = {'type': 'str'}
    dicts.append(dic)

    return dicts



def ID_Creator(s):
    return int(''.join(str(format(ord(c), "x")) for c in s), 16)


def Reverse_ID(n):
    s = str(hex(n))
    itr = len(s)
    result = ""
    for i in range(2, itr, 2):
        result += chr(int(s[i:i+2], 16))
    return result



def main():
    server = SimpleServer()

    ## Set up EPICs variables names
    prefix = 'H1:SEI-USGS_'
    pvdbs = func(6)

    ## Initialize EPICs variables
    for pvdb in pvdbs:
        server.createPV(prefix, pvdb)

    driver = myDriver()
    driver.setParam("NETWORK_PEAK", -1)
    driver.setParam("NETWORK_STATION_NUM", -1)
    driver.setParam("NETWORK_AUX1", -1)
    driver.setParam("NETWORK_AUX2", -1)
    driver.setParam("NETWORK_AUX3", -1)
    driver.setParam("NETWORK_STATION_NAME", "")
    driver.setParam("SERVER_START_GPS", 0)
    driver.setParam("SERVER_GPS", 0)
    driver.setParam("SERVER_RUNNING", 0)

    global start_gps
    start_gps = gpsnow()
    driver.setParam("IOC_START_GPS", start_gps)
    driver.setParam("IOC_START_STR", gps_to_str(start_gps))
    driver.setParam("IOC_HOSTNAME", gethostname())

    # try to guess if we're running from systemd
    systemd_key = "INVOCATION_ID"
    if (systemd_key in os.environ) and (len(os.environ[systemd_key]) > 0):
        ioc_process = "systemd"
    else:
        ioc_process = "unknown"
    driver.setParam("IOC_PROCESS", ioc_process)
    
    # process CA transactions
    while True:
        server.process(0.1)


if __name__ == '__main__':
    main()
