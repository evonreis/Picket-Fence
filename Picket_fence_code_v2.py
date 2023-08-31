#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 30 11:36:15 2023

@author: controls
"""
### V2 NOTES ###
# This is version two of the legacy picket fence code for LIGO with the objective of early warning for earthquakes at the observatories.
# See G2001601 and G2201345 for presentations on the matter. A short white paper outlining the performance can be found at T2300281 ###
# v2 Is written by Edgard L. Bonilla [ELB] based on the modifications made by Isaac Aguilar over the original code by Grace Johns, Anne Baer and Ryan Fisher.
# v2 is the first step in decoupling the connection and plotting aspects of the picket fence. We want to simplify modifications to the code by creating a single
# piece of code that can be called with different configurations.


### CODE EXPLANATION ###
#The code consists of three main classes: 
#-- seedlinkUpdater:
    # This class establishes a connection to a seedlink server, it is used to collect data from a list of public and private servers of seismic data.
    # The class is just a subclass of the ObsPy SLClient class: https://docs.obspy.org/packages/obspy.clients.seedlink.html
    # the methods run() and packetHandler() determine how the data is collected.
#-- seedlinkPlotter:
    # This class is based on the code from https://github.com/sbonaime/seedlink_plotter 
    # its main function is to update the display of data. It uses Tkinter to make a GUI that should plot dynamically.
#-- filteredStream:
    # This class is a subclass of ObsPy's stream: https://docs.obspy.org/packages/autogen/obspy.core.stream.Stream.html
    # The objective of the class is to handle all of the data processing of the raw stream that is collected by an instance of the seedlinkUpdater

#[ELB] 08/30/2023    


### IMPORTS ###
import warnings
warnings.filterwarnings("ignore", "Badly*")  # suppresses warning calls from lsim filter function

try:
    # Py3
    import tkinter
except ImportError:
    # Py2
    import Tkinter as tkinter
    
import matplotlib
# Set the backend for matplotlib.
matplotlib.use("TkAgg")
matplotlib.rc('figure.subplot', hspace=0)
matplotlib.rc('font', family="monospace")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.ticker import MaxNLocator
from matplotlib.patheffects import withStroke
from matplotlib.dates import date2num
import matplotlib.pyplot as plt


from obspy import Stream, Trace
from obspy.core import UTCDateTime
from obspy.core.event import Catalog
from obspy.core.util import MATPLOTLIB_VERSION
from obspy.clients.seedlink.slpacket import SLPacket
from obspy.clients.seedlink import SLClient
from obspy.clients.fdsn import Client


import threading
import os
from time import sleep
from datetime import datetime
import subprocess
import sys
from scipy import signal

import logging
import numpy as np
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

class SeedlinkUpdater(SLClient):
    
    def __init__(self, stream, myargs=None, lock=None):
        # loglevel NOTSET delegates messages to parent logger
        super(SeedlinkUpdater, self).__init__(loglevel="NOTSET")
        self.stream = stream
        self.lock = lock
        self.args = myargs

    def run(self, packet_handler=None):
        """
        Start this SLClient.

        :type packet_handler: func
        :param packet_handler: Custom packet handler funtion to override
            `self.packet_handler` for this seedlink request. The function will
            be repeatedly called with two arguments: the current packet counter
            (`int`) and the currently served seedlink packet
            (:class:`~obspy.clients.seedlink.SLPacket`). The function should
            return `True` to abort the request or `False` to continue the
            request.
        """
        global stop_flag
        stop_flag = False
        if packet_handler is None:
            packet_handler = self.packet_handler
        if self.infolevel is not None:
            self.slconn.request_info(self.infolevel)
        # Loop with the connection manager
        count = 1
        slpack = self.slconn.collect()
        while slpack is not None:
            if (slpack == SLPacket.SLTERMINATE):
                break
            try:
                # do something with packet
                terminate = packet_handler(count, slpack)
                if terminate:
                    break
            except SeedLinkException as sle:
                print(self.__class__.__name__ + ": " + sle.value)
            if count >= sys.maxsize:
                count = 1
                print("DEBUG INFO: " + self.__class__.__name__ + ":", end=' ')
                print("Packet count reset to 1")
            else:
                count += 1
            slpack = self.slconn.collect()
            if stop_flag:
                break

        # Close the SeedLinkConnection
        self.slconn.close()

    def packetHandler(self, count, slpack):
        """
        Processes each packet received from the SeedLinkConnection.
        :type count: int
        :param count:  Packet counter.
        :type slpack: :class:`~obspy.seedlink.SLPacket`
        :param slpack: packet to process.
        :return: Boolean true if connection to SeedLink server should be
            closed and session terminated, false otherwise.
        """

        # check if not a complete packet
        if slpack is None or (slpack == SLPacket.SLNOPACKET) or \
                (slpack == SLPacket.SLERROR):
            return False

        # get basic packet info
        type = slpack.get_type()

        # process INFO packets here
        if type == SLPacket.TYPE_SLINF:
            return False
        if type == SLPacket.TYPE_SLINFT:
            logging.info("Complete INFO:" + self.slconn.getInfoString())
            return self.infolevel is not None

        # process packet data
        trace = slpack.get_trace()
        if trace is None:
            logging.info(
                self.__class__.__name__ + ": blockette contains no trace")
            return False

        # new samples add to the main stream which is then trimmed
        with self.lock:
            self.stream += trace
            self.stream.merge(-1)
            self.stream.trim(starttime=UTCDateTime()-3600) #TODO STREAMLINE THIS
            for trace in self.stream:
                trace.stats.processing = []
        return False

    def getTraceIDs(self):
        """
        Return a list of SEED style Trace IDs that the SLClient is trying to
        fetch data for.
        """
        ids = []
        streams = self.slconn.get_streams()
        for stream in streams:
            net = stream.net
            sta = stream.station
            selectors = stream.get_selectors()
            for selector in selectors:
                if len(selector) == 3:
                    loc = ""
                else:
                    loc = selector[:2]
                cha = selector[-3:]
                ids.append(".".join((net, sta, loc, cha)))
        ids.sort()
        return ids

class filteredStream(Stream):
    
    def __init__(self, rawStream, myargs=None):
        super(filteredStream, self).__init__()
        
        #self.lock=lock
        self.args=myargs
        
        #initialize the internal traces
        self.rawStream = rawStream
        self.traces=rawStream.copy().traces
        
        #Define Brian's Lowpass filter that doesn't distort EQs [SEI aLog 2264]
        num =[ 0, 0.4726, 0.8728, 20.9151, 16.5637, 138.7922, 43.0012, 170.2783, 19.9420, 52.9641 ,0]
        den =[1.0000, 9.8557, 58.9535, 206.3141, 468.0879, 754.8555, 591.8468, 463.7391, 184.1213, 70.7469, 6.7789]
        self.filter=(num,den)
        
        #Internal states for Brian's filter
        self.customMetadata=dict()
        for trace in self.traces:
            self.customMetadata[trace.id]=dict()
            self.FirstLowpass(trace)
        
    def HanningWindow(self,trace):
        trace_len = len(trace.data)
        window_len = trace_len // 2
        window_len -= (window_len % 2) # Make sure window length is an even number
        if trace_len > window_len:
            hw = np.hanning(window_len) # Hanning window size of window length
            hw = np.split(hw, 2)
            hw = hw[0]
            hw_num = trace_len - window_len / 2 # Only first half of hanning window, don't want
            # the right side of the data to be impacted (only care about the most recent n seconds of data)
            hw_num = int(hw_num)
            new = np.tile(1, hw_num) # Make everything after the hanning window one, don't want most recent n seconds to be impacted
            hwp = np.append(hw, new)
            trace.data = trace.data * hwp # Apply window
            
    def FirstLowpass(self,trace):
            self.HanningWindow(trace)
            dt = trace.stats.delta
            T=np.arange(0.0, len(trace.data))
            T *= dt
            tout, yout, xout =signal.lsim(self.filter, trace.data, T, X0=None)
            trace.data = yout
            trace.trim(starttime=trace.stats.starttime+180) #TODO: Change this to actually be useful
            self.customMetadata[trace.id]['filterState']=xout[-1]
            self.customMetadata[trace.id]['endtime']=trace.stats.endtime
    
    def CollectAndAnalyze(self):
        #with self.lock:
        for trace in self.rawStream.traces:
            if trace.id in self.customMetadata.keys():
                oldEndtime=self.customMetadata[trace.id]['endtime']
                
                #Trim traces to isolate the new data
                if (trace.stats.endtime-oldEndtime)>0:
                    dt = trace.stats.delta
                    newTrace=trace.slice(starttime=oldEndtime+dt)
                    trace_len=len(newTrace.data)

                    #filter the new data and trim
                    xin=self.customMetadata[newTrace.id]['filterState'];
                    T=np.arange(0.0, trace_len)
                    T *= dt
                    tout, yout, xout =signal.lsim(self.filter, newTrace.data, T, X0=xin)
                    newTrace.data = yout
                    self.customMetadata[newTrace.id]['filterState']=xout[-1]
                    self.customMetadata[newTrace.id]['endtime']=newTrace.stats.endtime
                    self.append(newTrace)
                    
            else:#TODO: What happens if a station comes in and out?
                newTrace=trace.copy()
                self.customMetadata[trace.id]=dict()
                self.FirstLowpass(newTrace)    
                self.append(newTrace)
                
        #Merge and clean the trace information
        self.merge(-1)
        self.updateMetadata()
        self.trim(UTCDateTime()-2*self.args.backtrace_time) #TODO: make this trim not arbitrary
        for trace in self.traces:
            trace.stats.processing = [] 
            
    def updateMetadata(self):
        #Grab statistics for the traces in the last 'lookback' seconds
        for trace in self.traces:
            dummyTrace=trace.slice(starttime=UTCDateTime()-self.args.lookback)
            if len(dummyTrace.data)!=0:
                self.customMetadata[trace.id]['MAX']=np.max(dummyTrace.data)
                self.customMetadata[trace.id]['MIN']=np.min(dummyTrace.data)
                self.customMetadata[trace.id]['MEAN']=np.mean(dummyTrace.data)
