#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 12 16:53:05 2022

@author: controls
"""

from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from Picket_fence_code_v2 import PicketFence, picketFenceArguments
import logging


def main():
    parser = ArgumentParser(prog='seedlink_plotter',
                            description='Plot a realtime seismogram of a station',
                            formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument('-v', '--verbose', default=False,
                        action="store_true", dest="verbose",
                        help='show verbose debugging output')
    parser.add_argument('--epics', default=False, action="store_true",
                        dest="epics", help="set EPICS variables in IOC")

    # parse the arguments
    runtimeArgs = parser.parse_args()

    #copy arguments over the default
    args=picketFenceArguments()
    args.verbose=runtimeArgs.verbose
    args.send_epics=runtimeArgs.epics
    
    if args.verbose:
        loglevel = logging.DEBUG
    else:
        loglevel = logging.CRITICAL
    logging.basicConfig(level=loglevel)

    pickets= {
        "BBB":{
            "Latitude":52.1847,
            "Longitude":-128.1133,
            "Channel":"CN_BBB:HHZ",
            "PreferredServer":"cwbpub.cr.usgs.gov:18000"
            },
        "HLID":{
            "Latitude":43.562,
            "Longitude":-114.414,
            "Channel":"US_HLID:00BHZ",
            "PreferredServer":"cwbpub.cr.usgs.gov:18000"
            },
        "NEW":{
            "Latitude":48.264,
            "Longitude":-117.123,
            "Channel":"US_NEW:00BHZ",
            "PreferredServer":"cwbpub.cr.usgs.gov:18000"
        },
#        "NLWA":{
#            "Latitude":47.392,
#            "Longitude":-123.869,
#            "Channel":"US_NLWA:00BHZ",
#            "PreferredServer":"cwbpub.cr.usgs.gov:18000"
#        },
        "OTR":{
            "Latitude":48.08632 ,
            "Longitude":-124.34518,
            "Channel":"UW_OTR:HHZ",
            "PreferredServer":"pnsndata.ess.washington.edu:18000"
        },
        "MSO":{
            "Latitude":46.829,
            "Longitude":-113.941,
            "Channel":"US_MSO:00BHZ",
            "PreferredServer":"cwbpub.cr.usgs.gov:18000"
        },
        "LAIR":{
            "Latitude":43.16148,
            "Longitude":-123.93143,
            "Channel":"UO_LAIR:HHZ",
            "PreferredServer":"pnsndata.ess.washington.edu:18000"
        }
    }

    ii=1
    for station in pickets.keys():  
        pickets[station]['index']=str(ii)
        ii+=1
        
    pf=PicketFence(picket_dict=pickets,myargs=args,epics_prefix="H3:SEI-USGS_")
    pf.run()

if __name__ == '__main__':
    main()
