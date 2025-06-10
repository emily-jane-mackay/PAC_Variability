# PAC_Variability

# Python
#### 1. preprocessing.py
Loads raw queried data from MPOG, merges, cleans, and preprocesses data and defines cohort. 

# Stata
#### 2. characteristics.do
Formats data for characteristics table comparing PAC vs no PAC. 

#### 3. GLMM.do
Runs multiple GLMM analyses on processed dataset and exports the aggregated results. 

# Python
#### 4. pac_by_surgery.py
Uses aggregated data to generate data visualization for PAC and no PAC use by surgical procedure. 

#### 5. pac_histogram_kdensity.py
Uses aggregated data to generate data visualization for PAC use by anesthesiologist and hospital (histograms with kdensities overlay). 

