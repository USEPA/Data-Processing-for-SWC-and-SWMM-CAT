# extreme_events

- NRCS temporal distribution tables
    - nrcs_tables/ contains all rainfall temporal distribution tables obtained by running WinTR-20

    - make_temporal_dist_file.py takes all files in nrcs_tables/ and writes to SCS24Hour.txt
    
    - If new distributions are added to WinTR-20, run WinTR-20 and save the new tables to nrcs_tables/
    
    - Then run make_temporal_dist_file.py and place the updated SCS24Hour.txt file in swcalculator-server/src/main/resources 
    
- Figures for user's manual
    - plot_rainfall_distribution.py makes a figure that shows the geographic distribution of the NRCS distributions
    
    - plot_dist.py makes a figure that shows the fraction of 24-hour extreme storm values against time
    
    - The scripts are set up to use the same color scheme but would need to be edited if additional rainfall distributions are added


- Comparing NOAA and NRCS temporal distributions (exploratory work)
    - for_plotting/ contains rainfall temporal distributions from NRCS and NOAA

    - plot_dist.py plots NRCS and NOAA temporal distributions
