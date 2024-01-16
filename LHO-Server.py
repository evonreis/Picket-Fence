#!/usr/bin/env python3

import subprocess
import sys

def main():
    """
    THIS PROGRAM JUST CALLS THE EPICS SERVER V2 AND IT IS STRUCTURED THIS WAY FOR BACKWARDS COMPATIBILITY
    """
    
    prefix = 'H1:SEI-USGS_'
    path= "Picket_fence_EPICS_server_v2.py"
    subprocess.Popen(['python3', path, prefix])
    sys.exit(0)


if __name__ == '__main__':
    main()
