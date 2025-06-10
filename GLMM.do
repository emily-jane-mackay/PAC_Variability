
* setup  
set more off
set linesize 255

* log file setup
* local file_name = "glmm"
* local path = "/<path>/" 
* log using "`path'`file_name'.txt", replace text name("glmm")
log using "3-level_glmm.log", replace

* import data 
use "/<data.dta>", clear  

/////////////////////////////////////////////////////////////////////////////

// setup for selecting random samples in order run three-level model
di 145343/8
di (18168*7) + 18167

ssc install randomselect
set seed 273400
randomselect, gen(rando_1) n(18167)

set seed 04856
randomselect if rando_1 != 1 , gen(rando_2) n(18168)

set seed 7772039
randomselect if rando_1 != 1 & rando_2 != 1, gen(rando_3) n(18168)

set seed 7738205
randomselect if rando_1 != 1 & rando_2 != 1 & rando_3 != 1, gen(rando_4) n(18168)

set seed 112990403
randomselect if rando_1 != 1 & rando_2 != 1 & rando_3 != 1 & rando_4 != 1, gen(rando_5) n(18168)

set seed 283990
randomselect if rando_1 != 1 & rando_2 != 1 & rando_3 != 1 & rando_4 != 1 & rando_5 ! = 1, gen(rando_6) n(18168)

set seed 11100330
randomselect if rando_1 != 1 & rando_2 != 1 & rando_3 != 1 & rando_4 != 1 & rando_5 ! = 1 & rando_6 != 1, gen(rando_7) n(18168)

set seed 5564739
generate rando_8 = rando_1 != 1 & rando_2 != 1 & rando_3 != 1 & rando_4 != 1 & rando_5 ! = 1 & rando_6 != 1 & rando_7 != 1


// setup for selecting 4 random samples in order to check the 8 random samples 
di 145343/4
di (36336*3) + 36335

set seed 777320
randomselect, gen(rando_1a) n(36336)

set seed 19284
randomselect if rando_1a != 1 , gen(rando_2a) n(36336)

set seed 73225
randomselect if rando_1a != 1 & rando_2a != 1, gen(rando_3a) n(36336)

set seed 88335
generate rando_4a = rando_1a != 1 & rando_2a != 1 & rando_3a != 1 

tab rando_4a rando_1a

/////////////////////////////////////////////////////////////////////////////

* PAC: model 0: null model - anesthesiologist only: 4 random samples

/////////////////////////////////////////////////////////////////////////////

melogit pac_intraop_exp_b if rando_1a == 1, || starting_provider_anes_att_e:, or 
estimates store null_a_1a
melogit pac_intraop_exp_b if rando_2a == 1, || starting_provider_anes_att_e:, or 
estimates store null_a_2a
melogit pac_intraop_exp_b if rando_3a == 1, || starting_provider_anes_att_e:, or 
estimates store null_a_3a
melogit pac_intraop_exp_b if rando_4a == 1, || starting_provider_anes_att_e:, or 
estimates store null_a_4a
* estimates directory 
estimates dir
* code to clear estimates "estimates clear" 

* null model 
estimates replay null_a_1a
matrix list r(table)
gen odds_1a = (r(table)["b", "/:var(_cons[starting_provider_anes_att_e])"])
gen odds_1a_ll = (r(table)["ll", "/:var(_cons[starting_provider_anes_att_e])"])
gen odds_1a_ul = (r(table)["ul", "/:var(_cons[starting_provider_anes_att_e])"])
estimates replay null_a_1a
estat icc 
return list 
gen icc_1a = (r(icc2))

* null model 
estimates replay null_a_2a
matrix list r(table)
gen odds_2a = (r(table)["b", "/:var(_cons[starting_provider_anes_att_e])"])
gen odds_2a_ll = (r(table)["ll", "/:var(_cons[starting_provider_anes_att_e])"])
gen odds_2a_ul = (r(table)["ul", "/:var(_cons[starting_provider_anes_att_e])"])
estimates replay null_a_2a
estat icc 
return list 
gen icc_2a = (r(icc2))


* null model 
estimates replay null_a_3a
matrix list r(table)
gen odds_3a = (r(table)["b", "/:var(_cons[starting_provider_anes_att_e])"])
gen odds_3a_ll = (r(table)["ll", "/:var(_cons[starting_provider_anes_att_e])"])
gen odds_3a_ul = (r(table)["ul", "/:var(_cons[starting_provider_anes_att_e])"])
estimates replay null_a_3a
estat icc 
return list 
gen icc_3a = (r(icc2))


* null model 
estimates replay null_a_4a
matrix list r(table)
gen odds_4a = (r(table)["b", "/:var(_cons[starting_provider_anes_att_e])"])
gen odds_4a_ll = (r(table)["ll", "/:var(_cons[starting_provider_anes_att_e])"])
gen odds_4a_ul = (r(table)["ul", "/:var(_cons[starting_provider_anes_att_e])"])
estimates replay null_a_4a
estat icc 
return list 
gen icc_4a = (r(icc2))


* averages
gen mean_odds = (odds_1a + odds_2a + odds_3a + odds_4a)/4
gen mean_odds_ll = (odds_1a_ll + odds_2a_ll + odds_3a_ll + odds_4a_ll)/4
gen mean_odds_ul = (odds_1a_ul + odds_2a_ul + odds_3a_ul + odds_4a_ul)/4
gen icc = (icc_1a + icc_2a + icc_3a + icc_4a)/4

* MOR calculations 
gen mor = exp(0.95 * sqrt(mean_odds))
gen mor_ll = exp(0.95 * sqrt(mean_odds_ll))
gen mor_ul = exp(0.95 * sqrt(mean_odds_ul))
* Sigma calculations 
gen sigma = sqrt(mean_odds)
gen sigma_ll = sqrt(mean_odds_ll)
gen sigma_ul = sqrt(mean_odds_ul)


* putexcel 
putexcel set "mor_sigma_2025_05_22.xls", replace
putexcel A1 = ("variable") B1 = ("MOR") C1 = ("MOR 95% CI: ll") D1 = ("MOR 95% CI: ul") E1 = ("sigma") F1 = ("sigma 95% CI ll") G1 = ("sigma 95% CI: ul") H1 = "ICC"
putexcel A2 = "model 0: anesthesiologist"
putexcel A3 = "---"
putexcel A4 = "starting_provider_anes_att_e"
summarize mor 
return list 
putexcel B4 = (r(mean))
summarize mor_ll
putexcel C4 = (r(mean))
summarize mor_ul
putexcel D4 = (r(mean))
summarize sigma 
return list 
putexcel E4 = (r(mean))
summarize sigma_ll
putexcel F4 = (r(mean))
summarize sigma_ul
putexcel G4 = (r(mean))
summarize icc 
putexcel H4 = (r(mean))


* drop temporary variables to reuse 
drop icc* mor* sigma* odds* mean*

/////////////////////////////////////////////////////////////////////////////

* PAC: model 0: null model - hospital only: 4 random samples

/////////////////////////////////////////////////////////////////////////////

melogit pac_intraop_exp_b if rando_1a == 1, || institution_e:, or 
estimates store null_h_1a
melogit pac_intraop_exp_b if rando_2a == 1, || institution_e:, or 
estimates store null_h_2a
melogit pac_intraop_exp_b if rando_3a == 1, || institution_e:, or 
estimates store null_h_3a
melogit pac_intraop_exp_b if rando_4a == 1, || institution_e:, or 
estimates store null_h_4a
* estimates directory 
estimates dir

* null model 
estimates replay null_h_1a
matrix list r(table)
gen odds_1a = (r(table)["b", "/:var(_cons[institution_e])"])
gen odds_1a_ll = (r(table)["ll", "/:var(_cons[institution_e])"])
gen odds_1a_ul = (r(table)["ul", "/:var(_cons[institution_e])"])
estimates replay null_h_1a
estat icc 
return list 
gen icc_1a = (r(icc2))

* null model 
estimates replay null_h_2a
matrix list r(table)
gen odds_2a = (r(table)["b", "/:var(_cons[institution_e])"])
gen odds_2a_ll = (r(table)["ll", "/:var(_cons[institution_e])"])
gen odds_2a_ul = (r(table)["ul", "/:var(_cons[institution_e])"])
estimates replay null_h_2a
estat icc 
return list 
gen icc_2a = (r(icc2))

* null model 
estimates replay null_h_3a
matrix list r(table)
gen odds_3a = (r(table)["b", "/:var(_cons[institution_e])"])
gen odds_3a_ll = (r(table)["ll", "/:var(_cons[institution_e])"])
gen odds_3a_ul = (r(table)["ul", "/:var(_cons[institution_e])"])
estimates replay null_h_3a
estat icc 
return list 
gen icc_3a = (r(icc2))

* null model 
estimates replay null_h_4a
matrix list r(table)
gen odds_4a = (r(table)["b", "/:var(_cons[institution_e])"])
gen odds_4a_ll = (r(table)["ll", "/:var(_cons[institution_e])"])
gen odds_4a_ul = (r(table)["ul", "/:var(_cons[institution_e])"])
estimates replay null_h_4a
estat icc 
return list 
gen icc_4a = (r(icc2))

* averages
gen mean_odds = (odds_1a + odds_2a + odds_3a + odds_4a)/4
gen mean_odds_ll = (odds_1a_ll + odds_2a_ll + odds_3a_ll + odds_4a_ll)/4
gen mean_odds_ul = (odds_1a_ul + odds_2a_ul + odds_3a_ul + odds_4a_ul)/4
gen icc = (icc_1a + icc_2a + icc_3a + icc_4a)/4

* MOR calculations 
gen mor = exp(0.95 * sqrt(mean_odds))
gen mor_ll = exp(0.95 * sqrt(mean_odds_ll))
gen mor_ul = exp(0.95 * sqrt(mean_odds_ul))
* Sigma calculations 
gen sigma = sqrt(mean_odds)
gen sigma_ll = sqrt(mean_odds_ll)
gen sigma_ul = sqrt(mean_odds_ul)


* putexcel 
putexcel set "mor_sigma_2025_05_22.xls", modify 
putexcel A6 = "model 0: hospitals"
putexcel A7 = "---"
putexcel A8 = "institution_e"
summarize mor 
return list 
putexcel B8 = (r(mean))
summarize mor_ll
putexcel C8 = (r(mean))
summarize mor_ul
putexcel D8 = (r(mean))
summarize sigma 
return list 
putexcel E8 = (r(mean))
summarize sigma_ll
putexcel F8 = (r(mean))
summarize sigma_ul
putexcel G8 = (r(mean))
summarize icc 
putexcel H8 = (r(mean))


* drop temporary variables to reuse 
drop icc* mor* sigma* odds* mean*


/////////////////////////////////////////////////////////////////////////////

* PAC: model 0: null model - anesthesiologists nested in hospitals: 4 random samples

/////////////////////////////////////////////////////////////////////////////

melogit pac_intraop_exp_b if rando_1a == 1, || institution_e: || starting_provider_anes_att_e:, or 
estimates store null_ha_1a
melogit pac_intraop_exp_b if rando_2a == 1, || institution_e: || starting_provider_anes_att_e:, or 
estimates store null_ha_2a
melogit pac_intraop_exp_b if rando_3a == 1, || institution_e: || starting_provider_anes_att_e:, or 
estimates store null_ha_3a
melogit pac_intraop_exp_b if rando_4a == 1, || institution_e: || starting_provider_anes_att_e:, or 
estimates store null_ha_4a
* estimates directory 
estimates dir

* null model: 3-level 
estimates replay null_ha_1a
matrix list r(table)
gen odds_1a = (r(table)["b", "/:var(_cons[institution_e])"])
gen odds_1a_ll = (r(table)["ll", "/:var(_cons[institution_e])"])
gen odds_1a_ul = (r(table)["ul", "/:var(_cons[institution_e])"])
gen odds_1a_next = (r(table)["b", "/:var(_cons[institution_e>starting_provider_anes_att_e])"])
gen odds_1a_ll_next = (r(table)["ll", "/:var(_cons[institution_e>starting_provider_anes_att_e])"])
gen odds_1a_ul_next = (r(table)["ul", "/:var(_cons[institution_e>starting_provider_anes_att_e])"])
estimates replay null_ha_1a
estat icc 
return list 
gen icc_1a_inst = (r(icc3))
gen icc_1a_an_inst = (r(icc2))

* null model: 3-level 
estimates replay null_ha_2a
matrix list r(table)
gen odds_2a = (r(table)["b", "/:var(_cons[institution_e])"])
gen odds_2a_ll = (r(table)["ll", "/:var(_cons[institution_e])"])
gen odds_2a_ul = (r(table)["ul", "/:var(_cons[institution_e])"])
gen odds_2a_next = (r(table)["b", "/:var(_cons[institution_e>starting_provider_anes_att_e])"])
gen odds_2a_ll_next = (r(table)["ll", "/:var(_cons[institution_e>starting_provider_anes_att_e])"])
gen odds_2a_ul_next = (r(table)["ul", "/:var(_cons[institution_e>starting_provider_anes_att_e])"])
estimates replay null_ha_2a
estat icc 
return list 
gen icc_2a_inst = (r(icc3))
gen icc_2a_an_inst = (r(icc2))

* null model: 3-level 
estimates replay null_ha_3a
matrix list r(table)
gen odds_3a = (r(table)["b", "/:var(_cons[institution_e])"])
gen odds_3a_ll = (r(table)["ll", "/:var(_cons[institution_e])"])
gen odds_3a_ul = (r(table)["ul", "/:var(_cons[institution_e])"])
gen odds_3a_next = (r(table)["b", "/:var(_cons[institution_e>starting_provider_anes_att_e])"])
gen odds_3a_ll_next = (r(table)["ll", "/:var(_cons[institution_e>starting_provider_anes_att_e])"])
gen odds_3a_ul_next = (r(table)["ul", "/:var(_cons[institution_e>starting_provider_anes_att_e])"])
estimates replay null_ha_3a
estat icc 
return list 
gen icc_3a_inst = (r(icc3))
gen icc_3a_an_inst = (r(icc2))

* null model: 3-level 
estimates replay null_ha_4a
matrix list r(table)
gen odds_4a = (r(table)["b", "/:var(_cons[institution_e])"])
gen odds_4a_ll = (r(table)["ll", "/:var(_cons[institution_e])"])
gen odds_4a_ul = (r(table)["ul", "/:var(_cons[institution_e])"])
gen odds_4a_next = (r(table)["b", "/:var(_cons[institution_e>starting_provider_anes_att_e])"])
gen odds_4a_ll_next = (r(table)["ll", "/:var(_cons[institution_e>starting_provider_anes_att_e])"])
gen odds_4a_ul_next = (r(table)["ul", "/:var(_cons[institution_e>starting_provider_anes_att_e])"])
estimates replay null_ha_4a
estat icc 
return list 
gen icc_4a_inst = (r(icc3))
gen icc_4a_an_inst = (r(icc2))

* averages
gen mean_odds = (odds_1a + odds_2a + odds_3a + odds_4a)/4
gen mean_odds_ll = (odds_1a_ll + odds_2a_ll + odds_3a_ll + odds_4a_ll)/4
gen mean_odds_ul = (odds_1a_ul + odds_2a_ul + odds_3a_ul + odds_4a_ul)/4
gen mean_odds_next = (odds_1a_next + odds_2a_next + odds_3a_next + odds_4a_next)/4
gen mean_odds_ll_next = (odds_1a_ll_next + odds_2a_ll_next + odds_3a_ll_next + odds_4a_ll_next)/4
gen mean_odds_ul_next = (odds_1a_ul_next + odds_2a_ul_next + odds_3a_ul_next + odds_4a_ul_next)/4
gen icc_inst = (icc_1a_inst + icc_2a_inst + icc_3a_inst + icc_4a_inst)/4
gen icc_an_inst = (icc_1a_an_inst + icc_2a_an_inst + icc_3a_an_inst + icc_4a_an_inst)/4

* MOR calculations 
gen mor = exp(0.95 * sqrt(mean_odds))
gen mor_ll = exp(0.95 * sqrt(mean_odds_ll))
gen mor_ul = exp(0.95 * sqrt(mean_odds_ul))
gen mor_next = exp(0.95 * sqrt(mean_odds_next))
gen mor_ll_next = exp(0.95 * sqrt(mean_odds_ll_next))
gen mor_ul_next = exp(0.95 * sqrt(mean_odds_ul_next))
* Sigma calculations 
gen sigma = sqrt(mean_odds)
gen sigma_ll = sqrt(mean_odds_ll)
gen sigma_ul = sqrt(mean_odds_ul)
gen sigma_next = sqrt(mean_odds_next)
gen sigma_ll_next = sqrt(mean_odds_ll_next)
gen sigma_ul_next = sqrt(mean_odds_ul_next)


* putexcel 
putexcel set "mor_sigma_2025_05_22.xls", modify 
putexcel A10 = "model 0: anesthesiologists within hospitals"
putexcel A11 = "---"
putexcel A12 = "institution_e"
putexcel A13 = "institution_e>starting_provider_anes_att_e]"
summarize mor 
return list 
putexcel B12 = (r(mean))
summarize mor_ll
putexcel C12 = (r(mean))
summarize mor_ul
putexcel D12 = (r(mean))
summarize sigma 
return list 
putexcel E12 = (r(mean))
summarize sigma_ll
putexcel F12 = (r(mean))
summarize sigma_ul
putexcel G12 = (r(mean))
summarize icc_inst 
putexcel H12 = (r(mean))
summarize mor_next 
return list 
putexcel B13 = (r(mean))
summarize mor_ll_next
putexcel C13 = (r(mean))
summarize mor_ul_next
putexcel D13 = (r(mean))
summarize sigma_next 
return list 
putexcel E13 = (r(mean))
summarize sigma_ll_next
putexcel F13 = (r(mean))
summarize sigma_ul_next
putexcel G13 = (r(mean))
summarize icc_an_inst 
putexcel H13 = (r(mean))


* drop temporary variables to reuse 
drop icc* mor* sigma* odds* mean*



/////////////////////////////////////////////////////////////////////////////

* PAC: model 1: fixed effects  - fixed + anesthesiologists 

/////////////////////////////////////////////////////////////////////////////


melogit pac_intraop_exp_b surgical_vol_div_10 i.case_date_yr age_in_years i.sex_e i.race_e bmi  i.asa_class_e i.weekend_e i.starting_crna i.starting_res i.emergency_status_e i.elix_cardiac_arrhythmia_e i.elix_chronic_pulmonary_e i.elix_chf_e i.elix_pvd_e i.elix_valvular_e i.comorbid_mpog_cvd_e i.comorbid_mpog_cad_e preop_bun_imp preop_potassium_imp preop_hgb_a1c_imp preop_inr_imp preop_hemoglobin_imp i.isolated_cabg_e i.mv_repair_e i.mv_replace_e i.av_replace_e i.tricuspid_e i.avss_av_repair_e i.aortic_prox_e i.lung_tx_e i.heart_tx_e i.redo_e if rando_1a == 1, || starting_provider_anes_att_e:, or 
* store estimates
estimates store fixed_a_1a
* save output via outreg2
outreg2 using glmm_anes_fixed_2025_05_22.xls, replace dec(2) stat(coef ci se pval) eform sideway alpha(0.0001, 0.001, 0.01) ctitle(model_a) title("PAC") 
* coefficients
outreg2 using glmm_anes_fixed_coefs_2025_05_22.xls, replace dec(2) stat(coef ci se pval) sideway alpha(0.0001, 0.001, 0.01) ctitle(model_a) title("PAC") 


* next 
melogit pac_intraop_exp_b surgical_vol_div_10 i.case_date_yr age_in_years i.sex_e i.race_e bmi i.asa_class_e i.weekend_e i.starting_crna i.starting_res i.emergency_status_e i.elix_cardiac_arrhythmia_e i.elix_chronic_pulmonary_e i.elix_chf_e i.elix_pvd_e i.elix_valvular_e i.comorbid_mpog_cvd_e i.comorbid_mpog_cad_e preop_bun_imp preop_potassium_imp preop_hgb_a1c_imp preop_inr_imp preop_hemoglobin_imp i.isolated_cabg_e i.mv_repair_e i.mv_replace_e i.av_replace_e i.tricuspid_e i.avss_av_repair_e i.aortic_prox_e i.lung_tx_e i.heart_tx_e i.redo_e if rando_2a == 1, || starting_provider_anes_att_e:, or 
estimates store fixed_a_2a
* save output via outreg2
outreg2 using glmm_anes_fixed_2025_05_22.xls, append dec(2) stat(coef se ci pval) eform sideway alpha(0.0001, 0.001, 0.01) ctitle(model_b) title("PAC")
outreg2 using glmm_anes_fixed_coefs_2025_05_22.xls, append dec(2) stat(coef ci se pval) sideway alpha(0.0001, 0.001, 0.01) ctitle(model_b) title("PAC") 

* next 
melogit pac_intraop_exp_b surgical_vol_div_10 i.case_date_yr age_in_years i.sex_e i.race_e bmi i.asa_class_e i.weekend_e i.starting_crna i.starting_res i.emergency_status_e i.elix_cardiac_arrhythmia_e i.elix_chronic_pulmonary_e i.elix_chf_e i.elix_pvd_e i.elix_valvular_e i.comorbid_mpog_cvd_e i.comorbid_mpog_cad_e preop_bun_imp preop_potassium_imp preop_hgb_a1c_imp preop_inr_imp preop_hemoglobin_imp i.isolated_cabg_e i.mv_repair_e i.mv_replace_e i.av_replace_e i.tricuspid_e i.avss_av_repair_e i.aortic_prox_e i.lung_tx_e i.heart_tx_e i.redo_e if rando_3a == 1, || starting_provider_anes_att_e:, or 
estimates store fixed_a_3a
* save output via outreg2 
outreg2 using glmm_anes_fixed_2025_05_22.xls, append dec(2) stat(coef se ci pval) eform sideway alpha(0.0001, 0.001, 0.01) ctitle(model_c) title("PAC")
outreg2 using glmm_anes_fixed_coefs_2025_05_22.xls, append dec(2) stat(coef ci se pval) sideway alpha(0.0001, 0.001, 0.01) ctitle(model_c) title("PAC") 


* next 
melogit pac_intraop_exp_b surgical_vol_div_10 i.case_date_yr age_in_years i.sex_e i.race_e bmi  i.asa_class_e i.weekend_e i.starting_crna i.starting_res i.emergency_status_e i.elix_cardiac_arrhythmia_e i.elix_chronic_pulmonary_e i.elix_chf_e i.elix_pvd_e i.elix_valvular_e i.comorbid_mpog_cvd_e i.comorbid_mpog_cad_e preop_bun_imp preop_potassium_imp preop_hgb_a1c_imp preop_inr_imp preop_hemoglobin_imp i.isolated_cabg_e i.mv_repair_e i.mv_replace_e i.av_replace_e i.tricuspid_e i.avss_av_repair_e i.aortic_prox_e i.lung_tx_e i.heart_tx_e i.redo_e if rando_4a == 1, || starting_provider_anes_att_e:, or 
estimates store fixed_a_4a
* save output via outreg2 
outreg2 using glmm_anes_fixed_2025_05_22.xls, append dec(2) stat(coef se ci pval) eform sideway alpha(0.0001, 0.001, 0.01) ctitle(model_d) title("PAC")
outreg2 using glmm_anes_fixed_coefs_2025_05_22.xls, append dec(2) stat(coef ci se pval) sideway alpha(0.0001, 0.001, 0.01) ctitle(model_d) title("PAC") 


* directory of saved melogit estimates
estimates dir


* model 
estimates replay fixed_a_1a
matrix list r(table)
gen odds_1a = (r(table)["b", "/:var(_cons[starting_provider_anes_att_e])"])
gen odds_1a_ll = (r(table)["ll", "/:var(_cons[starting_provider_anes_att_e])"])
gen odds_1a_ul = (r(table)["ul", "/:var(_cons[starting_provider_anes_att_e])"])
estimates replay fixed_a_1a
estat icc 
return list 
gen icc_1a = (r(icc2))

* model 
estimates replay fixed_a_2a
matrix list r(table)
gen odds_2a = (r(table)["b", "/:var(_cons[starting_provider_anes_att_e])"])
gen odds_2a_ll = (r(table)["ll", "/:var(_cons[starting_provider_anes_att_e])"])
gen odds_2a_ul = (r(table)["ul", "/:var(_cons[starting_provider_anes_att_e])"])
estimates replay fixed_a_2a
estat icc 
return list 
gen icc_2a = (r(icc2))

* model 
estimates replay fixed_a_3a
matrix list r(table)
gen odds_3a = (r(table)["b", "/:var(_cons[starting_provider_anes_att_e])"])
gen odds_3a_ll = (r(table)["ll", "/:var(_cons[starting_provider_anes_att_e])"])
gen odds_3a_ul = (r(table)["ul", "/:var(_cons[starting_provider_anes_att_e])"])
estimates replay fixed_a_3a
estat icc 
return list 
gen icc_3a = (r(icc2))

* model 
estimates replay fixed_a_4a
matrix list r(table)
gen odds_4a = (r(table)["b", "/:var(_cons[starting_provider_anes_att_e])"])
gen odds_4a_ll = (r(table)["ll", "/:var(_cons[starting_provider_anes_att_e])"])
gen odds_4a_ul = (r(table)["ul", "/:var(_cons[starting_provider_anes_att_e])"])
estimates replay fixed_a_4a
estat icc 
return list 
gen icc_4a = (r(icc2))

* averages
gen mean_odds = (odds_1a + odds_2a + odds_3a + odds_4a)/4
gen mean_odds_ll = (odds_1a_ll + odds_2a_ll + odds_3a_ll + odds_4a_ll)/4
gen mean_odds_ul = (odds_1a_ul + odds_2a_ul + odds_3a_ul + odds_4a_ul)/4
gen icc = (icc_1a + icc_2a + icc_3a + icc_4a)/4

* MOR calculations 
gen mor = exp(0.95 * sqrt(mean_odds))
gen mor_ll = exp(0.95 * sqrt(mean_odds_ll))
gen mor_ul = exp(0.95 * sqrt(mean_odds_ul))

* Sigma calculations 
gen sigma = sqrt(mean_odds)
gen sigma_ll = sqrt(mean_odds_ll)
gen sigma_ul = sqrt(mean_odds_ul)

* putexcel 
putexcel set "mor_sigma_2025_05_22.xls", modify 
putexcel A15 = "model 1: fixed + anesthesiologists"
putexcel A16 = "---"
putexcel A17 = "starting_provider_anes_att_e"
summarize mor 
return list 
putexcel B17 = (r(mean))
summarize mor_ll
putexcel C17 = (r(mean))
summarize mor_ul
putexcel D17 = (r(mean))
summarize sigma 
return list 
putexcel E17 = (r(mean))
summarize sigma_ll
putexcel F17 = (r(mean))
summarize sigma_ul
putexcel G17 = (r(mean))
summarize icc 
putexcel H17 = (r(mean))

* drop temporary variables to reuse 
drop icc* mor* sigma* odds* mean*



/////////////////////////////////////////////////////////////////////////////

* PAC: model 2: fixed effects  - fixed + hospitals 

/////////////////////////////////////////////////////////////////////////////


melogit pac_intraop_exp_b surgical_vol_div_10 i.case_date_yr age_in_years i.sex_e bmi i.race_e i.asa_class_e i.weekend_e i.starting_crna i.starting_res i.emergency_status_e i.elix_cardiac_arrhythmia_e i.elix_chronic_pulmonary_e i.elix_chf_e i.elix_pvd_e i.elix_valvular_e i.comorbid_mpog_cvd_e i.comorbid_mpog_cad_e preop_bun_imp preop_potassium_imp preop_hgb_a1c_imp preop_inr_imp preop_hemoglobin_imp i.isolated_cabg_e i.mv_repair_e i.mv_replace_e i.av_replace_e i.tricuspid_e i.avss_av_repair_e i.aortic_prox_e i.lung_tx_e i.heart_tx_e i.redo_e if rando_1a == 1, || institution_e:, or 
* store estimates
estimates store fixed_h_1a
* save output via outreg2
outreg2 using glmm_hosp_fixed_2025_05_22.xls, replace dec(2) stat(coef ci se pval) eform sideway alpha(0.0001, 0.001, 0.01) ctitle(model_a) title("PAC") 
outreg2 using glmm_hosp_fixed_coefs_2025_05_22.xls, replace dec(2) stat(coef ci se pval) sideway alpha(0.0001, 0.001, 0.01) ctitle(model_a) title("PAC") 


* next 
melogit pac_intraop_exp_b surgical_vol_div_10 i.case_date_yr age_in_years i.sex_e bmi i.race_e i.asa_class_e i.weekend_e i.starting_crna i.starting_res i.emergency_status_e i.elix_cardiac_arrhythmia_e i.elix_chronic_pulmonary_e i.elix_chf_e i.elix_pvd_e i.elix_valvular_e i.comorbid_mpog_cvd_e i.comorbid_mpog_cad_e preop_bun_imp preop_potassium_imp preop_hgb_a1c_imp preop_inr_imp preop_hemoglobin_imp i.isolated_cabg_e i.mv_repair_e i.mv_replace_e i.av_replace_e i.tricuspid_e i.avss_av_repair_e i.aortic_prox_e i.lung_tx_e i.heart_tx_e i.redo_e if rando_2a == 1, || institution_e:, or 
estimates store fixed_h_2a
* save output via outreg2
outreg2 using glmm_hosp_fixed_2025_05_22.xls, append dec(2) stat(coef se ci pval) eform sideway alpha(0.0001, 0.001, 0.01) ctitle(model_b) title("PAC")
outreg2 using glmm_hosp_fixed_coefs_2025_05_22.xls, append dec(2) stat(coef ci se pval) sideway alpha(0.0001, 0.001, 0.01) ctitle(model_b) title("PAC") 


* next 
melogit pac_intraop_exp_b surgical_vol_div_10 i.case_date_yr age_in_years i.sex_e bmi i.race_e  i.asa_class_e i.weekend_e i.starting_crna i.starting_res i.emergency_status_e i.elix_cardiac_arrhythmia_e i.elix_chronic_pulmonary_e i.elix_chf_e i.elix_pvd_e i.elix_valvular_e i.comorbid_mpog_cvd_e i.comorbid_mpog_cad_e preop_bun_imp preop_potassium_imp preop_hgb_a1c_imp preop_inr_imp preop_hemoglobin_imp i.isolated_cabg_e i.mv_repair_e i.mv_replace_e i.av_replace_e i.tricuspid_e i.avss_av_repair_e i.aortic_prox_e i.lung_tx_e i.heart_tx_e i.redo_e if rando_3a == 1, || institution_e:, or 
estimates store fixed_h_3a
* save output via outreg2 
outreg2 using glmm_hosp_fixed_2025_05_22.xls, append dec(2) stat(coef se ci pval) eform sideway alpha(0.0001, 0.001, 0.01) ctitle(model_c) title("PAC")
outreg2 using glmm_hosp_fixed_coefs_2025_05_22.xls, append dec(2) stat(coef ci se pval) sideway alpha(0.0001, 0.001, 0.01) ctitle(model_c) title("PAC") 

* next 
melogit pac_intraop_exp_b surgical_vol_div_10 i.case_date_yr age_in_years i.sex_e bmi i.race_e i.asa_class_e i.weekend_e i.starting_crna i.starting_res i.emergency_status_e i.elix_cardiac_arrhythmia_e i.elix_chronic_pulmonary_e i.elix_chf_e i.elix_pvd_e i.elix_valvular_e i.comorbid_mpog_cvd_e i.comorbid_mpog_cad_e preop_bun_imp preop_potassium_imp preop_hgb_a1c_imp preop_inr_imp preop_hemoglobin_imp i.isolated_cabg_e i.mv_repair_e i.mv_replace_e i.av_replace_e i.tricuspid_e i.avss_av_repair_e i.aortic_prox_e i.lung_tx_e i.heart_tx_e i.redo_e if rando_4a == 1, || institution_e:, or 
estimates store fixed_h_4a
* save output via outreg2 
outreg2 using glmm_hosp_fixed_2025_05_22.xls, append dec(2) stat(coef se ci pval) eform sideway alpha(0.0001, 0.001, 0.01) ctitle(model_d) title("PAC")
outreg2 using glmm_hosp_fixed_coefs_2025_05_22.xls, append dec(2) stat(coef ci se pval) sideway alpha(0.0001, 0.001, 0.01) ctitle(model_d) title("PAC") 


* directory of saved melogit estimates
estimates dir


* model 
estimates replay fixed_h_1a
matrix list r(table)
gen odds_1a = (r(table)["b", "/:var(_cons[institution_e])"])
gen odds_1a_ll = (r(table)["ll", "/:var(_cons[institution_e])"])
gen odds_1a_ul = (r(table)["ul", "/:var(_cons[institution_e])"])
estimates replay fixed_h_1a
estat icc 
return list 
gen icc_1a = (r(icc2))

* model 
estimates replay fixed_h_2a
matrix list r(table)
gen odds_2a = (r(table)["b", "/:var(_cons[institution_e])"])
gen odds_2a_ll = (r(table)["ll", "/:var(_cons[institution_e])"])
gen odds_2a_ul = (r(table)["ul", "/:var(_cons[institution_e])"])
estimates replay fixed_h_2a
estat icc 
return list 
gen icc_2a = (r(icc2))

* model 
estimates replay fixed_h_3a
matrix list r(table)
gen odds_3a = (r(table)["b", "/:var(_cons[institution_e])"])
gen odds_3a_ll = (r(table)["ll", "/:var(_cons[institution_e])"])
gen odds_3a_ul = (r(table)["ul", "/:var(_cons[institution_e])"])
estimates replay fixed_h_3a
estat icc 
return list 
gen icc_3a = (r(icc2))

* model 
estimates replay fixed_h_4a
matrix list r(table)
gen odds_4a = (r(table)["b", "/:var(_cons[institution_e])"])
gen odds_4a_ll = (r(table)["ll", "/:var(_cons[institution_e])"])
gen odds_4a_ul = (r(table)["ul", "/:var(_cons[institution_e])"])
estimates replay fixed_h_4a
estat icc 
return list 
gen icc_4a = (r(icc2))

* averages
gen mean_odds = (odds_1a + odds_2a + odds_3a + odds_4a)/4
gen mean_odds_ll = (odds_1a_ll + odds_2a_ll + odds_3a_ll + odds_4a_ll)/4
gen mean_odds_ul = (odds_1a_ul + odds_2a_ul + odds_3a_ul + odds_4a_ul)/4
gen icc = (icc_1a + icc_2a + icc_3a + icc_4a)/4

* MOR calculations 
gen mor = exp(0.95 * sqrt(mean_odds))
gen mor_ll = exp(0.95 * sqrt(mean_odds_ll))
gen mor_ul = exp(0.95 * sqrt(mean_odds_ul))

* Sigma calculations 
gen sigma = sqrt(mean_odds)
gen sigma_ll = sqrt(mean_odds_ll)
gen sigma_ul = sqrt(mean_odds_ul)

* putexcel 
putexcel set "mor_sigma_2025_05_22.xls", modify 
putexcel A19 = "model 2: fixed + hospitals"
putexcel A20 = "---"
putexcel A21 = "institution_e"
summarize mor 
return list 
putexcel B21 = (r(mean))
summarize mor_ll
putexcel C21 = (r(mean))
summarize mor_ul
putexcel D21 = (r(mean))
summarize sigma 
return list 
putexcel E21 = (r(mean))
summarize sigma_ll
putexcel F21 = (r(mean))
summarize sigma_ul
putexcel G21 = (r(mean))
summarize icc 
putexcel H21 = (r(mean))

* drop temporary variables to reuse 
drop icc* mor* sigma* odds* mean*


/////////////////////////////////////////////////////////////////////////////

* PAC: model 3: fixed effects  - fixed + anesthesiologists within hospitals 

/////////////////////////////////////////////////////////////////////////////

melogit pac_intraop_exp_b surgical_vol_div_10 i.case_date_yr age_in_years i.sex_e i.race_e bmi  i.asa_class_e i.weekend_e i.starting_crna i.starting_res i.emergency_status_e i.elix_cardiac_arrhythmia_e i.elix_chronic_pulmonary_e i.elix_chf_e i.elix_pvd_e i.elix_valvular_e i.comorbid_mpog_cvd_e i.comorbid_mpog_cad_e preop_bun_imp preop_potassium_imp preop_hgb_a1c_imp preop_inr_imp preop_hemoglobin_imp i.isolated_cabg_e i.mv_repair_e i.mv_replace_e i.av_replace_e i.tricuspid_e i.avss_av_repair_e i.aortic_prox_e i.lung_tx_e i.heart_tx_e i.redo_e if rando_1a == 1, || institution_e: || starting_provider_anes_att_e:, or 
* store estimates
estimates store fixed_ha_1a
* save output via outreg2
outreg2 using glmm_anes_in_hosp_fixed_2025_05_22.xls, replace dec(2) stat(coef ci se pval) eform sideway alpha(0.0001, 0.001, 0.01) ctitle(model_a) title("PAC") 
outreg2 using glmm_anes_in_hosp_fixed_coefs_2025_05_22.xls, replace dec(2) stat(coef ci se pval) sideway alpha(0.0001, 0.001, 0.01) ctitle(model_a) title("PAC") 

* next 
melogit pac_intraop_exp_b surgical_vol_div_10 i.case_date_yr age_in_years i.sex_e bmi i.race_e  i.asa_class_e i.weekend_e i.starting_crna i.starting_res i.emergency_status_e i.elix_cardiac_arrhythmia_e i.elix_chronic_pulmonary_e i.elix_chf_e i.elix_pvd_e i.elix_valvular_e i.comorbid_mpog_cvd_e i.comorbid_mpog_cad_e preop_bun_imp preop_potassium_imp preop_hgb_a1c_imp preop_inr_imp preop_hemoglobin_imp i.isolated_cabg_e i.mv_repair_e i.mv_replace_e i.av_replace_e i.tricuspid_e i.avss_av_repair_e i.aortic_prox_e i.lung_tx_e i.heart_tx_e i.redo_e if rando_2a == 1, || institution_e: || starting_provider_anes_att_e:, or 
* store estimates
estimates store fixed_ha_2a
* save output via outreg2
outreg2 using glmm_anes_in_hosp_fixed_2025_05_22.xls, append dec(2) stat(coef ci se pval) eform sideway alpha(0.0001, 0.001, 0.01) ctitle(model_b) title("PAC") 
outreg2 using glmm_anes_in_hosp_fixed_coefs_2025_05_22.xls, append dec(2) stat(coef ci se pval) sideway alpha(0.0001, 0.001, 0.01) ctitle(model_b) title("PAC") 


* next 
melogit pac_intraop_exp_b surgical_vol_div_10 i.case_date_yr age_in_years i.sex_e i.race_e bmi i.asa_class_e i.weekend_e i.starting_crna i.starting_res i.emergency_status_e i.elix_cardiac_arrhythmia_e i.elix_chronic_pulmonary_e i.elix_chf_e i.elix_pvd_e i.elix_valvular_e i.comorbid_mpog_cvd_e i.comorbid_mpog_cad_e preop_bun_imp preop_potassium_imp preop_hgb_a1c_imp preop_inr_imp preop_hemoglobin_imp i.isolated_cabg_e i.mv_repair_e i.mv_replace_e i.av_replace_e i.tricuspid_e i.avss_av_repair_e i.aortic_prox_e i.lung_tx_e i.heart_tx_e i.redo_e if rando_3a == 1, || institution_e: || starting_provider_anes_att_e:, or 
* store estimates
estimates store fixed_ha_3a
* save output via outreg2
outreg2 using glmm_anes_in_hosp_fixed_2025_05_22.xls, append dec(2) stat(coef ci se pval) eform sideway alpha(0.0001, 0.001, 0.01) ctitle(model_c) title("PAC") 
outreg2 using glmm_anes_in_hosp_fixed_coefs_2025_05_22.xls, append dec(2) stat(coef ci se pval) sideway alpha(0.0001, 0.001, 0.01) ctitle(model_c) title("PAC") 


* next 
melogit pac_intraop_exp_b surgical_vol_div_10 i.case_date_yr age_in_years i.sex_e i.race_e bmi  i.asa_class_e i.weekend_e i.starting_crna i.starting_res i.emergency_status_e i.elix_cardiac_arrhythmia_e i.elix_chronic_pulmonary_e i.elix_chf_e i.elix_pvd_e i.elix_valvular_e i.comorbid_mpog_cvd_e i.comorbid_mpog_cad_e preop_bun_imp preop_potassium_imp preop_hgb_a1c_imp preop_inr_imp preop_hemoglobin_imp i.isolated_cabg_e i.mv_repair_e i.mv_replace_e i.av_replace_e i.tricuspid_e i.avss_av_repair_e i.aortic_prox_e i.lung_tx_e i.heart_tx_e i.redo_e if rando_4a == 1, || institution_e: || starting_provider_anes_att_e:, or 
* store estimates
estimates store fixed_ha_4a
* save output via outreg2
outreg2 using glmm_anes_in_hosp_fixed_2025_05_22.xls, append dec(2) stat(coef ci se pval) eform sideway alpha(0.0001, 0.001, 0.01) ctitle(model_d) title("PAC") 
outreg2 using glmm_anes_in_hosp_fixed_coefs_2025_05_22.xls, append dec(2) stat(coef ci se pval) sideway alpha(0.0001, 0.001, 0.01) ctitle(model_d) title("PAC") 


* estimates directory 
estimates dir

* fixed model: 3-level 
estimates replay fixed_ha_1a
matrix list r(table)
gen odds_1a = (r(table)["b", "/:var(_cons[institution_e])"])
gen odds_1a_ll = (r(table)["ll", "/:var(_cons[institution_e])"])
gen odds_1a_ul = (r(table)["ul", "/:var(_cons[institution_e])"])
gen odds_1a_next = (r(table)["b", "/:var(_cons[institution_e>starting_provider_anes_att_e])"])
gen odds_1a_ll_next = (r(table)["ll", "/:var(_cons[institution_e>starting_provider_anes_att_e])"])
gen odds_1a_ul_next = (r(table)["ul", "/:var(_cons[institution_e>starting_provider_anes_att_e])"])
estimates replay fixed_ha_1a
estat icc 
return list 
gen icc_1a_inst = (r(icc3))
gen icc_1a_an_inst = (r(icc2))

* fixed model: 3-level 
estimates replay fixed_ha_2a
matrix list r(table)
gen odds_2a = (r(table)["b", "/:var(_cons[institution_e])"])
gen odds_2a_ll = (r(table)["ll", "/:var(_cons[institution_e])"])
gen odds_2a_ul = (r(table)["ul", "/:var(_cons[institution_e])"])
gen odds_2a_next = (r(table)["b", "/:var(_cons[institution_e>starting_provider_anes_att_e])"])
gen odds_2a_ll_next = (r(table)["ll", "/:var(_cons[institution_e>starting_provider_anes_att_e])"])
gen odds_2a_ul_next = (r(table)["ul", "/:var(_cons[institution_e>starting_provider_anes_att_e])"])
estimates replay fixed_ha_2a
estat icc 
return list 
gen icc_2a_inst = (r(icc3))
gen icc_2a_an_inst = (r(icc2))

* fixed model: 3-level 
estimates replay fixed_ha_3a
matrix list r(table)
gen odds_3a = (r(table)["b", "/:var(_cons[institution_e])"])
gen odds_3a_ll = (r(table)["ll", "/:var(_cons[institution_e])"])
gen odds_3a_ul = (r(table)["ul", "/:var(_cons[institution_e])"])
gen odds_3a_next = (r(table)["b", "/:var(_cons[institution_e>starting_provider_anes_att_e])"])
gen odds_3a_ll_next = (r(table)["ll", "/:var(_cons[institution_e>starting_provider_anes_att_e])"])
gen odds_3a_ul_next = (r(table)["ul", "/:var(_cons[institution_e>starting_provider_anes_att_e])"])
estimates replay fixed_ha_3a
estat icc 
return list 
gen icc_3a_inst = (r(icc3))
gen icc_3a_an_inst = (r(icc2))

* null model: 3-level 
estimates replay fixed_ha_4a
matrix list r(table)
gen odds_4a = (r(table)["b", "/:var(_cons[institution_e])"])
gen odds_4a_ll = (r(table)["ll", "/:var(_cons[institution_e])"])
gen odds_4a_ul = (r(table)["ul", "/:var(_cons[institution_e])"])
gen odds_4a_next = (r(table)["b", "/:var(_cons[institution_e>starting_provider_anes_att_e])"])
gen odds_4a_ll_next = (r(table)["ll", "/:var(_cons[institution_e>starting_provider_anes_att_e])"])
gen odds_4a_ul_next = (r(table)["ul", "/:var(_cons[institution_e>starting_provider_anes_att_e])"])
estimates replay fixed_ha_4a
estat icc 
return list 
gen icc_4a_inst = (r(icc3))
gen icc_4a_an_inst = (r(icc2))

* averages
gen mean_odds = (odds_1a + odds_2a + odds_3a + odds_4a)/4
gen mean_odds_ll = (odds_1a_ll + odds_2a_ll + odds_3a_ll + odds_4a_ll)/4
gen mean_odds_ul = (odds_1a_ul + odds_2a_ul + odds_3a_ul + odds_4a_ul)/4
gen mean_odds_next = (odds_1a_next + odds_2a_next + odds_3a_next + odds_4a_next)/4
gen mean_odds_ll_next = (odds_1a_ll_next + odds_2a_ll_next + odds_3a_ll_next + odds_4a_ll_next)/4
gen mean_odds_ul_next = (odds_1a_ul_next + odds_2a_ul_next + odds_3a_ul_next + odds_4a_ul_next)/4
gen icc_inst = (icc_1a_inst + icc_2a_inst + icc_3a_inst + icc_4a_inst)/4
gen icc_an_inst = (icc_1a_an_inst + icc_2a_an_inst + icc_3a_an_inst + icc_4a_an_inst)/4

* MOR calculations 
gen mor = exp(0.95 * sqrt(mean_odds))
gen mor_ll = exp(0.95 * sqrt(mean_odds_ll))
gen mor_ul = exp(0.95 * sqrt(mean_odds_ul))
gen mor_next = exp(0.95 * sqrt(mean_odds_next))
gen mor_ll_next = exp(0.95 * sqrt(mean_odds_ll_next))
gen mor_ul_next = exp(0.95 * sqrt(mean_odds_ul_next))
* Sigma calculations 
gen sigma = sqrt(mean_odds)
gen sigma_ll = sqrt(mean_odds_ll)
gen sigma_ul = sqrt(mean_odds_ul)
gen sigma_next = sqrt(mean_odds_next)
gen sigma_ll_next = sqrt(mean_odds_ll_next)
gen sigma_ul_next = sqrt(mean_odds_ul_next)


* putexcel 
putexcel set "mor_sigma_2025_05_22.xls", modify 
putexcel A23 = "model 3: fixed + anesthesiologists within hospitals"
putexcel A24 = "---"
putexcel A25 = "institution_e"
putexcel A26 = "institution_e>starting_provider_anes_att_e]"
summarize mor 
return list 
putexcel B25 = (r(mean))
summarize mor_ll
putexcel C25 = (r(mean))
summarize mor_ul
putexcel D25 = (r(mean))
summarize sigma 
return list 
putexcel E25 = (r(mean))
summarize sigma_ll
putexcel F25 = (r(mean))
summarize sigma_ul
putexcel G25 = (r(mean))
summarize icc_inst 
putexcel H25 = (r(mean))
summarize mor_next 
return list 
putexcel B26 = (r(mean))
summarize mor_ll_next
putexcel C26 = (r(mean))
summarize mor_ul_next
putexcel D26 = (r(mean))
summarize sigma_next 
return list 
putexcel E26 = (r(mean))
summarize sigma_ll_next
putexcel F26 = (r(mean))
summarize sigma_ul_next
putexcel G26 = (r(mean))
summarize icc_an_inst 
putexcel H26 = (r(mean))


* drop temporary variables to reuse 
drop icc* mor* sigma* odds* mean*

/////////////////////////////////////////////////////////////////////////////


/////////////////////////////////////////////////////////////////////////////



log close 
