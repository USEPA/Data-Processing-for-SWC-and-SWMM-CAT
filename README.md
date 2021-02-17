# extreme_events

- NRCS temporal distribution tables
    - nrcs_tables/ contains all rainfall temporal distribution tables obtained by running WinTR-20

    - make_temporal_dist_file.py takes all files in nrcs_tables/ and writes to a temporal_dist_file.txt

- Comparing NOAA and NRCS temporal distribtions
    - for_plotting/ contains rainfall temporal distributions from NRCS and NOAA

    - plot_dist.py plots NRCS and NOAA temporal distributions
