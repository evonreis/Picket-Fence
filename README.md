# Picket-Fence
This program will display live data from USGS sites that feed data to IRIS.

This program has many optional parameters and flags that can be changed:

Stations can be changed by -s or --seedlink_streams \[SEEDLINK_STREAMS\]

Server can be changed by --seedlink_server \[SEEDLINK_SERVER\]

The amount of time the plot displays can be changed with -b or --backtrace_time \[BACKTRACE_TIME\]

The threshold velocity to make a plot turn red can be changed with --threshold \[THRESHOLD\]

The full list of parameters is in the main function of L?O_picket_fence.py. Anything in a `parser.add_argument` can be changed with a flag and for formatting help, look at the `default` or at the `type`.

An example is `python3 LLO_picket_fence.py -s "US_KVTX:10BHZ, IU_HKT:00BHZ, IU_TEIG:00BHZ, US_MIAR:00BHZ, US_LRAL:00BHZ, IU_DWPF:00BHZ" -b 30m --seedlink_server "rtserve.iris.washington.edu:18000" --update_time 2s --threshold 200 --lookback 360`.

All the parameters also have defaults which I have personally chosen as good fits so `python3 LLO_picket_fence.py` as it is, with none of the extra optional parameters set, will run with the default parameters I have chosen.

If you would like the minimum y-axis to be the threshold (default 500 nm/s), then you need to get the waveform.py file from obspy and make the following changes (this is purely for aesthetic reasons, the code will run as it should without this being done). I would recommend doing so solely because it forces each y-axis to have the same range so you can view the signals relative to each other.

If you would like the aesthetics mentioned above, do the following:

Find where it says `self.__plot_set_y_ticks()` and change it to `self.__plot_set_y_ticks(**kwargs)`. This allows us to pass our variable to the function. Once that is done, go to the function `__plot_set_y_ticks(self, *args, **kwargs)` and near the end of the first if statement. after `ylims[:, 1] += yrange_paddings[:] / 2`, we can add the following lines of code:

```
if "min_bound" in kwargs:
                value = kwargs["min_bound"]
                ylims[:, 0] = np.clip(ylims[:, 0], None, -2 * value)  ## changes made to fix min scaling
                ylims[:, 1] = np.clip(ylims[:, 1], 2 * value, None)   ## changes made to fix max scaling
```

and now running the program should have the minimum y-axis of threshold to negative threshold.

When an earthquake that crosses our preset threshold occurs, the background for the plot of the station measuring the earthquake will turn a bright red. Only stations that are currently feeding us data are shown, otherwise the station will not be displayed. 

For any questions, you may email me at isaac007@stanford.edu and please make the subject involve Picket-Fence.
