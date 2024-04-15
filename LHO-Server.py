#!/usr/bin/env python

from gpstime import gpsnow, gpstime
from socket import gethostname
import os
import time
import threading
from ligo_softioc import SoftIOC


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


    return dicts

def main():
    ioc = SoftIOC(
        prefix='H3:SEI-USGS_',
        ioc_chan_prefix = "IOC_",
        separate_server = True,
    )

    ## Set up EPICs variables names
    prefix = 'H1:SEI-USGS_'
    pvdbs = func(6)

    ## Initialize EPICs variables
    for pvdb in pvdbs:
        ioc.add_channels(pvdb)

    ioc.finalize_channels()

    ioc.setParam("NETWORK_PEAK", -1)
    ioc.setParam("NETWORK_STATION_NUM", -1)
    ioc.setParam("NETWORK_AUX1", -1)
    ioc.setParam("NETWORK_AUX2", -1)
    ioc.setParam("NETWORK_AUX3", -1)
    ioc.setParam("NETWORK_STATION_NAME", "")

    ioc.start()


if __name__ == '__main__':
    main()
