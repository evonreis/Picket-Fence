# Picket-Fence
DESCRIPTION:

This program will display live data from USGS sites that feed data to IRIS.
___________


INSTALLATION:

First, start off with downloading conda which will make the rest of the installation much easier. It can be downloaded here https://conda.io/projects/conda/en/latest/user-guide/install/index.html and should only take a few minutes. Once conda is installed, we must download obspy, matplotlib, numpy, and scipy which can be downloaded with the commands `conda install -c conda-forge obspy`, `conda install -c conda-forge matplotlib`, `conda install -c conda-forge numpy`, and `conda install -c conda-forge scipy`. For LLO, the audio cue requires playsound to be downloaded, which in turn requires pip. To download pip with conda, use `conda install pip` and to use pip to download playsound, use `pip install playsound`.

Now that all dependencies are downloaded, to download the Picket-Fence files, open a terminal, enter the directory you would like the files to be located at, and finally use `git clone https://github.com/IAguilar007/Picket-Fence`. Whenever an update drops, we can use `git pull https://github.com/IAguilar007/Picket-Fence` should work.
___________

RUNNING THE PROGRAM:

To run, just open a terminal, go to the directory where you stored the file, and enter the command `python3 LLO_picket_fence.py` or `python3 LHO_picket_fence.py` depending on the file you downloaded. This will run the program with the optional parameters already chosen by me (the optional parameters I have set are good fits). When an earthquake that crosses our preset threshold occurs, the background for the plot of the station measuring the earthquake will turn a bright red. If a station is not being plotted, this is because it is currently down/ not feeding us data.

For any questions, you may email me at isaac007@stanford.edu and please make the subject involve Picket-Fence.

___________

OPTIONAL PARAMETERS (optional reading):

This program has many optional parameters and flags that can be changed:

Stations can be changed by -s or --seedlink_streams \[SEEDLINK_STREAMS\]

Server can be changed by --seedlink_server \[SEEDLINK_SERVER\]

The amount of time the plot displays can be changed with -b or --backtrace_time \[BACKTRACE_TIME\]

The threshold velocity to make a plot turn red can be changed with --threshold \[THRESHOLD\]

The full list of parameters is in the main function of L?O_picket_fence.py. Anything in a `parser.add_argument` can be changed with a flag and for formatting help, look at the `default` or at the `type`.

EXAMPLE OF RUNNING CODE WITH CHANGED PARAMETERS:

`python3 LLO_picket_fence.py -s "US_KVTX:10BHZ, IU_HKT:00BHZ, IU_TEIG:00BHZ, US_MIAR:00BHZ, US_LRAL:00BHZ, IU_DWPF:00BHZ" -b 30m --seedlink_server "rtserve.iris.washington.edu:18000" --update_time 2s --threshold 200 --lookback 360`.

_________

OPTIONAL AESTHETIC CHANGES (optional reading):

If you would like the minimum y-axis to be the threshold (default 500 nm/s), then you need to open the waveform.py file from obspy and make some slight modifications (this is purely for aesthetic reasons, the code will run as it should without this being done). I would recommend doing so solely because it allows you to view the signals relative to the threshold as oppose to relative to the largest signal being shown. The modifications will not corrupt obspy in any other files where it is a dependency.

If you would like the aesthetics mentioned above, do the following in the obspy waveform.py file:

Find where it says `self.__plot_set_y_ticks()` and change it to `self.__plot_set_y_ticks(**kwargs)`. This allows us to pass our variable to the function. Once that is done, go to the function `__plot_set_y_ticks(self, *args, **kwargs)` and near the end of the first if statement. Directly under `ylims[:, 1] += yrange_paddings[:] / 2`, we can add the following lines of code:

```
if "min_bound" in kwargs:
                value = kwargs["min_bound"]
                ylims[:, 0] = np.clip(ylims[:, 0], None, -2 * value)  ## changes made to fix min scaling
                ylims[:, 1] = np.clip(ylims[:, 1], 2 * value, None)   ## changes made to fix max scaling
```

and now running the program should have the minimum y-axis of negative threshold to threshold.
