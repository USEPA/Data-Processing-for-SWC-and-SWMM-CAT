# README

- The notebooks in this folder get data from every source for every station, including some stations that were not ultimately included in the SWC. This was initially done to get statistics but means that you are getting more data than you need. Then a postgres database is used to process the data (pg_processing.ipynb). This approach could be adapted to move forward.
- As an alternative, branch `upload-updated-temperature-data` has a notebook, new_data.ipynb, that was created to get one year of data and append it to the previous temperature data files without getting data from all sources or using postgres.
- If you want to use new_data.ipynb and output, they probably need to be QA'd before including in the SWC.
- The temperature files (used for calculating evaporation in the SWC) are in resources/temperature in this repository.
