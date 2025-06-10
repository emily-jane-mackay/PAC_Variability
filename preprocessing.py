# -*- coding: utf-8 -*-
"""
Created on Fri Dec 15 15:51:06 2023

@author: macemil
"""

# %%
import os
import re
import pandas as pd
import numpy as np

from sklearn.linear_model import LinearRegression
from sklearn.impute import SimpleImputer
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer

import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.formula.api import glm

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.cbook as cbook
import matplotlib.colors as mcolors
import matplotlib.patches as mpatch
import matplotlib as mpl
from matplotlib.colors import LinearSegmentedColormap, ListedColormap

import seaborn as sns
import seaborn.objects as so

dirname=os.path.dirname(__file__) #note: this errors if run individually but not if entire .py code is run as block
pd.set_option('display.max_columns', 200)
pd.set_option('display.max_rows', 200)

#%%
# manual creation of dataframe
df = pd.DataFrame({"a": [0, 1], "b": [1, 1]})
# note - double click on data viewer to view it
print(df)

#%%
case=pd.read_csv(
    filepath_or_buffer=os.path.join(dirname, "data", "PCRC_0094_CaseInfo_120723.csv.gz"),
        dtype=str,
        index_col=False
)

#%% 
# look at data 
c = case.head()
c = case.head(1000)
case.dtypes
case.count()

#%% look at exposures
case['TEE_Probe_Placed'].value_counts(dropna=False)
case['TEE_Probe_Removed'].value_counts(dropna=False)
case['TEE_Exam_Note'].value_counts(dropna=False)
case['TEE_Detailed_Obs'].value_counts(dropna=False)
case['Intraop_PAC'].value_counts(dropna=False)
case['Intraop_PAC_CVC'].value_counts(dropna=False)
case['Intraop_CVC'].value_counts(dropna=False)
case['Surg_CPT_93325'].value_counts(dropna=False)
case['Surg_CPT_93321'].value_counts(dropna=False)
case['Surg_CPT_93320'].value_counts(dropna=False)
case['Surg_CPT_93318'].value_counts(dropna=False)
case['Surg_CPT_93317'].value_counts(dropna=False)
case['Surg_CPT_93316'].value_counts(dropna=False)
case['Surg_CPT_93315'].value_counts(dropna=False)
case['Surg_CPT_93314'].value_counts(dropna=False)
case['Surg_CPT_93313'].value_counts(dropna=False)
case['Surg_CPT_93312'].value_counts(dropna=False)

#%%
# create TEE exposure column based on multiple conditions (both MPOG note & CPT codes)
case['TEE_intraop'] = np.where((case['TEE_Probe_Placed'] == 'True') | (case['TEE_Probe_Removed'] == 'True') | (case['Surg_CPT_93325'] == 'True') | (case['Surg_CPT_93321'] == 'True') | (case['Surg_CPT_93320'] == 'True') | (case['Surg_CPT_93318'] == 'True') | (case['Surg_CPT_93317'] == 'True') | (case['Surg_CPT_93316'] == 'True') | (case['Surg_CPT_93315'] == 'True') | (case['Surg_CPT_93314'] == 'True') |  (case['Surg_CPT_93313'] == 'True') | (case['Surg_CPT_93312'] == 'True'), 1, 0)   
case['TEE_intraop'].value_counts(dropna=False)

#%%
# look at PAC & CVC columns
case['Intraop_PAC'].value_counts(dropna=False)
case['Intraop_PAC_CVC'].value_counts(dropna=False)
case['Intraop_CVC'].value_counts(dropna=False)

#%%
# continuous variables must be converted to numerical
# columns with counts <175372 & >166603 can be simple imputation (i.e. missing <0.05)
# columns with counts <175372 & <166603 require multiple imputation (i.e. missing >0.05)
case['Age_In_Years'] = pd.to_numeric(case['Age_In_Years'])
case['Age_In_Years'].describe() # no missing data 
case['Height_cm'] = pd.to_numeric(case['Height_cm'])
case['Height_cm'].describe() # simple impute
case['Weight_kg'] = pd.to_numeric(case['Weight_kg'])
case['Weight_kg'].describe() # simple impute
case['BMI'] = pd.to_numeric(case['BMI'])
case['BMI'].describe() # technically multiple imputation by 0.05 rule (calculates to 0.0574) but executive decision to simple impute based on clinical inference
case['Cardiopulmonary_Bypass_Duration'] = pd.to_numeric(case['Cardiopulmonary_Bypass_Duration'])
case['Cardiopulmonary_Bypass_Duration'].describe() # CPB time not appropriate for multiple imputation
case['Anesthesia_Duration'] = pd.to_numeric(case['Anesthesia_Duration'])
case['Anesthesia_Duration'].describe() # no missing data 

case['Patient_In_Room_Duration'] = pd.to_numeric(case['Patient_In_Room_Duration'])
case['Patient_In_Room_Duration'].describe() # multiple imputation if needed but likely colinear with anesthesia duration 

# lab data needs to be looked at after convering -999 to nan
case['Preop_Albumin'] = pd.to_numeric(case['Preop_Albumin'])
case['Preop_Albumin'].describe()
case['Preop_Alk_Phosphatase'] = pd.to_numeric(case['Preop_Alk_Phosphatase'])
case['Preop_ALT'] = pd.to_numeric(case['Preop_ALT'])
case['Preop_Arterial_pH'] = pd.to_numeric(case['Preop_Arterial_pH'])
case['Preop_AST'] = pd.to_numeric(case['Preop_AST'])
case['Preop_BUN'] = pd.to_numeric(case['Preop_BUN'])
case['Preop_Calcium_Ionized'] = pd.to_numeric(case['Preop_Calcium_Ionized'])
case['Preop_Calcium_Total'] = pd.to_numeric(case['Preop_Calcium_Total'])
case['Preop_CO2_Arterial'] = pd.to_numeric(case['Preop_CO2_Arterial'])
case['Preop_EGFR_60_Day_Most_Recent'] = pd.to_numeric(case['Preop_EGFR_60_Day_Most_Recent'])
case['Preop_HCO3'] = pd.to_numeric(case['Preop_HCO3'])
case['Preop_Glucose'] = pd.to_numeric(case['Preop_Glucose'])
case['Preop_Hematocrit'] = pd.to_numeric(case['Preop_Hematocrit'])
case['Preop_Hemoglobin'] = pd.to_numeric(case['Preop_Hemoglobin'])
case['Preop_Hgb_A1c'] = pd.to_numeric(case['Preop_Hgb_A1c'])
case['Preop_INR'] = pd.to_numeric(case['Preop_INR'])
case['Preop_Lactate'] = pd.to_numeric(case['Preop_Lactate'])
case['Preop_Platelets'] = pd.to_numeric(case['Preop_Platelets'])
case['Preop_Potassium'] = pd.to_numeric(case['Preop_Potassium'])
case['Preop_PT'] = pd.to_numeric(case['Preop_PT'])
case['Preop_PTT'] = pd.to_numeric(case['Preop_PTT'])
case['Preop_Sodium'] = pd.to_numeric(case['Preop_Sodium'])
case['Preop_Total_Bilirubin'] = pd.to_numeric(case['Preop_Total_Bilirubin'])
case['Preop_Troponin_Highest'] = pd.to_numeric(case['Preop_Troponin_Highest'])
case['Preop_WBC'] = pd.to_numeric(case['Preop_WBC'])
case['Intraop_PRBC_Volume_In_Units'] = pd.to_numeric(case['Intraop_PRBC_Volume_In_Units'])
case['Intraop_PRBC_Volume_In_MLs'] = pd.to_numeric(case['Intraop_PRBC_Volume_In_MLs'])
case['Intraop_FFP_Volume_In_Units'] = pd.to_numeric(case['Intraop_FFP_Volume_In_Units'])
case['Intraop_FFP_Volume_In_MLs'] = pd.to_numeric(case['Intraop_FFP_Volume_In_MLs'])
case['Intraop_Platelets_Volume_In_Units'] = pd.to_numeric(case['Intraop_Platelets_Volume_In_Units'])
case['Intraop_Platelets_Volume_In_MLs'] = pd.to_numeric(case['Intraop_Platelets_Volume_In_MLs'])
case['Intraop_Cryo_Volume_In_Units'] = pd.to_numeric(case['Intraop_Cryo_Volume_In_Units'])
case['Intraop_Cryo_Volume_In_MLs'] = pd.to_numeric(case['Intraop_Cryo_Volume_In_MLs'])
case['Intraop_Crystalloids'] = pd.to_numeric(case['Intraop_Crystalloids'])
case['Intraop_Urine_Output'] = pd.to_numeric(case['Intraop_Urine_Output'])

#%%
# check
c = case.head(2000)

#%%
# ideally, need to figure out how to convert all negative numbers (primarily -999 & -998 but some other random negatives) to nan in numeric columns in the case datafram that contains both string and numeric columns
# solution if all columns in dataframe are numeric
# numeric = case.select_dtypes(include=np.number) # create numeric dataframe
# numeric[numeric < 0] = 0 # replace all negative values with zero in numeric dataframe
# numeric = numeric.replace({0: np.nan})

#%%
# current colution if both string and numeric columns are in the dataframe
case = case.replace({-999: np.nan})
case = case.replace({-998: np.nan}) 

#%%
# look at all the lab, product, crystalloid, and urine data 
case['Preop_Albumin'].describe() # multiple imputation
case['Preop_Alk_Phosphatase'].describe() # multiple imputation
case['Preop_ALT'].describe() # multiple imputation
case['Preop_Arterial_pH'].describe() # not appropriate for imputation -- missing too much data 
case['Preop_AST'].describe() # multiple imputation
case['Preop_BUN'].describe() # multiple imputation
case['Preop_Calcium_Ionized'].describe() # not appropriate for imputation -- missing too much data 
case['Preop_Calcium_Total'].describe() # multiple imputation
case['Preop_CO2_Arterial'].describe() # not appropriate for imputation -- missing too much data 
case['Preop_EGFR_60_Day_Most_Recent'].describe() # not appropriate for imputation -- clinical inference (use Cr | BUN instead)
case['Preop_HCO3'].describe() # not appropriate for imputation -- missing too much data 
case['Preop_Glucose'].describe() # multiple imputation
case['Preop_Hematocrit'].describe() # multiple imputation
case['Preop_Hemoglobin'].describe() # multiple imputation
case['Preop_Hgb_A1c'].describe() # multiple imputation
case['Preop_INR'].describe() # multiple imputation
case['Preop_Lactate'].describe() # not appropriate for imputation -- missing too much data 

case['Preop_Platelets'].describe() # multiple imputation
case['Preop_Potassium'].describe() # multiple imputation
case['Preop_PT'].describe() # multiple imputation
case['Preop_PTT'].describe() # multiple imputation
case['Preop_Sodium'].describe() # multiple imputation
case['Preop_Total_Bilirubin'].describe() # multiple imputation
case['Preop_Troponin_Highest'].describe() # ? 
case['Preop_WBC'].describe() # multiple imputation
case['Intraop_PRBC_Volume_In_Units'].describe() # simple imputation  
case['Intraop_PRBC_Volume_In_MLs'].describe() # simple imputation
case['Intraop_FFP_Volume_In_Units'].describe() # simple imputation  
case['Intraop_FFP_Volume_In_MLs'].describe() # simple imputation

case['Intraop_Platelets_Volume_In_Units'].describe() # simple imputation
case['Intraop_Platelets_Volume_In_MLs'].describe() # simple imputation
case['Intraop_Cryo_Volume_In_Units'].describe() # simple imputation
case['Intraop_Cryo_Volume_In_MLs'].describe() # simple imputation
case['Intraop_Crystalloids'].describe() # simple imputation
case['Intraop_Urine_Output'].describe() # not appropriate for imputation -- clinical inference 

#%% 
# data check
case.count()
c = case.head(1000)

#%%
# categorical data - count missing 
tee_probe_placed_nan_count = case['TEE_Probe_Placed'].isna().sum()
print(tee_probe_placed_nan_count)
62263/175372
# continuous data - count missing 
cpb_nan_count = case['Cardiopulmonary_Bypass_Duration'].isna().sum()
print(cpb_nan_count)
23110/175372


#%%
#impute missing using fit_transform sklearn
# imputer sklearn
imputer = SimpleImputer(missing_values=np.nan, strategy='mean')

#%% continuous data for simple imputation
case['Age_In_Years'].describe()

case['Height_cm'].describe()
imputer.fit(case['Height_cm'].values.reshape(-1, 1))
case['Height_cm'] = imputer.transform(case['Height_cm'].values.reshape(-1, 1))
case['Height_cm'].describe()

case['Weight_kg'].describe()
imputer.fit(case['Weight_kg'].values.reshape(-1, 1))
case['Weight_kg'] = imputer.transform(case['Weight_kg'].values.reshape(-1, 1))
case['Weight_kg'].describe()

case['BMI'].describe()
imputer.fit(case['BMI'].values.reshape(-1, 1))
case['BMI'] = imputer.transform(case['BMI'].values.reshape(-1, 1))
case['BMI'].describe()

case['Anesthesia_Duration'].describe()

# note: in future work using intraop products -- will need to flag and drop the obs with negative values
case['Intraop_PRBC_Volume_In_Units'].describe()
imputer.fit(case['Intraop_PRBC_Volume_In_Units'].values.reshape(-1, 1))
case['Intraop_PRBC_Volume_In_Units'] = imputer.transform(case['Intraop_PRBC_Volume_In_Units'].values.reshape(-1, 1))
case['Intraop_PRBC_Volume_In_Units'].describe()

# note: in future work using intraop products -- will need to flag and drop the obs with negative values
case['Intraop_PRBC_Volume_In_MLs'].describe()
imputer.fit(case['Intraop_PRBC_Volume_In_MLs'].values.reshape(-1, 1))
case['Intraop_PRBC_Volume_In_MLs'] = imputer.transform(case['Intraop_PRBC_Volume_In_MLs'].values.reshape(-1, 1))
case['Intraop_PRBC_Volume_In_MLs'].describe() 
# check on negative values 
df_reds = case[['Intraop_PRBC_Volume_In_Units', 'Intraop_PRBC_Volume_In_MLs']]

case['Intraop_FFP_Volume_In_Units'].describe()
imputer.fit(case['Intraop_FFP_Volume_In_Units'].values.reshape(-1, 1))
case['Intraop_FFP_Volume_In_Units'] = imputer.transform(case['Intraop_FFP_Volume_In_Units'].values.reshape(-1, 1))
case['Intraop_FFP_Volume_In_Units'].describe()

case['Intraop_FFP_Volume_In_MLs'].describe()
imputer.fit(case['Intraop_FFP_Volume_In_MLs'].values.reshape(-1, 1))
case['Intraop_FFP_Volume_In_MLs'] = imputer.transform(case['Intraop_FFP_Volume_In_MLs'].values.reshape(-1, 1))
case['Intraop_FFP_Volume_In_MLs'].describe()

case['Intraop_Platelets_Volume_In_Units'].describe()
imputer.fit(case['Intraop_Platelets_Volume_In_Units'].values.reshape(-1, 1))
case['Intraop_Platelets_Volume_In_Units'] = imputer.transform(case['Intraop_Platelets_Volume_In_Units'].values.reshape(-1, 1))
case['Intraop_Platelets_Volume_In_Units'].describe()

case['Intraop_Platelets_Volume_In_MLs'].describe()
imputer.fit(case['Intraop_Platelets_Volume_In_MLs'].values.reshape(-1, 1))
case['Intraop_Platelets_Volume_In_MLs'] = imputer.transform(case['Intraop_Platelets_Volume_In_MLs'].values.reshape(-1, 1))
case['Intraop_Platelets_Volume_In_MLs'].describe()

case['Intraop_Cryo_Volume_In_Units'].describe()
imputer.fit(case['Intraop_Cryo_Volume_In_Units'].values.reshape(-1, 1))
case['Intraop_Cryo_Volume_In_Units'] = imputer.transform(case['Intraop_Cryo_Volume_In_Units'].values.reshape(-1, 1))
case['Intraop_Cryo_Volume_In_Units'].describe()

case['Intraop_Cryo_Volume_In_MLs'].describe()
imputer.fit(case['Intraop_Cryo_Volume_In_MLs'].values.reshape(-1, 1))
case['Intraop_Cryo_Volume_In_MLs'] = imputer.transform(case['Intraop_Cryo_Volume_In_MLs'].values.reshape(-1, 1))
case['Intraop_Cryo_Volume_In_MLs'].describe()

# note: in future work using intraop crystalloid -- will need to flag and drop the obs with negative values
case['Intraop_Crystalloids'].describe()
imputer.fit(case['Intraop_Crystalloids'].values.reshape(-1, 1))
case['Intraop_Crystalloids'] = imputer.transform(case['Intraop_Crystalloids'].values.reshape(-1, 1))
case['Intraop_Crystalloids'].describe()
# check negative values 
df_crystal = case[['Intraop_Crystalloids']]

#%% multiple imputation 
imputer_multi = IterativeImputer(random_state=100, max_iter=10)

# dataframe with the numeric columns for multiple imputation
df_multi = case.loc[:, ["Preop_Albumin", "Preop_Alk_Phosphatase", "Preop_ALT", "Preop_AST", "Preop_BUN", "Preop_Calcium_Total", "Preop_Glucose", "Preop_Hematocrit", "Preop_Hemoglobin", "Preop_Hgb_A1c", "Preop_INR", "Preop_Platelets", "Preop_Potassium", "Preop_PT", "Preop_PTT", "Preop_Sodium", "Preop_Total_Bilirubin", "Preop_WBC"]]
df_multi.head()

# fit on the dataframe
imputer_multi.fit(df_multi)

# predict missing values 
df_imputed = imputer_multi.transform(df_multi)
df_imputed[:10]

# replace with imputed values 
df_multi.loc[:, ["Preop_Albumin", "Preop_Alk_Phosphatase", "Preop_ALT", "Preop_AST", "Preop_BUN", "Preop_Calcium_Total", "Preop_Glucose", "Preop_Hematocrit", "Preop_Hemoglobin", "Preop_Hgb_A1c", "Preop_INR", "Preop_Platelets", "Preop_Potassium", "Preop_PT", "Preop_PTT", "Preop_Sodium", "Preop_Total_Bilirubin", "Preop_WBC"]] = df_imputed
df_multi.head(10)

# add sufix to dataframe with imputed data
df_multi_suff = df_multi.add_suffix('_imp')

#%% merge back into original dataframe using concat -- possible if data from both dataframes are in same order

# check order 
x = case[['Preop_Albumin']]
y = df_multi_suff[['Preop_Albumin_imp']]

# concat two dataframes after confirming order is correct
temp = pd.concat([case, df_multi_suff], axis=1)

#%%
# overwrite case dataframe with concatenated data to get the columns with multiple imputation back into original dataframe
case = temp

#%%
c = case.head(1000)
case.dtypes
case.count()
#%%
# check categorical columns for missing data
# ASA
asa_nan_count = case['ASA_Class'].isna().sum()
print(asa_nan_count)
# Institution
case['Institution'].value_counts(dropna=False)
inst_nan_count = case['Institution'].isna().sum()
print(inst_nan_count)
# Starting_Provider_Anes_Attending
starting_anes_att_count = case['Starting_Provider_Anes_Attending'].isna().sum()
print(starting_anes_att_count)
# Note: exclude row if "Starting_Provider_Anes_Attending" isna
# Primary_Provider_Surg_Attending
primary_surg_att_count = case['Primary_Provider_Surg_Attending'].isna().sum()
print(primary_surg_att_count)
# Note: too many rows with missing primary surgeons to exclude - could consider as a secondary GLMM analysis
case.Emergency_Status.value_counts(dropna=False)

#%%
# comorbidity coding 
# Elixhauser_Cardiac_Arrhythmia
case['Elixhauser_Cardiac_Arrhythmia'].value_counts(dropna=False)
case['elix_cardiac_arrhythmia'] = np.where((case['Elixhauser_Cardiac_Arrhythmia'] == 'Yes'), True, False)  
case[['Elixhauser_Cardiac_Arrhythmia', 'elix_cardiac_arrhythmia']].value_counts(dropna=False)
case[['elix_cardiac_arrhythmia']].value_counts(dropna=False)

#%%
# Elixhauser_Chronic_Pulmonary_Disease
case['Elixhauser_Chronic_Pulmonary_Disease'].value_counts(dropna=False)
case['elix_chronic_pulmonary'] = np.where((case['Elixhauser_Chronic_Pulmonary_Disease'] == 'Yes'), True, False)  
case[['Elixhauser_Chronic_Pulmonary_Disease', 'elix_chronic_pulmonary']].value_counts(dropna=False)
case[['elix_chronic_pulmonary']].value_counts(dropna=False)

#%%
# Elixhauser_Coagulopathy
case['Elixhauser_Coagulopathy'].value_counts(dropna=False)
case['elix_coagulopathy'] = np.where((case['Elixhauser_Coagulopathy'] == 'Yes'), True, False)  
case[['Elixhauser_Coagulopathy', 'elix_coagulopathy']].value_counts(dropna=False)
case[['elix_coagulopathy']].value_counts(dropna=False)

#%%
# Elixhauser_Congestive_Heart_Failure
case['Elixhauser_Congestive_Heart_Failure'].value_counts(dropna=False)
case['elix_chf'] = np.where((case['Elixhauser_Congestive_Heart_Failure'] == 'Yes'), True, False)  
case[['Elixhauser_Congestive_Heart_Failure', 'elix_chf']].value_counts(dropna=False)
case[['elix_chf']].value_counts(dropna=False)

#%%
# Elixhauser_Deficiency_Anemia
case['Elixhauser_Deficiency_Anemia'].value_counts(dropna=False)
case['elix_anemia'] = np.where((case['Elixhauser_Deficiency_Anemia'] == 'Yes'), True, False)  
case[['Elixhauser_Deficiency_Anemia', 'elix_anemia']].value_counts(dropna=False)
case[['elix_anemia']].value_counts(dropna=False)

#%%
# Elixhauser_Diabetes_with_Complications 
case['Elixhauser_Diabetes_with_Complications'].value_counts(dropna=False)
case['elix_dm_w_cx'] = np.where((case['Elixhauser_Diabetes_with_Complications'] == 'Yes'), True, False)  
case[['Elixhauser_Diabetes_with_Complications', 'elix_dm_w_cx']].value_counts(dropna=False)
case[['elix_dm_w_cx']].value_counts(dropna=False)

#%%
# Elixhauser_Diabetes_without_Complications 
case['Elixhauser_Diabetes_without_Complications'].value_counts(dropna=False)
case['elix_dm_w_out_cx'] = np.where((case['Elixhauser_Diabetes_without_Complications'] == 'Yes'), True, False)  
case[['Elixhauser_Diabetes_without_Complications', 'elix_dm_w_out_cx']].value_counts(dropna=False)
case[['elix_dm_w_out_cx']].value_counts(dropna=False)

#%%
# Elixhauser_Fluid_and_Electrolyte_Disorders 
case['Elixhauser_Fluid_and_Electrolyte_Disorders'].value_counts(dropna=False)
case['elix_fluid_elec'] = np.where((case['Elixhauser_Fluid_and_Electrolyte_Disorders'] == 'Yes'), True, False)  
case[['Elixhauser_Fluid_and_Electrolyte_Disorders', 'elix_fluid_elec']].value_counts(dropna=False)
case[['elix_fluid_elec']].value_counts(dropna=False)

#%%
# Elixhauser_Hypertension_with_Complications 
case['Elixhauser_Hypertension_with_Complications'].value_counts(dropna=False)
case['elix_htn_w_cx'] = np.where((case['Elixhauser_Hypertension_with_Complications'] == 'Yes'), True, False)  
case[['Elixhauser_Hypertension_with_Complications', 'elix_htn_w_cx']].value_counts(dropna=False)
case[['elix_htn_w_cx']].value_counts(dropna=False)

#%%
# Elixhauser_Hypertension_without_Complications 
case['Elixhauser_Hypertension_without_Complications'].value_counts(dropna=False)
case['elix_htn_w_out_cx'] = np.where((case['Elixhauser_Hypertension_without_Complications'] == 'Yes'), True, False)  
case[['Elixhauser_Hypertension_without_Complications', 'elix_htn_w_out_cx']].value_counts(dropna=False)
case[['elix_htn_w_out_cx']].value_counts(dropna=False)

#%%
# Elixhauser_Liver_Disease 
case['Elixhauser_Liver_Disease'].value_counts(dropna=False)
case['elix_liver'] = np.where((case['Elixhauser_Liver_Disease'] == 'Yes'), True, False)  
case[['Elixhauser_Liver_Disease', 'elix_liver']].value_counts(dropna=False)
case[['elix_liver']].value_counts(dropna=False)

#%%
# Elixhauser_Obesity 
case['Elixhauser_Obesity'].value_counts(dropna=False)
case['elix_obesity'] = np.where((case['Elixhauser_Obesity'] == 'Yes'), True, False)  
case[['Elixhauser_Obesity', 'elix_obesity']].value_counts(dropna=False)
case[['elix_obesity']].value_counts(dropna=False)

#%%
# Elixhauser_Other_Neurological_Disorders 
case['Elixhauser_Other_Neurological_Disorders'].value_counts(dropna=False)
case['elix_neurological'] = np.where((case['Elixhauser_Other_Neurological_Disorders'] == 'Yes'), True, False)  
case[['Elixhauser_Other_Neurological_Disorders', 'elix_neurological']].value_counts(dropna=False)
case[['elix_neurological']].value_counts(dropna=False)

#%%
# Elixhauser_Peripheral_Vascular_Disorders 
case['Elixhauser_Peripheral_Vascular_Disorders'].value_counts(dropna=False)
case['elix_pvd'] = np.where((case['Elixhauser_Peripheral_Vascular_Disorders'] == 'Yes'), True, False)  
case[['Elixhauser_Peripheral_Vascular_Disorders', 'elix_pvd']].value_counts(dropna=False)
case[['elix_pvd']].value_counts(dropna=False)

#%%
# Elixhauser_Pulmonary_Circulation_Disorders 
case['Elixhauser_Pulmonary_Circulation_Disorders'].value_counts(dropna=False)
case['elix_pulm_circ'] = np.where((case['Elixhauser_Pulmonary_Circulation_Disorders'] == 'Yes'), True, False)  
case[['Elixhauser_Pulmonary_Circulation_Disorders', 'elix_pulm_circ']].value_counts(dropna=False)
case[['elix_pulm_circ']].value_counts(dropna=False)

#%%
# Elixhauser_Renal_Failure 
case['Elixhauser_Renal_Failure'].value_counts(dropna=False)
case['elix_renal_fail'] = np.where((case['Elixhauser_Renal_Failure'] == 'Yes'), True, False)  
case[['Elixhauser_Renal_Failure', 'elix_renal_fail']].value_counts(dropna=False)
case[['elix_renal_fail']].value_counts(dropna=False)

#%%
# Elixhauser_Valvular_Disease 
case['Elixhauser_Valvular_Disease'].value_counts(dropna=False)
case['elix_valvular'] = np.where((case['Elixhauser_Valvular_Disease'] == 'Yes'), True, False)  
case[['Elixhauser_Valvular_Disease', 'elix_valvular']].value_counts(dropna=False)
case[['elix_valvular']].value_counts(dropna=False)
 
#%%
# Comorbidity_MPOG_Cerebrovascular_Disease 
case['Comorbidity_MPOG_Cerebrovascular_Disease'].value_counts(dropna=False)
case['comorbid_mpog_cvd'] = np.where((case['Comorbidity_MPOG_Cerebrovascular_Disease'] == 'Yes'),True, False)  
case[['Comorbidity_MPOG_Cerebrovascular_Disease', 'comorbid_mpog_cvd']].value_counts(dropna=False)
case[['comorbid_mpog_cvd']].value_counts(dropna=False)

#%%
# Comorbidity_MPOG_Coronary_Artery_Disease 
case['Comorbidity_MPOG_Coronary_Artery_Disease'].value_counts(dropna=False)
case['comorbid_mpog_cad'] = np.where((case['Comorbidity_MPOG_Coronary_Artery_Disease'] == 'Yes'), True, False)  
case[['Comorbidity_MPOG_Coronary_Artery_Disease', 'comorbid_mpog_cad']].value_counts(dropna=False)
case[['comorbid_mpog_cad']].value_counts(dropna=False)
 
#%%
# date variables
case[['Case_Date_dt']] = case[['Case_Date']].apply(pd.to_datetime, format='%Y-%m-%d %H:%M:%S')
case[['Preop_Start', 'Anesthesia_Start', 'Anesthesia_End', 'Patient_In_Room_Start', 'Patient_In_Room_End', ]] = case[['Preop_Start', 'Anesthesia_Start', 'Anesthesia_End', 'Patient_In_Room_Start', 'Patient_In_Room_End']].apply(pd.to_datetime, format='%Y-%m-%d %H:%M:%S')

#%%
# assign 1 to all rows as a surgery indicator
case['case_count_tot'] = case.groupby(['MPOG_Case_ID']).cumcount().add(1)
case['case_count_tot'].value_counts(dropna=False)

#%%
c = case.head(1000)

#%%
# to_period - required if goal column has year-month-day / year-month / year
# create year / month / day period variable
case['Case_Date_yr_mo_d'] = case['Case_Date_dt'].dt.to_period('D')
# create year / month period variable 
case['Case_Date_yr_mo'] = case['Case_Date_dt'].dt.to_period('M')
# create year period variable
case['Case_Date_yr'] = case['Case_Date_dt'].dt.to_period('Y')

#%%
# assign 1 to all rows as a surgery indicator
case['case_count_tot'] = case.groupby(['MPOG_Case_ID']).cumcount().add(1)
case['case_count_tot'].value_counts(dropna=False)

#%% 
# sequential merging
# sum case counts by Institution (for all years) & save as series 
inst_counts = case.groupby(['Institution'])['case_count_tot'].count()
# merge series into dataframe requires <to_frame>
m = case.merge(inst_counts.to_frame(), left_on=['Institution'], right_on=['Institution'], how='left', indicator=True)
m=m.rename({'_merge' : '_merge_0'}, axis=1)
m=m.rename({'case_count_tot_y' : 'case_count_tot_cum'}, axis=1)
m=m.rename({'case_count_tot_x' : 'case_indicator'}, axis=1)
m['_merge_0'].value_counts()["both"]
m['case_count_tot_cum'].describe()

#%%
# sum case counts by Institution (for year & month) & save as series 
inst_counts_yr_mo = case.groupby(['Institution', 'Case_Date_yr_mo'])['case_count_tot'].count()
# merge series into dataframe (requires <to_frame>)
m_1 = m.merge(inst_counts_yr_mo.to_frame(), left_on=['Institution', 'Case_Date_yr_mo'], right_on=['Institution', 'Case_Date_yr_mo'], how='left', indicator=True)
# check
m_1.dtypes
# rename
m_1 = m_1.rename({'_merge' : '_merge_1'}, axis=1)
m_1 = m_1.rename({'case_count_tot' : 'case_count_tot_yr_mo'}, axis=1)
m_1['_merge_1'].value_counts()["both"]
# check
c = m_1.head(1000)

#%%
# sum case counts by Institution (for year) & save as series 
inst_counts_yr = case.groupby(['Institution', 'Case_Date_yr'])['case_count_tot'].count()
# merge series into dataframe (requires <to_frame>)
m_2 = m_1.merge(inst_counts_yr.to_frame(), left_on=['Institution', 'Case_Date_yr'], right_on=['Institution', 'Case_Date_yr'], how='left', indicator=True)
# check
m_2.dtypes
# rename
m_2 = m_2.rename({'_merge' : '_merge_2'}, axis=1)
m_2 = m_2.rename({'case_count_tot' : 'case_count_tot_yr'}, axis=1)
m_2['_merge_2'].value_counts()["both"]
# check
c = m_2.head(1000)

#%%
# experimenting with line plots
# year & month
# issue - x-axis isn't justified according to date (e.g. some hospitals only have data 2020-2022 but others 2016-2022) 
inst_counts_yr_mo.groupby('Institution').plot(x='Case_Date_yr_mo', sharex=True)
inst_counts_yr_mo.groupby('Institution').plot(x='Case_Date_dt', sharex=True)

#%%
# year 
# issue - x-axis isn't justified according to date (e.g. some hospitals only have data 2020-2022 but others 2016-2022)
inst_counts_yr.groupby('Institution').plot(x='Case_Date_yr', sharex=True)
inst_counts_yr.groupby('Institution').plot(x='Case_Date_dt', sharex=True)


#%% this code will plot individual hospitals
inst_counts_yr.reset_index().groupby('Institution').plot(x='Case_Date_yr', sharex=True)

#%% this code will plot individual hospitals
inst_counts_yr_mo.reset_index().groupby('Institution').plot(x='Case_Date_yr_mo', sharex=True, use_index=True, legend=True, subplots=True, xlabel='Date: Year Month', ylabel='Case Count')

#%%
# add the Institution labels
#monthyearFmt = mdates.DateFormatter('%b %Y')
for (inst_id, group) in inst_counts_yr_mo.groupby('Institution'):
    g = group.reset_index()
    #g['Date_yr_mo'] = g['Case_Date_yr_mo'].astype('datetime64[M]')
    ax = g.plot(x='Case_Date_yr_mo', y='case_count_tot', title=f"Institution {inst_id}")
    #ax.xaxis.set_major_formatter(monthyearFmt)
    ax.minorticks_off()
    plt.show()

#%%
# add the Institution labels
for (inst_id, group) in inst_counts_yr.groupby('Institution'):
    g = group.reset_index()
    #g['Date_yr'] = g['Case_Date_yr'].astype('datetime64[Y]')
    ax = g.plot(x='Case_Date_yr', y='case_count_tot', title=f"Institution {inst_id}")
    ax.minorticks_off()
    plt.show()

#%%
# add the Institution labels
fix, ax = plt.subplots()
#monthyearFmt = mdates.DateFormatter('%b %Y')
for (inst_id, group) in inst_counts_yr_mo.groupby('Institution'):
    g = group.reset_index()
    #g['Date_yr_mo'] = g['Case_Date_yr_mo'].astype('datetime64[M]')
    g.plot(x='Case_Date_yr_mo', y='case_count_tot', label=f"{inst_id}", ax=ax)
    #ax.xaxis.set_major_formatter(monthyearFmt)
plt.show()

#%%
check = m_2[m_2['Institution'].isin(['53'])]
check = m_2[m_2['Institution'].isin(['97'])]
check = m_2[m_2['Institution'].isin(['99'])]

#%% 
# data visualization case counts - bar and line charts 
# bar plot for total surgical volume by hospital
inst_id_ser = pd.Series(m_2.Institution)
case_count_tot_cum_ser = pd.Series(m_2.case_count_tot_cum)
hos = pd.DataFrame({ 'inst': inst_id_ser, 'surg_count': case_count_tot_cum_ser})
hos.drop_duplicates(inplace=True)
hos.sort_values(by='surg_count', ascending=False, inplace=True)
hos.plot.bar(x='inst', y='surg_count', rot=90)

#%%
# check 
c = m_2.head(1000)
c = m_2.tail(1000)
m_2.count()
m_2.dtypes
######

#%%
# create working dataframe with relevant variables
c_t = case.head(1000)

working = m_2[['MPOG_Case_ID', 'MPOG_Patient_ID', 'Case_Date', 'Case_Date_dt', 'Case_Date_yr_mo_d', 'Case_Date_yr_mo', 'Case_Date_yr', 'Institution', 'case_indicator', 'case_count_tot_cum', 'case_count_tot_yr', 'case_count_tot_yr_mo', 'US_Institution', 'Age_In_Years', 'Sex', 'Height_cm', 'Weight_kg', 'BMI', 'ASA_Class', 'Weekend', 'Emergency_Status', 'Arrived_Intubated', 'Arterial_Line_Used', 'Primary_Surgical_CPT', 'Procedure_Type_Cardiac', 'Procedure_Text', 'Starting_Provider_Anes_Attending', 'Starting_Provider_CRNA', 'Starting_Provider_Anes_Resident', 'Primary_Provider_Surg_Attending', 'Anesthesia_Duration', 'Patient_In_Room_Duration', 'Cardiopulmonary_Bypass_Duration', 'Preop_Albumin_imp', 'Preop_Alk_Phosphatase_imp', 'Preop_ALT_imp', 'Preop_AST_imp', 'Preop_BUN_imp', 'Preop_Calcium_Total_imp', 'Preop_Glucose_imp', 'Preop_Hematocrit_imp', 'Preop_Hemoglobin_imp', 'Preop_Hgb_A1c_imp', 'Preop_INR_imp', 'Preop_Platelets_imp', 'Preop_Potassium_imp', 'Preop_PT_imp', 'Preop_PTT_imp', 'Preop_Sodium_imp', 'Preop_Total_Bilirubin_imp', 'Preop_WBC_imp', 'Intraop_PRBC_Volume_In_Units', 'Intraop_PRBC_Volume_In_MLs', 'Intraop_FFP_Volume_In_Units', 'Intraop_FFP_Volume_In_MLs', 'Intraop_Platelets_Volume_In_Units', 'Intraop_Platelets_Volume_In_MLs', 'Intraop_Cryo_Volume_In_Units', 'Intraop_Cryo_Volume_In_Units', 'Intraop_Cryo_Volume_In_MLs', 'Intraop_Crystalloids',  'elix_cardiac_arrhythmia', 'elix_chronic_pulmonary', 'elix_coagulopathy', 'elix_chf', 'elix_anemia', 'elix_dm_w_cx', 'elix_dm_w_out_cx',  'elix_htn_w_cx', 'elix_htn_w_out_cx', 'elix_fluid_elec', 'elix_liver', 'elix_neurological', 'elix_pvd', 'elix_pulm_circ', 'elix_renal_fail', 'elix_valvular',  'comorbid_mpog_cvd', 'comorbid_mpog_cad', 'TEE_intraop']]

#%%
# check
w = working.tail(1000)

#%%
# starting count
working['MPOG_Case_ID'].value_counts(dropna=False)
working['MPOG_Case_ID'].nunique()

#%%
# create exclusion indicators
# surgical volume exclusion
working['exclude_surg_vol'] = np.where((working['case_count_tot_yr'] <= 25), 1, 0)  
# check
working['exclude_surg_vol'].value_counts(dropna=False)

#%%
# starting anesthesia provider missing data exclusion
working['exclude_missing_starting_anes_attd'] = working['Starting_Provider_Anes_Attending'].isna()
working['exclude_missing_starting_anes_attd'] = np.where(working['Starting_Provider_Anes_Attending'].isna(), 1, 0)
# check
working['exclude_missing_starting_anes_attd'].value_counts(dropna=False)

#%% 
# missing, unknown, or invalid emergency status [note: emergency indicator yes/no remain]
working['exclude_missing_emergency_status'] = np.where((working['Emergency_Status'] == 'Missing or Unknown') | (working['Emergency_Status'] == 'Invalid Value'), 1, 0)
# check
working['exclude_missing_emergency_status'].value_counts(dropna=False)

#%%
# check
w = working.tail(1000)

#%% 
# list of exclusion variables
working['exclude_surg_vol'].value_counts(dropna=False)
working['exclude_missing_starting_anes_attd'].value_counts(dropna=False)
working['exclude_missing_emergency_status'].value_counts(dropna=False)

#%% 
# load pap systolic dataset
pap_s=pd.read_csv(
    filepath_or_buffer=os.path.join(dirname, "data", "PCRC_0094_Physio_PAP_Sys_120723.csv.gz"),
        index_col=False
)


#%% 
# look at pap_s data 
# create a smaller dataframe that will load
ps = pap_s.head()
ps = pap_s.head(1000)
pap_s.dtypes
pap_s.count()

#%%
# convert object to date
pap_s['Value_Observation_DT_pap_s'] = pd.to_datetime(pap_s['Value_Observation_DT'], infer_datetime_format=True)
# sort by date
pap_s.sort_values(by='Value_Observation_DT_pap_s')
print(pap_s)
# convert object to numeric 
pap_s['Value_s'] = pd.to_numeric(pap_s['Value'])
ps = pap_s.head(1000)
#%%
#pivot_table for transformation of data rows to columns grouped by MPOG case ID [note: pivot_table 'index' is the groupby]
# ps_pivot = ps.pivot_table(index=['MPOG_Case_ID'], columns=['Value_Observation_DT_pap_s'], values=['Value_s'])

#%% 
# set pap systolic threshold range for logic
pap_s['thresh_s'] = np.where((pap_s['Value_s'] <=100) & (pap_s['Value_s'] >=20), 1, 0)
pap_s['thresh_s'] = pd.to_numeric(pap_s['thresh_s'])

pap_s_gb = pap_s.groupby('MPOG_Case_ID', as_index=False).agg({'Value_s': ['min', 'max', 'mean'], 'thresh_s': 'count'})
pap_s_gb = pap_s.groupby('MPOG_Case_ID', as_index=False).agg(min_Value_s=('Value_s', 'min'), max_Value_s=('Value_s', 'max'), mean_Value_s=('Value_s', 'mean'), count_thresh_s=('thresh_s', 'sum'))

pap_s_gb['count_thresh_s'] = pd.to_numeric(pap_s_gb['count_thresh_s'])
pap_s_gb['pac_ind_s'] = np.where(pap_s_gb['count_thresh_s'] >=30, 1, 0)
pap_s_gb['pac_ind_s'] = np.where(pap_s_gb['count_thresh_s'] >=60, 1, 0)
pap_s_gb['pac_ind_s'].value_counts(dropna=False)

pap_s.nunique()
pap_s_gb.nunique()
print(pap_s_gb)

#%%
# sanity check (against indicator variables in pap_s_gb dataframe)
p_s_check = pap_s[pap_s['MPOG_Case_ID'].isin(['00d5278d-298d-ba05-e053-0ad4802066a3'])]
p_s_check = pap_s[pap_s['MPOG_Case_ID'].isin(['96c4cd68-f487-ec11-98c8-d65560f56ffa'])]
p_s_check = pap_s[pap_s['MPOG_Case_ID'].isin(['00053bef-13f9-ec11-813a-005056ad0e71', '96c4cd68-f487-ec11-98c8-d65560f56ffa', '00011587-3bd9-e911-a967-005056ace3cb'])]
p_s_check = pap_s[pap_s['MPOG_Case_ID'].isin(['00d5278d-298d-ba05-e053-0ad4802066a3', '00d5278d-b48d-ba05-e053-0ad4802066a3', '00d5278d-b88d-ba05-e053-0ad4802066a3'])] # nan issue example
p_s_check = pap_s[pap_s['MPOG_Case_ID'].isin(['00011587-3bd9-e911-a967-005056ace3cb'])]
p_s_check = pap_s[pap_s['MPOG_Case_ID'].isin(['00053bef-13f9-ec11-813a-005056ad0e71'])]
p_s_check = pap_s[pap_s['MPOG_Case_ID'].isin(['009a6173-0065-a601-e053-0ad48020a541'])]
p_s_check = pap_s[pap_s['MPOG_Case_ID'].isin(['ffdab438-735b-e911-8109-005056b6177e'])]
p_s_check = pap_s[pap_s['MPOG_Case_ID'].isin(['00d4443e-81c8-e811-8103-005056b6e40e'])]
print(p_s_check) 

pap_s_gb['pac_ind_s'].value_counts(dropna=False)

# dataframe for merging back into case file = "pap_s_gb"

######
#%%
# load pap diastolic dataset
pap_d=pd.read_csv(
    filepath_or_buffer=os.path.join(dirname, "data", "PCRC_0094_Physio_PAP_Dias_120723.csv.gz"),
        index_col=False
)

#%% 
# look at pap_d data 
# create a smaller dataframe that will load
pdi = pap_d.head()
pdi = pap_d.head(1000)
pap_d.dtypes
pap_d.count()

#%%
# convert object to date
# one option
pap_d['Value_Observation_DT_pap_d_1'] = pd.to_datetime(pap_d['Value_Observation_DT'], format='%Y-%m-%d %H:%M:%S') 
# another option 
pap_d['Value_Observation_DT_pap_d'] = pd.to_datetime(pap_d['Value_Observation_DT'], infer_datetime_format=True)
# check
pdi = pap_d.head(1000)
# sort by date
pap_d.sort_values(by='Value_Observation_DT_pap_d')
print(pap_d)
# convert object to numeric 
pap_d['Value_d'] = pd.to_numeric(pap_d['Value'])
pdi = pap_d.head(1000)

#%% 
# set pap diastolic threshold range for logic
pap_d['thresh_d'] = np.where((pap_d['Value_d'] <=60) & (pap_d['Value_d'] >=0), 1, 0)
pap_d_gb = pap_d.groupby('MPOG_Case_ID', as_index=False).agg({'Value_d': ['min', 'max', 'mean'], 'thresh_d': 'count'})
pap_d_gb = pap_d.groupby('MPOG_Case_ID', as_index=False).agg(min_Value_d=('Value_d', 'min'), max_Value_d=('Value_d', 'max'), mean_Value_d=('Value_d', 'mean'), count_thresh_d=('thresh_d', 'sum')) 
pap_d_gb['pac_ind_d'] = np.where(pap_d_gb['count_thresh_d'] >=60, 1, 0)
pap_d_gb['pac_ind_d'].value_counts(dropna=False)

#%%
pap_d.nunique()
pap_d_gb.nunique()
print(pap_d_gb)

#%%
# sanity check (against indicator variables in pap_d_gb dataframe)
p_d_check = pap_d[pap_d['MPOG_Case_ID'].isin(['0003e49a-bf6e-ed11-a848-000d3a1f389e'])]
p_d_check = pap_d[pap_d['MPOG_Case_ID'].isin(['007070d9-8876-e811-a2c9-00155de9bd26'])]
p_d_check = pap_d[pap_d['MPOG_Case_ID'].isin(['00f3ed6f-df88-a5ac-e053-c047649b93c8'])]
print(p_d_check)

pap_d_gb['pac_ind_d'].value_counts(dropna=False)


# dataframe for merging back into case file = "pap_d_gb"

#%%
# load pap mean dataset
pap_m=pd.read_csv(
    filepath_or_buffer=os.path.join(dirname, "data", "PCRC_0094_Physio_PAP_Mean_120723.csv.gz"),
        index_col=False
)

#%% 
# look at pap_m data 
# create a smaller dataframe that will load
pm = pap_m.head()
pm = pap_m.head(1000)
pap_m.dtypes
pap_m.count()

#%%
# convert object to date
# one option
pap_m['Value_Observation_DT_pap_m_1'] = pd.to_datetime(pap_d['Value_Observation_DT'], format='%Y-%m-%d %H:%M:%S') 
# another option 
pap_m['Value_Observation_DT_pap_m'] = pd.to_datetime(pap_d['Value_Observation_DT'], infer_datetime_format=True)
# check
pm = pap_m.head(1000)
# sort by date
pap_m.sort_values(by='Value_Observation_DT_pap_m')
print(pap_m)
# convert object to numeric 
pap_m['Value_m'] = pd.to_numeric(pap_m['Value'])
pm = pap_m.head(1000)

#%% 
# set pap mean threshold range for logic
pap_m['thresh_m'] = np.where((pap_m['Value_m'] <=80) & (pap_m['Value_m'] >=10), 1, 0)
pap_m_gb = pap_m.groupby('MPOG_Case_ID', as_index=False).agg({'Value_m': ['min', 'max', 'mean'], 'thresh_m': 'count'})
pap_m_gb = pap_m.groupby('MPOG_Case_ID', as_index=False).agg(min_Value_m=('Value_m', 'min'), max_Value_m=('Value_m', 'max'), mean_Value_m=('Value_m', 'mean'), count_thresh_m=('thresh_m', 'sum')) 
pap_m_gb['pac_ind_m'] = np.where(pap_m_gb['count_thresh_m'] >=60, 1, 0)
pap_m_gb['pac_ind_m'].value_counts(dropna=False)

#%%
pap_m.nunique()
pap_m_gb.nunique()
pap_m_gb.value_counts()

print(pap_m_gb)

#%%
# sanity check (against indicator variables in pap_m_gb dataframe)
check = pap_m[pap_m['MPOG_Case_ID'].isin(['00014aba-6847-e811-adce-005056a2520b'])]
check = pap_m[pap_m['MPOG_Case_ID'].isin(['000cf7ad-c330-ec11-a998-005056ace3cb'])]

print(check)

pap_m_gb['pac_ind_m'].value_counts(dropna=False)

# dataframe for merging back into case file = "pap_d_gb"

#%% 
pap_s_gb['pac_ind_s'].value_counts(dropna=False)
pap_d_gb['pac_ind_d'].value_counts(dropna=False)
pap_m_gb['pac_ind_m'].value_counts(dropna=False)

#%% 
# merge pulmonary arterial exposure data into working dataframe
# sequential merging
# pap_s_gb
m = working.merge(pap_s_gb, left_on=['MPOG_Case_ID'], right_on=['MPOG_Case_ID'], how='left', indicator=False)
m['pac_ind_s'].value_counts(dropna=False)

#%%
# pap_d_gb
m_1 = m.merge(pap_d_gb, left_on=['MPOG_Case_ID'], right_on=['MPOG_Case_ID'], how='left', indicator=False)
m_1['pac_ind_d'].value_counts(dropna=False)

#%%
# pap_m_gb
m_2 = m_1.merge(pap_m_gb, left_on=['MPOG_Case_ID'], right_on=['MPOG_Case_ID'], how='left', indicator=False)
m_2['pac_ind_m'].value_counts(dropna=False)

#%%
# define true/false exposures (PAC & TEE) 
m_2['PAC_intraop_exp'] = ((m_2['pac_ind_s'] == 1) | (m_2['pac_ind_d'] == 1) | (m_2['pac_ind_m'] == 1))
m_2['TEE_intraop_exp'] = ((m_2['TEE_intraop'] == 1)) 
# define 1/0 exposures (PAC & TEE) 
m_2['PAC_intraop'] = np.where((m_2['PAC_intraop_exp'] == True), 1, 0)
m_2['TEE_intraop'].value_counts(dropna=False)
# check
m_2['PAC_intraop'].value_counts(dropna=False)
m_2['TEE_intraop'].value_counts(dropna=False)

#%% 
# TEE by Institution (for all years) & save as series 
# note: count only if TEE_intraop == 1
inst_counts_tee = m_2[m_2['TEE_intraop'] == 1].groupby('Institution')['TEE_intraop'].count()
# merge series into dataframe requires <to_frame>
m_t = m_2.merge(inst_counts_tee.to_frame(), left_on=['Institution'], right_on=['Institution'], how='left', indicator=True)
# check
m_t.dtypes
# rename
m_t=m_t.rename({'_merge' : '_tee_merge_0'}, axis=1)
m_t=m_t.rename({'TEE_intraop_y': 'TEE_intraop_cum'}, axis=1)
m_t['_tee_merge_0'].value_counts()
# check
m_t['TEE_intraop_x'].value_counts()

#%%
# TEE by Institution (for year & month) & save as series 
inst_counts_tee_yr_mo = m_2[m_2['TEE_intraop'] == 1].groupby(['Institution', 'Case_Date_yr_mo'])['TEE_intraop'].count()
# merge series into dataframe (requires <to_frame>)
m_t_1 = m_t.merge(inst_counts_tee_yr_mo.to_frame(), left_on=['Institution', 'Case_Date_yr_mo'], right_on=['Institution', 'Case_Date_yr_mo'], how='left', indicator=True)
# check
m_t_1.dtypes
# rename
m_t_1=m_t_1.rename({'TEE_intraop': 'TEE_intraop_yr_mo'}, axis=1)
m_t_1 = m_t_1.rename({'_merge' : '_tee_merge_1'}, axis=1)
m_t_1['_tee_merge_1'].value_counts()["both"]
# check
c = m_t_1.head(1000)

#%%
# TEE by Institution (for year) & save as series 
inst_counts_tee_yr = m_2[m_2['TEE_intraop'] == 1].groupby(['Institution', 'Case_Date_yr'])['TEE_intraop'].count()
# merge series into dataframe (requires <to_frame>)
m_t_2 = m_t_1.merge(inst_counts_tee_yr.to_frame(), left_on=['Institution', 'Case_Date_yr'], right_on=['Institution', 'Case_Date_yr'], how='left', indicator=True)
# check
m_t_2.dtypes
# rename
m_t_2 = m_t_2.rename({'_merge' : '_tee_merge_2'}, axis=1)
m_t_2 = m_t_2.rename({'TEE_intraop' : 'TEE_intraop_yr'}, axis=1)
m_t_2['_tee_merge_2'].value_counts()

#%% 
# PAC by Institution (for all years) & save as series 
# note: count only if PAC_intraop == 1
inst_counts_pac = m_2[m_2['PAC_intraop'] == 1].groupby('Institution')['PAC_intraop'].count()
# merge series into dataframe requires <to_frame>
m_p = m_t_2.merge(inst_counts_pac.to_frame(), left_on=['Institution'], right_on=['Institution'], how='left', indicator=True)
# check
m_p.dtypes
# rename
m_p=m_p.rename({'_merge' : '_pac_merge_0'}, axis=1)
m_p=m_p.rename({'PAC_intraop_y': 'PAC_intraop_cum'}, axis=1)
m_p['_pac_merge_0'].value_counts()
# check
m_p['PAC_intraop_x'].value_counts()
# check
c = m_p.head(1000)

#%%
# PAC by Institution (for year & month) & save as series 
inst_counts_pac_yr_mo = m_2[m_2['PAC_intraop'] == 1].groupby(['Institution', 'Case_Date_yr_mo'])['PAC_intraop'].count()
# merge series into dataframe (requires <to_frame>)
m_p_1 = m_p.merge(inst_counts_pac_yr_mo.to_frame(), left_on=['Institution', 'Case_Date_yr_mo'], right_on=['Institution', 'Case_Date_yr_mo'], how='left', indicator=True)
# check
m_p_1.dtypes
# rename
m_p_1=m_p_1.rename({'PAC_intraop': 'PAC_intraop_yr_mo'}, axis=1)
m_p_1 = m_p_1.rename({'_merge' : '_pac_merge_1'}, axis=1)
m_p_1['_pac_merge_1'].value_counts()
# check
c = m_p_1.head(1000)

#%%
# PAC by Institution (for year) & save as series 
inst_counts_pac_yr = m_2[m_2['PAC_intraop'] == 1].groupby(['Institution', 'Case_Date_yr'])['PAC_intraop'].count()
# merge series into dataframe (requires <to_frame>)
m_p_2 = m_p_1.merge(inst_counts_pac_yr.to_frame(), left_on=['Institution', 'Case_Date_yr'], right_on=['Institution', 'Case_Date_yr'], how='left', indicator=True)
# check
m_p_2.dtypes
# rename
m_p_2 = m_p_2.rename({'_merge' : '_pac_merge_2'}, axis=1)
m_p_2 = m_p_2.rename({'PAC_intraop' : 'PAC_intraop_yr'}, axis=1)
m_p_2['_pac_merge_2'].value_counts()

#%% 
# update working dataframe
working = m_p_2

#%%
# calculate % exposure use overall / by year / by year & month
# ensure columns are numerical & make sure nan values are replaced with zeroo
working['TEE_intraop_cum'] = pd.to_numeric(working['TEE_intraop_cum'].replace(np.nan, 0))
working['TEE_intraop_yr_mo'] = pd.to_numeric(working['TEE_intraop_yr_mo'].replace(np.nan, 0))
working['TEE_intraop_yr'] = pd.to_numeric(working['TEE_intraop_yr'].replace(np.nan, 0))

# calcuate the TEE rates
working['tee_rate'] = working['TEE_intraop_cum'] / working['case_count_tot_cum']
working['tee_rate_yr_mo'] = working['TEE_intraop_yr_mo'] / working['case_count_tot_yr_mo']
working['tee_rate_yr'] = working['TEE_intraop_yr'] / working['case_count_tot_yr']

# check
s = working[['Institution', 'tee_rate', 'Case_Date_yr_mo', 'tee_rate_yr_mo', 'Case_Date_yr', 'tee_rate_yr', 'TEE_intraop_cum', 'case_count_tot_cum']]

#%%
# PAC
# ensure columns are numerical 
working['PAC_intraop_cum'] = pd.to_numeric(working['PAC_intraop_cum'].replace(np.nan, 0))
working['PAC_intraop_yr_mo'] = pd.to_numeric(working['PAC_intraop_yr_mo'].replace(np.nan, 0))
working['PAC_intraop_yr'] = pd.to_numeric(working['PAC_intraop_yr'].replace(np.nan, 0))

# divide one column by a second column
working['pac_rate'] = working['PAC_intraop_cum'] / working['case_count_tot_cum']
working['pac_rate_yr_mo'] = working['PAC_intraop_yr_mo'] / working['case_count_tot_yr_mo']
working['pac_rate_yr'] = working['PAC_intraop_yr'] / working['case_count_tot_yr']

# check
s = working[['Institution', 'tee_rate', 'pac_rate', 'Case_Date_yr_mo', 'tee_rate_yr_mo', 'pac_rate_yr_mo', 'Case_Date_yr', 'tee_rate_yr', 'pac_rate_yr']]

#%%
# check
check = m_2[m_2['Institution'].isin(['114'])]

#%%
# data visualizations
#%%
tee_rate_fig = working[['Case_Date_yr', 'Institution', 'tee_rate_yr']]
tee_rate_fig.drop_duplicates(inplace=True)
tee_rate_fig.astype({"Case_Date_yr": 'str', "Institution": 'str'}) 
print() 

#%%
# pivot the data 
tee_pivot = tee_rate_fig.pivot(index='Case_Date_yr', columns='Institution', values='tee_rate_yr')
# check
tee_pivot.head()

#%%
# pivot_table the data
tee_pivot_table = tee_rate_fig.pivot_table(
    index=['Case_Date_yr'], 
    columns=['Institution'], 
    values=['tee_rate_yr'])
# check
tee_pivot_table.head()
tee_pivot_table.reset_index()


#%%
# matplotlib: line plot
tee_pivot.plot(figsize=(20,10))
tee_pivot.plot(figsize=(40,10))

#%%
# pandas: area plot
ax = tee_pivot.plot.area(figsize=(50,20))
ax = tee_pivot.plot.area(figsize=(30,10))

#%%
#%%
# seborn
# good example but error in my code when I try to replicate: https://python-graph-gallery.com/web-stacked-line-chart-with-labels/
# import seaborn.objects as so
# sns.relplot(data=tee_rate_fig, x="Case_Date_yr", y="tee_rate_yr", hue="Institution", kind="line")
#%%
w = working.head(1000)

#%%
# regex validation website: https://regex101.com/
# regex to separate surgical categories 
surg_text = working[['Procedure_Text', 'MPOG_Case_ID', 'MPOG_Patient_ID']]

surg_text = m_p_2[['Procedure_Text', 'MPOG_Case_ID', 'MPOG_Patient_ID']]

#%% 
surg_text['cabg'] = surg_text['Procedure_Text'].str.extract(r'(CABG|CAB|coronary\s{0,3}artery\s{0,3}bypass|bypass\s{0,3}graft\s{0,3}coronary|coronary\s{0,3}artery\s{0,3}bypas|coronary\s{0,3}atery\s{0,3}bypassCA\s{0,3}BG|LIMA|SVG|BIMA|CAD|right\s{0,3}coronary|off-pump|bypass\s{0,3}graft\s{0,3}revision\s{0,3}coronary|coronary-artery\s{0,3}bypass|coronary\s{0,3}artery\s{0,3}x\s{0,3}3|coronary\s{0,3}artery\s{0,3}bypss|coroanary|bypass\s{0,3}graft\s{0,3}robot|graft\s{0,3}x|bypass\s{0,3}graft\s{0,3}with\s{0,3}pump|triple\s{0,3}bypass|coronary\s{0,3}arterial|bypass\s{0,3}graft\s{0,3}artery\s{0,3}cor|x\s{0,3}\d|bypass\s{0,3}art\s{0,3}cor)', re.IGNORECASE).notna()

surg_text['mitral'] = surg_text['Procedure_Text'].str.extract(r'(mv|mvr|mitral|mr\s{1,3}repair|\s{1,3}mr\s{1,3}|mtiral)', re.IGNORECASE).notna()
surg_text['mv_repair'] = surg_text['Procedure_Text'].str.extract(r'(mitral\s{0,3}valve\s{0,3}repair|mv\s{0,3}repair|MR\s{1,3}repair|mitral\s{0,3}repair|(?=MV).*(?=repair)|(?=mitral).*(?=repair)|valvuloplasty\s{0,3}mitral|repair\s{0,3}mitral|mitral\s{0,3}valve\s{0,3}annuloplasty|repair\s{0,3}valve\s{0,3}mitral|annuloplasty\s{0,3}mitral|mitral\s{0,3}valvoplasty|repair\s{0,3}of\s{0,3}mitral|(?=repa).*(?=mitral)|(?=ring).*(?=mitral)|complex\s{0,3}mitral\s{0,3}valvuloplasty)', re.IGNORECASE).notna()
surg_text['mv_replace'] = surg_text['Procedure_Text'].str.extract(r'(mitral\s{0,3}valve\s{0,3}replacement|MVR\s{0,3}|mitral\s{0,3}valve\s{0,3}repair\s{0,3}or\s{0,3}replacement|MV\s{0,3}replacement|mechanical\s{0,3}mitral|replacement\s{0,3}mitral|replacement\s{0,3}of\s{0,3}mitral|epic\s{0,3}mitral|(?=replacement).*(?=mitral)|(?=mitral\s{0,3}).*(?=repla)|repair\s{0,3}or\s{0,3}replace\s{0,3}valve\s{0,3}mitral|replace\s{0,3}mitral\s{0,3}|mitral\s{0,3}valve\s{0,3}relp|replac\s{0,3}mitral|(?=mitral\s{0,3}).*(?=epic))', re.IGNORECASE).notna()
surg_text['check_mitral'] = np.where((surg_text['mitral']==True) & (surg_text['mv_repair']==False) & (surg_text['mv_replace']==False), True, False) 
surg_text['check_mitral'].value_counts(dropna=False)

surg_text['tricuspid'] = surg_text['Procedure_Text'].str.extract(r'(tv|tvr|tricuspid|\s{1,3}tric\s{1,3})', re.IGNORECASE).notna()
surg_text['tv_repair'] = surg_text['Procedure_Text'].str.extract(r'(tricuspid\s{0,3}valve\s{0,3}repair|TV\s{0,3}repair|TR\s{1,3}repair|tricuspid\s{0,3}repair|valvuloplasty\s{0,3}tricuspid|repair\s{0,3}tricuspid|tricuspid\s{0,3}valve\s{0,3}annuloplasty|tricuspid\s{0,3}annuloplasty|repair\s{0,3}valve\s{0,3}tricuspid|annuloplasty\s{0,3}tricuspid|tricuspid\s{0,3}valvoplasty|(?=repair).*(?=tricuspid)|tricuspid\s{0,3}valve\s{0,3}ring|tv\s{0,3}annuloplasty)', re.IGNORECASE).notna()
surg_text['tv_replace'] = surg_text['Procedure_Text'].str.extract(r'(tricuspid\s{0,3}valve\s{0,3}replac|TVR\s{0,3}|tricuspid\s{0,3}valve\s{0,3}repair\s{0,3}or\s{0,3}replacement|TV\s{0,3}replacement|mechanical\s{0,3}tricuspid|replacement\s{0,3}tricuspid|replace\s{0,3}tricuspid\s{0,3}valve)', re.IGNORECASE).notna()
surg_text['check_tricuspid'] = np.where((surg_text['tricuspid']==True) & (surg_text['tv_repair']==False) & (surg_text['tv_replace']==False), True, False) 
surg_text['check_tricuspid'].value_counts(dropna=False)

surg_text['pulmonic'] = surg_text['Procedure_Text'].str.extract(r'(pv\s{0,3}r|pvr|pulmonic\s{0,3}v|pulmonary\s{0,3}valve)', re.IGNORECASE).notna()
surg_text['pv_repair'] = surg_text['Procedure_Text'].str.extract(r'(pulmonic\s{0,3}valve\s{0,3}repair|PV\s{0,3}repair|pulmonary\s{1,3}valve\s{0,3}repair|pulmonic\s{0,3}repair|valvuloplasty\s{0,3}pulmonic|repair\s{0,3}pulmonic|pulmonic\s{0,3}valve\s{0,3}annuloplasty|pulmonic\s{0,3}annuloplasty|repair\s{0,3}valve\s{0,3}pulmonic|annuloplasty\s{0,3}pulmonic|pulmonic\s{0,3}valvoplasty|(?=repair).*(?=pulmonic)|pulmonic\s{0,3}valve\s{0,3}ring|tv\s{0,3}annuloplasty|repair\s{0,3}of\s{0,3}pulmonary\s{0,3}valve)', re.IGNORECASE).notna()
surg_text['pv_replace'] = surg_text['Procedure_Text'].str.extract(r'(pulmonic\s{0,3}valve\s{0,3}replac|pulmonary\s{0,3}valve\s{0,3}replacement|PVR\s{0,3}|pulmonary\s{0,3}valve\s{0,3}replac|PV\s{0,3}replacement|mechanical\s{0,3}pulmonic|replacement\s{0,3}pulmonary|replacement\s{0,3}pulmonic|replace\s{0,3}pulmonic\s{0,3}valve|pulmonary\s{0,3}valve\s{0,3}repair/replac|replace\s{0,3}pulmonary\s{0,3}valve|replacement\s{0,3}of\s{0,3}pulmonary\s{0,3}valve|replacement aortic&pulmon valves)', re.IGNORECASE).notna()
surg_text['pulm_homograft'] = surg_text['Procedure_Text'].str.extract(r'(pulmonary\s{0,3}valve\s{0,3}homo)', re.IGNORECASE).notna()
surg_text['ross'] = surg_text['Procedure_Text'].str.extract(r'(replacement\s{0,3}aortic\s{0,3}valve\s{0,3}with\s{0,3}autologous\s{0,3}pulmonic\s{0,3}valve|(?=replacement\s{0,3}aortic\s{0,3}valve).*(?=autologous\s{0,3}pulmonary\s{0,3}valve))', re.IGNORECASE).notna()
surg_text['check_pulmonic'] = np.where((surg_text['pulmonic']==True) & (surg_text['pv_repair']==False) & (surg_text['pv_replace']==False) & (surg_text['pulm_homograft']==False) & (surg_text['ross']==False), True, False) 
surg_text['check_pulmonic'].value_counts(dropna=False)

surg_text['aortic_v'] = surg_text['Procedure_Text'].str.extract(r'(\s{1,3}av\s{1,3}r|avr|replacement\s{0,3}aortic&pulmon\s{0,3}valves|aortic\s{0,3}val|aoritc\s{0,3}valve|aorti\s{0,3}valve|aortiv\s{0,3}val|aortic\s{0,3}vlve|replacement\s{0,3}aortic\s{0,3}valve|valve\s{0,3}aortic|bioroot|vs-arr|vsarr|bentall|bioprosthetic\s{0,3}a|wheat)', re.IGNORECASE).notna()
surg_text['avss_av_repair'] = surg_text['Procedure_Text'].str.extract(r'(valve\s{0,3}sparing\s{0,3}|valve-sparing|aortic\s{0,3}valve\s{0,3}sparVSARR|aortic\s{0,3}valve\s{0,3}repair|repair\s{0,3}aortic\s{0,3}valve|AV\s{0,3}repair|valvuloplasty\s{0,3}aortic\s{0,3}valve|resuspension|resusspension|re-suspension|suspension|VSARR|VS-ARR|subcommisural\s{0,3}annuloplasty|aortic\s{0,3}valve\s{0,3}commissuroplasty|reconstruction\s{0,3}of\s{0,3}aortic\s{0,3}valve\s{1,3}|aortic\s{0,3}valvuloplasty|HAART|aortic valv rep|aortic valve rep|reimplantation native aortic valve|aortiv valve repair|aortic valve resuspention)', re.IGNORECASE).notna()
surg_text['av_replace'] = surg_text['Procedure_Text'].str.extract(r'(AVR|aortic\s{0,3}valve\s{0,3}repla|replacement\s{0,3}aortic\s{0,3}valve|replacement\s{0,3}valve\s{0,3}aortic|aortic\s{0,3}valve\s{0,3}repair or replace|valve\s{0,3}aortic\s{0,3}replace|replacement\s{0,3}prosthetic\s{0,3}aortic\s{0,3}valve|replace\s{0,3}aortic\s{0,3}valve|valve\s{0,3}conduit|AV\s{0,3}replace|bentall|KONNECT|KONECT|valved\s{0,3}conduit|Bioroot|(?=aortic\s{0,3}valve).*(?=replac)|(?=replacement).*(?=aortic\s{0,3}valve)|(?=replacement).*(?=aortic\s{0,3}and).*(?=valve)|(?=aortic\s{0,3}and).*(?=valve\s{0,3}replace)|Magna|(?=aortic\s{0,3}valve).*(?=mechanical)|(?=mechanical).*(?=aortic\s{0,3}valve)|mechanical valve aortic|(?=aortic\s{0,3}valve).*(?=tissue)|(?=tissue).*(?=aortic\s{0,3}valve)|(?=aortic\s{0,3}valve).*(?=bio)(?=aortic\s{0,3}valve).*(?=inspiris)|Inspirus|Mosaic|Mosaic\s{0,3}aortic\s{0,3}valve|stentless|tissue\s{0,3}aortic\s{0,3}valve|Wheat|aortic\s{0,3}valve\s{0,3}homograft|aoritc valve replacement|aorti valve replacement|aortic valv replacement|aortic vlve replacement|aortiv valve repl|aortic valvle replacement|replacement aortic&pulmon valves|aortic vale replacment|replac aortic valv|aortic vale replacement|aortic valve replcement|replace valve aortic|aortic valve eplacement|replacement of aortic valve|replacemen  aortic valve|aortic valve homagraft)', re.IGNORECASE).notna()
surg_text['check_av'] = np.where((surg_text['aortic_v']==True) & (surg_text['avss_av_repair']==False) & (surg_text['av_replace']==False), True, False) 
surg_text['check_av'].value_counts(dropna=False)

surg_text['aortic_prox'] = surg_text['Procedure_Text'].str.extract(r'(aorta|aortic\s{0,3}root|asc|arch|type\s{0,3}a|elephant\s{0,3}trunk\s{0,3}|bioroot|thoracic\s{0,3}aortic\s{0,3}aneur|bentall|aortic\s{0,3}dissection|dissection\s{0,3}repair|aortic\s{0,3}aneurysm\s{0,3}repair|hemiarch|hemi|aortic\s{0,3}repair|SOV|aortic{0,3}pseudo|valve\s{0,3}spar|root|rooot|aortic\s{0,3}pseudo|aortic\s{0,3}replacement|wheat|coarct|buffalo\s{0,3}trunk|valsalva|type\s{0,3}I\s{0,3}dissection)', re.IGNORECASE).notna()
surg_text['aortic_prox'].value_counts(dropna=False)

surg_text['aortic_desc'] = surg_text['Procedure_Text'].str.extract(r'(thoracoabdominal|thoraco-abdominal|taaa|abdominal\s{0,3}aneurysm|abdominal\s{0,3}aortic\s{0,3}aneurysm|desc\s{0,3}aorta|type\s{0,3}four\s{0,3}aneur|descending\s{0,3}aortic\s{0,3}aneur|descending\s{0,3}thoracic)', re.IGNORECASE).notna()
surg_text['aortic_desc'].value_counts(dropna=False)

surg_text['lung_tx'] = surg_text['Procedure_Text'].str.extract(r'(lung/|lung\s{0,3}bilateral|bilateral\s{0,3}lung|lung\s{0,3}single|clamshell|double\s{0,3}lung|single\s{0,3}lung|lung\s{0,3}transplant|right\s{0,3}single|left\s{0,3}single|transplant\s{0,3}lung|right\s{0,3}lung|left\s{0,3}lung|slt|lung\s{0,3}tx|lung\s{0,3}tr)', re.IGNORECASE).notna()
surg_text['lung_tx'].value_counts(dropna=False)

surg_text['heart_tx'] = surg_text['Procedure_Text'].str.extract(r'(OHT|\s{1,3}OTH\s{1,3}|heart\s{0,3}tr|transplant.\s{0,3}heart|heart\s{0,3}[a-z]{0,9}.\s{0,3}transplant|(?=heart).*(?=transplant))', re.IGNORECASE).notna()
surg_text['heart_tx'].value_counts(dropna=False)

surg_text['lvad'] = surg_text['Procedure_Text'].str.extract(r'(LVAD|VAD|HM3|HMIII|ventricular\s{0,3}assist|mate|HMII|HM\s{0,3}II|HM\s{0,3}2)', re.IGNORECASE).notna()
surg_text['lvad'].value_counts(dropna=False)
surg_text['rvad'] = surg_text['Procedure_Text'].str.extract(r'(RVAD)', re.IGNORECASE).notna()
surg_text['rvad'].value_counts(dropna=False)
surg_text['vad_explant'] = surg_text['Procedure_Text'].str.extract(r'(VAD\s{0,3}explant|VAD\s{0,3}removal})', re.IGNORECASE).notna()
surg_text['vad_explant'].value_counts(dropna=False)
surg_text['lvad_implant'] = np.where((surg_text['lvad']==True) & (surg_text['vad_explant']==False), True, False)
surg_text['lvad_implant'].value_counts(dropna=False)
surg_text['rvad_implant'] = np.where((surg_text['rvad']==True) & (surg_text['vad_explant']==False), True, False)

surg_text['impella'] = surg_text['Procedure_Text'].str.extract(r'(impella)', re.IGNORECASE).notna()
surg_text['impella_removal'] = surg_text['Procedure_Text'].str.extract(r'(impella\s{0,3}removal|impella\s{0,3}decan)', re.IGNORECASE).notna()
surg_text['impella_implant'] = np.where((surg_text['impella']==True) & (surg_text['impella_removal']==False), True, False)
surg_text['impella_implant'].value_counts(dropna=False)

surg_text['centrimag'] = surg_text['Procedure_Text'].str.extract(r'(centrimag)', re.IGNORECASE).notna()
surg_text['centrimag_removal'] = surg_text['Procedure_Text'].str.extract(r'(centrimag\s{0,3}removal)', re.IGNORECASE).notna()
surg_text['centrimag_implant'] = np.where((surg_text['centrimag']==True) & (surg_text['centrimag_removal']==False), True, False)
surg_text['centrimag_implant'].value_counts(dropna=False)

surg_text['iabp'] = surg_text['Procedure_Text'].str.extract(r'(intra.aortic|balloon)', re.IGNORECASE).notna()
surg_text['iabp'].value_counts(dropna=False)

surg_text['protek'] = surg_text['Procedure_Text'].str.extract(r'(protek|duo)', re.IGNORECASE).notna()
surg_text['protek'].value_counts(dropna=False)

surg_text['ecmo'] = surg_text['Procedure_Text'].str.extract(r'(ECMO|extracorp)', re.IGNORECASE).notna()
surg_text['ecmo_decan'] = surg_text['Procedure_Text'].str.extract(r'(ecmo\s{0,3}decan)', re.IGNORECASE).notna()
surg_text['ecmo_on'] = np.where((surg_text['ecmo']==True) & (surg_text['ecmo_decan']==False), True, False)
surg_text['ecmo'].value_counts(dropna=False)
surg_text['ecmo_on'].value_counts(dropna=False)

surg_text['pulm_endart'] = surg_text['Procedure_Text'].str.extract(r'(\s{1,3}PTE\s{1,3}|pulmonary\s{0,3}endart)', re.IGNORECASE).notna()
surg_text['pulm_endart'].value_counts(dropna=False)

surg_text['structural'] = surg_text['Procedure_Text'].str.extract(r'(VSD|ASD|myectomy|myomectomy|atrial\s{0,3}mass|mass\s{0,3}resection|PFO|myxoma|pericardectomy|pericardiectomy|RVOT\s{0,3}repair|subaortic|mass|rv\s{0,3}conduit|septal\s{0,3}defect|fibroelastoma|RVOT\s{0,3}stenosis\s{0,3}repair|unroofing|fontan|tof|tetralogy|conduit|SVC|subaortic|fistula|sub-aortic|rvot|lvot|secundum|MAZE|Ebstein|scimitar|anomalous\s{0,3}coronary|pericardial|septum|left\s{0,3}atrial\s{0,3}thrombectomy|LV\s{0,3}aneur|pericard|pricard|RCA\s{0,3}pseudo|atrial|anomalous|anomolous|anomalies|pseudoaneurysm\s{0,3}repair|ALCAPA|RV\s{0,3}repair|sinus\s{0,3}venosus|cardiac\s{0,3}tumor|IVC\s{0,3}tumor|lesion|apical\s{0,3}aneurysm)', re.IGNORECASE).notna()

surg_text['redo'] = surg_text['Procedure_Text'].str.extract(r'(redo|re-do|re-op\s{0,3}sternotomy|re-op)', re.IGNORECASE).notna()

surg_text['chest_washout'] = surg_text['Procedure_Text'].str.extract(r'(chest\s{0,3}washout|washout|chest\s{0,3}explor|mediastinal\s{0,3}expl|exploration\s{0,3}chest|expl|debridement\s{0,3}chest|post-op\s{0,3}bleed\s{0,3}cardiac)', re.IGNORECASE).notna()

surg_text['chest_closure'] = surg_text['Procedure_Text'].str.extract(r'(closure\s{0,3}surgical\s{0,3}wound\s{0,3}chest)', re.IGNORECASE).notna()

surg_text['missing'] = surg_text['Procedure_Text'].str.extract(r'(missing)', re.IGNORECASE).notna()

surg_text['aborted'] = surg_text['Procedure_Text'].str.extract(r'(aborted)', re.IGNORECASE).notna()

#%%
# sanity check
surg_text['marked'] = np.where((surg_text['cabg']==True) | (surg_text['mitral']==True) | (surg_text['tricuspid']==True) | (surg_text['pulmonic']==True) | (surg_text['aortic_v']==True) | (surg_text['aortic_prox']==True) | (surg_text['aortic_desc']==True) | (surg_text['lung_tx']==True) | (surg_text['heart_tx']==True) | (surg_text['lvad']==True) | (surg_text['rvad']==True) | (surg_text['impella']==True) | (surg_text['iabp']==True) | (surg_text['protek']==True)  | (surg_text['centrimag']==True) | (surg_text['ecmo']==True) | (surg_text['pulm_endart']==True) | (surg_text['structural']==True) | (surg_text['redo']==True) | (surg_text['chest_washout']==True) | (surg_text['chest_closure']==True) | (surg_text['missing']==True), 1, 0) 
# check
surg_text['marked'].value_counts(dropna=False)

#%%
# idicator for other surgeries - not classified in any of the cases above                                    
surg_text['other_surg'] = surg_text['marked']==0

#%%
# create isolated_cabg column
surg_text['isolated_CABG'] = np.where((surg_text['cabg']==True) & ((surg_text['mitral']==False) & (surg_text['tricuspid']==False) & (surg_text['pulmonic']==False) & (surg_text['aortic_v']==False) & (surg_text['aortic_prox']==False) & (surg_text['aortic_desc']==False) & (surg_text['lung_tx']==False) | (surg_text['heart_tx']==False) & (surg_text['lvad']==False) & (surg_text['rvad']==False) & (surg_text['impella']==False) & (surg_text['pulm_endart']==False) & (surg_text['structural']==False) & (surg_text['redo']==False) & (surg_text['chest_washout']==False) & (surg_text['chest_closure']==False) & (surg_text['missing']==False) & (surg_text['other_surg']==False)), True, False) 

# check
surg_text['isolated_CABG'].value_counts(dropna=False)

#%% 
# drop columns with prefix "check_"
surg_text.drop(list(surg_text.filter(regex='check')), axis=1, inplace=True)

#%% 
# merge surgical categories into working 
m_w = working.merge(surg_text, left_on=['MPOG_Case_ID'], right_on=['MPOG_Case_ID'], how='left', indicator=True)
m_w = m_w.rename({'_merge' : '_surg_cat_merge'}, axis=1)

#%%
# sanity check
temp = m_w.head(2000)

#%% 
# update working file 
working_2 = m_w

#%%
# Exclusions
# look at previously-defined exclude variables
working_2['exclude_missing_starting_anes_attd'].value_counts(dropna=False)
working_2['exclude_missing_emergency_status'].value_counts(dropna=False)
working_2['exclude_surg_vol'].value_counts(dropna=False)

# generate additional exclude variables 
working_2['exclude_missing_surg_cat'] = np.where((working_2['missing']==True), 1, 0)
working_2['exclude_missing_surg_cat'].value_counts(dropna=False)
#
working_2['Cardiopulmonary_Bypass_Duration'].describe()
working_2['exclude_cpb_time_under_20'] = np.where((working_2['Cardiopulmonary_Bypass_Duration'] <= 20), 1, 0)  
working_2['exclude_cpb_time_under_20'].value_counts(dropna=False)
working_2['Cardiopulmonary_Bypass_Duration'][working_2['exclude_cpb_time_under_20'] == 1].describe()
#
working_2['exclude_aborted_surg_cat'] = np.where((working_2['aborted']==True), 1, 0)
working_2['exclude_aborted_surg_cat'].value_counts(dropna=False)
#
working_2['exclude_chest_expl_or_close'] = np.where((working_2['chest_washout']==True | (working_2['chest_closure']==True)), 1, 0)
working_2['exclude_chest_expl_or_close'].value_counts(dropna=False)
#
working_2['exclude_arrived_intub'] = np.where((working_2['Arrived_Intubated']=='Yes'), 1, 0)
working_2['exclude_arrived_intub'].value_counts(dropna=False)



#%% cohort consort 
# starting count
working_2['case_indicator'].value_counts(dropna=False)

# 1st exclusion count
working_2['exclude_missing_starting_anes_attd'].value_counts(dropna=False) # exclusion count
tmp_1 = working_2[working_2['exclude_missing_starting_anes_attd'] == 0] # tmp_1 - dataframe with first exclusion 
tmp_1['case_indicator'].value_counts(dropna=False) # inclusion count

# 2nd exclusion count 
tmp_1['exclude_missing_emergency_status'].value_counts(dropna=False) # exclusion count 
tmp_2 = tmp_1[tmp_1['exclude_missing_emergency_status'] == 0] # tmp_2 - dataframe with first & second exclusions 
tmp_2['case_indicator'].value_counts(dropna=False) # inclusion count

# 3rd exclusion count
tmp_2['exclude_surg_vol'].value_counts(dropna=False) # exclusion count
tmp_3 = tmp_2[tmp_2['exclude_surg_vol'] == 0] # tmp_3 - dataframe with first, second, & third exclusions 
tmp_3['case_indicator'].value_counts(dropna=False) # inclusion count

# 4th exclusion count
tmp_3['exclude_cpb_time_under_20'].value_counts(dropna=False) # exclusion count
tmp_4 = tmp_3[tmp_3['exclude_cpb_time_under_20'] == 0] # tmp_4 - dataframe with first, second, third, & fourth exclusions 
tmp_4['case_indicator'].value_counts(dropna=False) # inclusion count

# 5th exclusionn count
tmp_4['exclude_aborted_surg_cat'].value_counts(dropna=False)
tmp_5 = tmp_4[tmp_4['exclude_aborted_surg_cat'] == 0] # tmp_5 - dataframe with first, second, third, fourth, & fifth exclusions 
tmp_5['case_indicator'].value_counts(dropna=False) # inclusion count

# 6th exclusion count 
tmp_5['exclude_chest_expl_or_close'].value_counts(dropna=False)
tmp_6 = tmp_5[tmp_5['exclude_chest_expl_or_close'] == 0] # tmp_5 - dataframe with first, second, third, fourth, & fifth exclusions 
tmp_6['case_indicator'].value_counts(dropna=False) # inclusion count

#%%
# 7th exclusion count 
tmp_6['exclude_arrived_intub'].value_counts(dropna=False)
tmp_7 = tmp_6[tmp_6['exclude_arrived_intub'] == 0] # tmp_5 - dataframe with first, second, third, fourth, & fifth exclusions 
tmp_7['case_indicator'].value_counts(dropna=False) # inclusion count

# final cohort count
tmp_7['case_indicator'].value_counts(dropna=False) # inclusion count


#%%
working_2 = tmp_7 # update working dataframe conditional on all exclusion conditions already 
working_2['case_indicator'].value_counts(dropna=False) # inclusion count

w = working_2.tail(2000)


#%%
working_2['case_indicator'].value_counts(dropna=False)
working_2['PAC_intraop_exp'].value_counts(dropna=False)
working_2['TEE_intraop_exp'].value_counts(dropna=False)

working_2['case_indicator'][working_2['isolated_CABG']==1].value_counts(dropna=False)
working_2['PAC_intraop_exp'][working_2['isolated_CABG']==1].value_counts(dropna=False)
working_2['TEE_intraop_exp'][working_2['isolated_CABG']==1].value_counts(dropna=False)

working_2['case_indicator'][working_2['isolated_CABG']==0].value_counts(dropna=False)
working_2['PAC_intraop_exp'][working_2['isolated_CABG']==0].value_counts(dropna=False)
working_2['TEE_intraop_exp'][working_2['isolated_CABG']==0].value_counts(dropna=False)

#%%
working_2['TEE_plus_PAC'] = (working_2['PAC_intraop_exp']==1) & (working_2['TEE_intraop_exp']==1) # TEE plus PAC monitoring profile
working_2['TEE_plus_PAC'].value_counts(dropna=False) # 81186

working_2['TEE_only'] = (working_2['PAC_intraop_exp']==0) & (working_2['TEE_intraop_exp']==1) # TEE without PAC monitoring profile 
working_2['TEE_only'].value_counts(dropna=False) #29115

working_2['PAC_only'] = (working_2['PAC_intraop_exp']==1) & (working_2['TEE_intraop_exp']==0) # PAC without TEE monitoring profile 
working_2['PAC_only'].value_counts(dropna=False) # 23440

working_2['no_TEE_no_PAC'] = (working_2['PAC_intraop_exp']==0) & (working_2['TEE_intraop_exp']==0) # Neither TEE nor PAC monitoring profile 
working_2['no_TEE_no_PAC'].value_counts(dropna=False) # 11602

#%%
# sanity check
81186 + 29115 + 23440 + 11602 # 145343
working_2['case_indicator'].value_counts(dropna=False) # inclusion count
# 
81186/145343
29115/145343
23440/145343
11602/145343

#%%
# tee data visualization 
tee_rate_fig = working_2[['Case_Date_yr', 'Institution', 'tee_rate_yr']]
tee_rate_fig.drop_duplicates(inplace=True)
tee_rate_fig.astype({"Case_Date_yr": 'str', "Institution": 'str'}) 
print() 
#%%
# pivot the data 
tee_pivot = tee_rate_fig.pivot(index='Case_Date_yr', columns='Institution', values='tee_rate_yr')
# check
tee_pivot.head()
#%%
# pivot_table the data
tee_pivot_table = tee_rate_fig.pivot_table(
    index=['Case_Date_yr'], 
    columns=['Institution'], 
    values=['tee_rate_yr'])
# check
tee_pivot_table.head()
tee_pivot_table.reset_index()

#%%
# matplotlib: line plot
tee_pivot.plot(figsize=(20,10))
tee_pivot.plot(figsize=(40,10))
#%%
# pandas: area plot
ax = tee_pivot.plot.area(figsize=(50,20))
ax = tee_pivot.plot.area(figsize=(30,10))
plt.savefig("tee_hosp_area.svg", format="svg")

#%%
# pac data visualization 
pac_rate_fig = working_2[['Case_Date_yr', 'Institution', 'pac_rate_yr']]
pac_rate_fig.drop_duplicates(inplace=True)
pac_rate_fig.astype({"Case_Date_yr": 'str', "Institution": 'str'}) 
#%%
# pivot the data 
pac_pivot = pac_rate_fig.pivot(index='Case_Date_yr', columns='Institution', values='pac_rate_yr')
# check
pac_pivot.head()
# pivot_table the data
pac_pivot_table = pac_rate_fig.pivot_table(
    index=['Case_Date_yr'], 
    columns=['Institution'], 
    values=['pac_rate_yr'])
# check
pac_pivot_table.head()
pac_pivot_table.reset_index()

#%%
# matplotlib: line plot
pac_pivot.plot(figsize=(20,10))
pac_pivot.plot(figsize=(40,10))
#%%
# pandas: area plot
ax = pac_pivot.plot.area(figsize=(50,20))
ax = pac_pivot.plot.area(figsize=(30,10))
plt.savefig("pac_hosp_area.svg", format="svg")


#%%
# look at hospital surgical volume more closely 
vol = working_2[['Institution', 'Case_Date_yr', 'case_count_tot_cum', 'tee_rate', 'pac_rate', 'case_count_tot_yr', 'tee_rate_yr', 'pac_rate_yr', 'case_count_tot_yr_mo']]

#%%
# generate the validation dataset 
val = working_2[['MPOG_Case_ID', 'Institution', 'Case_Date_yr', 'TEE_intraop_exp', 'PAC_intraop_exp', 'pac_ind_s', 'pac_ind_d', 'pac_ind_m']]

#%%
# clean up working_2 dataset
working_2.dtypes
working_2.drop(list(working_2.filter(regex='_merge')), axis=1, inplace=True) # regex column drop option 
working_2.dtypes

working_2.drop(columns=['exclude_surg_vol', 'exclude_missing_starting_anes_attd', 'exclude_missing_emergency_status', 'exclude_missing_surg_cat', 'exclude_cpb_time_under_20', 'exclude_aborted_surg_cat', 'exclude_chest_expl_or_close', 'exclude_arrived_intub'], inplace=True) # python drop option by listing out columns
working_2.dtypes

#%%

#%% 
# data visualization case counts - bar and line charts 
# bar plot for hemodynamic profile(s) 
# color styles 
plt.style.use('default') # resets style to default
list(plt.style.available)

80134/143321
28752/143321
23179/143321
11256/143321

hf = pd.DataFrame({'hemo_profile':['TEE_plus_PAC', 'TEE_only', 'PAC_only', 'no_TEE_no_PAC'], 'rate':[.56, .20, .16, .08]})
ax = hf.plot.bar(x='hemo_profile', y='rate', rot=0)

# create data
x_hemo_p = ['hemo_profile']
y_rate_1 = np.array([.56])
y_rate_2 = np.array([.20])
y_rate_3 = np.array([.16])
y_rate_4 = np.array([.08])

#%%
plt.style.use('default') # resets style to default
plt.bar(x_hemo_p, y_rate_1, color='olivedrab')
plt.bar(x_hemo_p, y_rate_2, bottom=y_rate_1, color='darkorange')
plt.bar(x_hemo_p, y_rate_3, bottom=y_rate_1+y_rate_2, color='cornflowerblue')
plt.bar(x_hemo_p, y_rate_4, bottom=y_rate_1+y_rate_2+y_rate_3, color='dimgrey')
plt.xlabel("hemodynamic profile")
plt.ylabel("rate")
plt.legend(["TEE + PAC", "TEE only", "PAC only", "No TEE No PAC"], fontsize='x-small')
plt.title("Rates of Hemodynamic Monitoring Profile")
plt.savefig("hemo_profile_stacked_a.svg", format="svg")
plt.show()


#%%
plt.style.use('tableau-colorblind10')
plt.rcParams["figure.figsize"] = (5,5)
plt.bar(x_hemo_p, y_rate_1, alpha=0.8, width=0.2)
plt.bar(x_hemo_p, y_rate_2, bottom=y_rate_1, alpha=0.8, width=0.2)
plt.bar(x_hemo_p, y_rate_3, bottom=y_rate_1+y_rate_2, alpha=0.8, width=0.2)
plt.bar(x_hemo_p, y_rate_4, bottom=y_rate_1+y_rate_2+y_rate_3, alpha=0.8, width=0.2)
plt.xlabel("hemodynamicprofile", fontsize='small')
plt.ylabel("rate", fontsize='small')
plt.legend(["TEE + PAC", "TEE only", "PAC only", "No TEE No PAC"])
plt.title("Rates of Hemodynamic Monitoring Profile")
plt.savefig("hemo_profile_stacked_b.svg", format="svg")
plt.show()

#%%
# manual creation of dataframe
df = pd.DataFrame({"a": [0, 1], "b": [1, 1]})
# note - double click on data viewer to view it
print(df)

#%%
# save file(s) as .csv 
# val.to_csv(os.path.join(dirname, "validation_dataset_2024_06_05.csv"), index=False)
# working_2.to_csv(os.path.join(dirname, "clean_dataset_2024_06_05.csv"), index=False)



