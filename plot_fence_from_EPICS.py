#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct  6 13:43:42 2023

@author: controls
"""
#This function creates a picketMap instance by looking at the EPICS Variables. Therefore, it can plot the current state of the picket fence as seen from the EPICS side.

#TODO: Dynamically access all of the picket fence EPICS information. Right now this is NOT the case.it is all hardcoded

from picketMapTools import picketMap
from Picket_fence_code_v2 import load_pickets
from epics import caget
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter


#format the station in the format that the picketMap function is able to plot.
def create_station_dict(name,lon,lat):
    station_dict=dict()
    station_dict[name]=dict()
    station_dict[name]["Longitude"]=lon
    station_dict[name]["Latitude"]=lat
    return station_dict

def main():
    parser = ArgumentParser(prog='Picket_Map_from_EPICS',
                            description='Plot the map of active pickets from EPICS',
                            formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        '--ifo_name', type=str,
                        help='LHO or LLO', required=True)
    parser.add_argument(
        '--longitude', type=float,
                        help='longitude coordinate for the ifo', required=True)
    parser.add_argument(
        '--latitude', type=float,
                        help='latitude coordinate for the ifo', required=True)
    parser.add_argument(
        '--EPICS_prefix', type=str,
                        help='epics prefix for the picket fence, like "H1:SEI-USGS_"', required=True)

    # parse the arguments
    runtimeArgs = parser.parse_args()
    
    epics_prefix=runtimeArgs.EPICS_prefix
    
    observatory=create_station_dict(runtimeArgs.ifo_name,runtimeArgs.longitude,runtimeArgs.latitude)
    
    picket_list=[]
    for i in range(6): #TODO: make it realize how many EPICS pickets we have active
        picket_list.append(caget(epics_prefix+f"STATION_0{i+1}_NAME"))
        
    picket_dict=load_pickets(picket_list)
    picket_map=picketMap(picket_dict=picket_dict,central_station=observatory)
    picket_map.generate_plot()
if __name__ == '__main__':
    main()