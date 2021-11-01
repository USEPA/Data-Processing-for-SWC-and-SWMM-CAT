# bls_for_swc

1. Register for the BLS API [here](https://data.bls.gov/registrationEngine/)
2. Clone repository `git clone https://github.com/barrc/bls_for_swc`
3. Change directory to bls_for_swc 
4. Create src/passwords.py with 

```
BLS_API_KEY = "your_BLS_key"
```

5. Create conda environment `conda env create --file bls.yml` and activate `conda activate bls`
6. Change year (#TODO make command line argument)
7. Run `python src/bls_for_swc.py` and note national index value
8. Copy costRegionalizationCache.txt to swcalculator_home/costData
9. Change national index in CostRegionalizationServiceImpl.java
10. Change year in legends Front End
