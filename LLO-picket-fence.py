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
        "LRAL":{
            "Latitude":33.0399,
            "Longitude":-86.9978,
            "Channel":"US_LRAL:00BHZ",
            "PreferredServer":"cwbpub.cr.usgs.gov:18000"
            },
        "MIAR":{
            "Latitude":34.5454,
            "Longitude":-93.5765,
            "Channel":"US_MIAR:00BHZ",
            "PreferredServer":"cwbpub.cr.usgs.gov:18000"
            },
        "TEIG":{
            "Latitude":20.226,
            "Longitude":-88.276,
            "Channel":"IU_TEIG:00BHZ",
            "PreferredServer":"cwbpub.cr.usgs.gov:18000"
        },
        "HKT":{
            "Latitude":29.965,
            "Longitude":-95.838,
            "Channel":"IU_HKT:00BHZ",
            "PreferredServer":"cwbpub.cr.usgs.gov:18000"
        },
        "DWPF":{
            "Latitude":28.11,
            "Longitude":-81.433,
            "Channel":"IU_DWPF:00BHZ",
            "PreferredServer":"cwbpub.cr.usgs.gov:18000"
        },
        
        # "735B":{
        #     "Latitude":28.8553,
        #     "Longitude":-97.8082,
        #     "Channel":"N4_735B:00HHZ",
        #     "PreferredServer":"cwbpub.cr.usgs.gov:18000"
        # }
        "KVTX":{
            "Latitude":27.546,
            "Longitude":-97.893,
            "Channel":"US_KVTX:00BHZ",
            "PreferredServer":"cwbpub.cr.usgs.gov:18000"
        }
    }

    ii=1
    for station in pickets.keys():  
        pickets[station]['index']=str(ii)
        ii+=1
        
    pf=PicketFence(picket_dict=pickets,myargs=args,epics_prefix="L1:SEI-USGS_")
    pf.run()

if __name__ == '__main__':
    main()
