* setup  
set more off
set linesize 255

* log file setup
* local file_name = "characteristics"
* local path = "/<path>/" 
* log using "`path'`file_name'.txt", replace text name("glmm")
log using "characteristics.log", replace

* data preparation 
* import file with race data
import delimited "/PCRC 094 MacKay/data/PCRC_0094_CaseInfo_120723b.csv", clear
* create a dta dataset with only Race and mpog case id 
keep mpog_case_id race 
* export/save race dataset 
save "/PCRC 094 MacKay/stata/race_data_2025_04_24.dta", replace  
* import clean dataset 
import delimited "/PCRC 094 MacKay/clean_dataset_2024_06_05.csv", clear
* export clean dataset to .dta for merging
save "/PCRC 094 MacKay/stata/clean_with_race_2025_04_24.dta", replace  
* load race file 
use race_data_2025_04_24.dta, clear 
* merge master dataset 
merge 1:1 mpog_case_id using clean_with_race_2025_04_24.dta
* drop the unmatched (already excluded) observations
drop if _merge == 1
count
* drop temporary merge variable 
drop _merge 

* make sure correct packages are installed 
ssc install outreg2
ssc install multencode
ssc install randomselect

* GLMM data setup 
* encode categoricals 
tostring institution, replace
encode institution, gen(institution_e)
encode sex, gen(sex_e)
encode race, gen(race_e)
tostring asa_class, replace
encode asa_class, gen(asa_class_e)
encode weekend, gen(weekend_e)
encode emergency_status, gen(emergency_status_e)
encode arrived_intubated, gen(arrived_intubated_e)
encode starting_provider_anes_attending, gen(starting_provider_anes_att_e)

encode cabg, gen(cabg_e)
encode mitral, gen(mitral_e)
encode mv_repair, gen(mv_repair_e)
encode mv_replace, gen(mv_replace_e)
encode tricuspid, gen(tricuspid_e)
encode tv_repair, gen(tv_repair_e)
encode tv_replace, gen(tv_replace_e)
encode pulmonic, gen(pulmonic_e)
encode pv_repair, gen(pv_repair_e)
encode pv_replace, gen(pv_replace_e)
encode pulm_homograft, gen(pulm_homograft_e)
encode ross, gen(ross_e)
encode aortic_v, gen(aortic_v_e)
encode avss_av_repair, gen(avss_av_repair_e)
encode av_replace, gen(av_replace_e)
encode aortic_prox, gen(aortic_prox_e)
encode aortic_desc, gen(aortic_desc_e)
encode lung_tx, gen(lung_tx_e)
encode heart_tx, gen(heart_tx_e)
encode lvad, gen(lvad_e)
encode rvad, gen(rvad_e)
encode pulm_endart, gen(pulm_endart_e)
encode structural, gen(structural_e)
encode redo, gen(redo_e)
encode isolated_cabg, gen(isolated_cabg_e)

foreach v of var elix_*{
            multencode `v', gen(`v'_e)
        }
		
encode comorbid_mpog_cvd, gen(comorbid_mpog_cvd_e)
encode comorbid_mpog_cad, gen(comorbid_mpog_cad_e)


* generate binary 1 vs 0 categoricals 
generate starting_crna = cond((starting_provider_crna == ""), 0, 1)
generate starting_res = cond((starting_provider_anes_resident == ""), 0, 1)

* exposure(s)
generate tee_intraop_exp_b = cond((tee_intraop_exp == "True"), 1, 0)
generate pac_intraop_exp_b = cond((pac_intraop_exp == "True"), 1, 0)

encode tee_intraop_exp, gen(tee_intraop_exp_e)
encode pac_intraop_exp, gen(pac_intraop_exp_e)

generate tee_plus_pac_b = cond((tee_plus_pac == "True"), 1, 0)
generate tee_only_b = cond((tee_only == "True"), 1, 0)
generate pac_only_b = cond((pac_only == "True"), 1, 0)
generate no_tee_no_pac_b = cond((no_tee_no_pac == "True"), 1, 0)

generate hemo_profile = " "
replace hemo_profile = "tee + pac" if tee_plus_pac == "True"
replace hemo_profile = "tee" if tee_only == "True"
replace hemo_profile = "pac" if pac_only == "True"
replace hemo_profile = "neither" if no_tee_no_pac == "True"
encode hemo_profile, gen(hemo_profile_e)

* binary classifiers

* format date columns
generate date = date(case_date, "YMD hms")
format date %td
generate month = month(date)
generate year = year(date)

* surgical volume
* issue - not every hospital has cases every year -- instead of bucketing when many hospitals will have zero -- divide case_count_tot_yr by 10 [reference Table 2 Chen et al NEJM cataract paper]
tab institution_e case_date_yr
summarize case_count_tot_yr, detail
generate surgical_vol_div_10 = case_count_tot_yr/10 

* hospital-level tee rate categories
summarize tee_rate, detail
generate high_tee_inst = cond((tee_rate >= .8611982), 1, 0)
generate low_tee_inst = cond((tee_rate < .8611982), 1, 0)

* hospital-level pac rate categories
summarize pac_rate, detail
generate high_pac_inst = cond((pac_rate >= .7978817), 1, 0)
generate low_pac_inst = cond((pac_rate < .7978817), 1, 0)

* generate variable that captures hospital with data crossing all years 
generate hosp_cross_all_yrs = cond((institution == "88" | institution == "89" | institution == "86" | institution == "84" | institution == "83" | institution == "78" | institution == "75" | institution == "70" | institution == "7" | institution == "69" | institution == "68" | institution == "66" | institution == "64" | institution == "58" | institution == "57" | institution == "53" | institution == "5" | institution == "40" | institution == "4" | institution == "36" | institution == "35" | institution == "23" | institution == "19" | institution == "14"), 1, 0)
tab hosp_cross_all_yrs

* anesthesiologist-level TEE and PAC rate data?
egen tee_rate_provider_yr = mean(tee_intraop_exp_b), by (starting_provider_anes_att_e case_date_yr)
egen tee_rate_provider = mean(tee_intraop_exp_b), by (starting_provider_anes_att_e)

egen pac_rate_provider_yr = mean(pac_intraop_exp_b), by (starting_provider_anes_att_e case_date_yr)
egen pac_rate_provider = mean(pac_intraop_exp_b), by (starting_provider_anes_att_e)

* condition on anesthesiologists caring for at least 5 patients
egen anes_case_count = count(case_indicator), by (starting_provider_anes_att_e)
generate anes_cases_over_10 = cond((anes_case_count >10), 1, 0)

* primary provider surgeon data 
encode primary_provider_surg_attending, gen(primary_provider_surg_att_e)
generate surgeon_missing = . 
replace surgeon_missing = cond((primary_provider_surg_attending == ""), 1, 0) 

//////////////////////////////////////////////////////

* Descriptive Statistics: PAC

//////////////////////////////////////////////////////

* PAC vs no PAC
tabulate pac_intraop_exp

* descriptive statistics: PAC 
mtable set characteristics_pac

ttest case_indicator, by(pac_intraop_exp_e)
mtable "ttest" case_indicator "case" 

ttest age_in_years, by(pac_intraop_exp_e)
mtable "ttest" age_in_years "age"

ttest bmi, by(pac_intraop_exp_e)
mtable "ttest" bmi "bmi"

ttest weight_kg, by(pac_intraop_exp_e)
mtable "ttest" weight_kg "weight_kg"

tabulate sex_e pac_intraop_exp_e, chi2 expected miss column matcell(values) matrow(names)f
mtable "tabulate" sex_e "sex"

tabulate race_e pac_intraop_exp_e, chi2 expected miss column matcell(values) matrow(names)f
mtable "tabulate" race_e "race"

tabulate asa_class_e pac_intraop_exp_e, chi2 expected miss column matcell(values) matrow(names)
mtable "tabulate" asa_class "ASA"

ttest case_count_tot_yr, by(pac_intraop_exp_e)
mtable "ttest" case_count_tot_cum "yearly_srg_vol"

tabulate high_tee_inst pac_intraop_exp_e, chi2 expected miss column matcell(values) matrow(names)
mtable "tabulate" high_tee_inst "high_tee_inst"

tabulate high_pac_inst pac_intraop_exp_e, chi2 expected miss column matcell(values) matrow(names)
mtable "tabulate" high_pac_inst "high_pac_inst"

tabulate weekend_e pac_intraop_exp_e, chi2 expected miss column matcell(values) matrow(names)
mtable "tabulate" weekend_e "weekend"

tabulate starting_crna pac_intraop_exp_e, chi2 expected miss column matcell(values) matrow(names)
mtable "tabulate" starting_crna "CRNA_start"

tabulate starting_res pac_intraop_exp_e, chi2 expected miss column matcell(values) matrow(names)
mtable "tabulate" starting_res "Res_start"

tabulate emergency_status_e pac_intraop_exp_e, chi2 expected miss column matcell(values) matrow(names)
mtable "tabulate" emergency_status_e "emergency"

ttest preop_albumin_imp, by(pac_intraop_exp_e)
mtable "ttest" preop_albumin_imp "albumin"

ttest preop_bun_imp, by(pac_intraop_exp_e)
mtable "ttest" preop_bun_imp "BUN"

ttest preop_potassium_imp, by(pac_intraop_exp_e)
mtable "ttest" preop_potassium_imp "K+"

ttest preop_hgb_a1c_imp, by(pac_intraop_exp_e)
mtable "ttest" preop_hgb_a1c_imp "Hgb_A1c"

ttest preop_glucose_imp, by(pac_intraop_exp_e)
mtable "ttest" preop_glucose_imp "glucose"

ttest preop_hemoglobin_imp, by(pac_intraop_exp_e)
mtable "ttest" preop_hemoglobin_imp "Hgb"

ttest preop_inr_imp, by(pac_intraop_exp_e)
mtable "ttest" preop_inr_imp "INR"

ttest preop_platelets_imp, by(pac_intraop_exp_e)
mtable "ttest" preop_platelets_imp "plts"

tabulate elix_cardiac_arrhythmia_e pac_intraop_exp_e, chi2 expected miss column matcell(values) matrow(names)
mtable "tabulate" elix_cardiac_arrhythmia_e "arrhythmia"

tabulate elix_chronic_pulmonary_e pac_intraop_exp_e, chi2 expected miss column matcell(values) matrow(names)
mtable "tabulate" elix_chronic_pulmonary_e "pulm"

tabulate elix_chf_e pac_intraop_exp_e, chi2 expected miss column matcell(values) matrow(names)
mtable "tabulate" elix_chf_e "chf"

tabulate elix_pvd_e pac_intraop_exp_e, chi2 expected miss column matcell(values) matrow(names)
mtable "tabulate" elix_pvd_e "pvd"

tabulate elix_pulm_circ_e pac_intraop_exp_e, chi2 expected miss column matcell(values) matrow(names)
mtable "tabulate" elix_pulm_circ_e "pulm_circ"

tabulate elix_valvular_e pac_intraop_exp_e, chi2 expected miss column matcell(values) matrow(names)
mtable "tabulate" elix_valvular_e "valvular"

tabulate comorbid_mpog_cvd_e pac_intraop_exp_e, chi2 expected miss column matcell(values) matrow(names)
mtable "tabulate" comorbid_mpog_cvd_e "cvd"

tabulate comorbid_mpog_cad_e pac_intraop_exp_e, chi2 expected miss column matcell(values) matrow(names)
mtable "tabulate" comorbid_mpog_cad_e "cad"

tabulate isolated_cabg_e pac_intraop_exp_e, chi2 expected miss column matcell(values) matrow(names)
mtable "tabulate" isolated_cabg_e "isolated_cabg"

tabulate cabg_e pac_intraop_exp_e, chi2 expected miss column matcell(values) matrow(names)
mtable "tabulate" cabg_e "cabg"

tabulate mv_repair_e pac_intraop_exp_e, chi2 expected miss column matcell(values) matrow(names)
mtable "tabulate" mv_repair_e "mv_repair"

tabulate mv_replace_e pac_intraop_exp_e, chi2 expected miss column matcell(values) matrow(names)
mtable "tabulate" mv_replace_e "mv_replace"

tabulate tricuspid_e pac_intraop_exp_e, chi2 expected miss column matcell(values) matrow(names)
mtable "tabulate" tricuspid_e "tricuspid"

tabulate pulmonic_e pac_intraop_exp_e, chi2 expected miss column matcell(values) matrow(names)
mtable "tabulate" pulmonic_e "pulmonic"

tabulate av_replace_e pac_intraop_exp_e, chi2 expected miss column matcell(values) matrow(names)
mtable "tabulate" av_replace_e "av_replace"

tabulate avss_av_repair_e pac_intraop_exp_e, chi2 expected miss column matcell(values) matrow(names)
mtable "tabulate" avss_av_repair_e "avss_av_repair"

tabulate aortic_prox_e pac_intraop_exp_e, chi2 expected miss column matcell(values) matrow(names)
mtable "tabulate" aortic_prox_e "aortic_prox"

tabulate aortic_desc_e pac_intraop_exp_e, chi2 expected miss column matcell(values) matrow(names)
mtable "tabulate" aortic_desc_e "aortic_desc"

tabulate lung_tx_e pac_intraop_exp_e, chi2 expected miss column matcell(values) matrow(names)
mtable "tabulate" lung_tx_e "lung_tx"

tabulate heart_tx_e pac_intraop_exp_e, chi2 expected miss column matcell(values) matrow(names)
mtable "tabulate" heart_tx_e "heart_tx"

tabulate redo_e pac_intraop_exp_e, chi2 expected miss column matcell(values) matrow(names)
mtable "tabulate" redo_e "redo"

//////////////////////////////////////////////////////

* Data Visualizations 

//////////////////////////////////////////////////////

* Data visualizations
* color scheme options
graph query, schemes
* select color scheme
* reset to default factory schemes
set scheme s2color

* graph results of a tabulated categorical variable
graph bar (count), over(hemo_profile)
graph bar (percent), over(hemo_profile)

graph hbar (percent), over(hemo_profile) ///
	title("Frequency of Hemodynamic Monitoring Profile") ///
	blabel(bar, size(medium) color(black) format(%9.1f))

* TEE & PAC rates by hospital
twoway (kdensity tee_rate, color(green*.8) ) (kdensity pac_rate, color(blue*.5)), legend(label(1 "TEE") label(2 "PAC")) xtitle("Probability of Hemodynamic Monitor (TEE or PAC) by Hospital") ytitle("Density")

* TEE & PAC rates by anesthesiologist
twoway (kdensity tee_rate_provider_yr, color(green*.8) ) (kdensity pac_rate_provider_yr, color(blue*.5)), legend(label(1 "TEE") label(2 "PAC")) xtitle("Probability of Hemodynamic Monitor (TEE or PAC) by Anesthesiologist") ytitle("Density")



/////////////////////////////////////////////////////////////////////////////

* create dataset with only variables for glmm 
keep mpog_case_id case_date_yr_mo_d case_date_yr_mo case_date_yr institution case_indicator case_count_tot_cum case_count_tot_yr case_count_tot_yr_mo tee_intraop_exp_b pac_intraop_exp_b high_tee_inst high_pac_inst surgical_vol_div_10 age_in_years sex_e race_e bmi asa_class_e weekend_e starting_crna starting_res emergency_status_e elix_cardiac_arrhythmia_e elix_chronic_pulmonary_e elix_chf_e elix_pvd_e elix_valvular_e comorbid_mpog_cvd_e comorbid_mpog_cad_e preop_bun_imp preop_potassium_imp preop_hgb_a1c_imp preop_inr_imp preop_hemoglobin_imp isolated_cabg_e cabg_e  mv_repair_e mv_replace_e tricuspid_e pulmonic_e av_replace_e avss_av_repair_e aortic_prox_e lung_tx_e heart_tx_e redo_e institution_e starting_provider_anes_att_e


/////////////////////////////////////////////////////////////////////////////
* export truncated dataset(s) (one in .dta format and a copy in .csv format) for glmm
save "/PCRC 094 MacKay/dataset_for_glmm_2025_05_22.dta", replace  
export delimited "/PCRC 094 MacKay/dataset_for_glmm_2025_05_22.csv", replace  

/*
*/ 

log close _all



