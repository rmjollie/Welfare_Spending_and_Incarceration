# -*- coding: utf-8 -*-
"""
Created on Tue Apr 18 15:44:13 2023

@author: rmjol
"""

import pandas as pd
import numpy as np
import os
from matplotlib import pyplot as plt
import seaborn as sns
import statsmodels.formula.api as smf
import statsmodels.api as sm
from linearmodels import PooledOLS
from linearmodels import RandomEffects

os.chdir("C:/Users/rmjol/OneDrive/Documents/Python/Projects/Welfare_Spending_and_Incarceration/Data")

#### File Reading ####
## Read state population estiamtes 2010-2018"
state_population = pd.read_excel("nst-est2019-01.xlsx")

## Read all state spending estimates 2010 - 2018 ##
file_pattern1 = "ACSDP1Y{}.csv"
file_names1 = [file_pattern1.format(i) for i in range(2010, 2019)]
state_stats = [pd.read_csv(file) for file in file_names1]
for i, stats in enumerate(state_stats):
    globals()[f"stats_{i+2010}"] = stats
    
## Read state probation estimates 2010 - 2018 ##
file_pattern2 = "Probation{}.tsv"
file_names2 = [file_pattern2.format(i) for i in range(2010, 2019)]
state_probation = [pd.read_csv(file, sep="\t") for file in file_names2]
for i, probation in enumerate(state_probation):
    globals()[f"probation_{i+2010}"] = probation

## Read state parole estimates 2010 - 2018 ##
file_pattern3 = "Parole{}.tsv"
file_names3 = [file_pattern3.format(i) for i in range(2010, 2019)]
state_parole = [pd.read_csv(file, sep="\t") for file in file_names3]
for i, parole in enumerate(state_parole):
    globals()[f"parole_{i+2010}"] = parole

## Read state jail estimates ##
file_pattern4 = "Jail{}.tsv"
file_names4 = [file_pattern4.format(i) for i in range(2010, 2019)]
state_jail = [pd.read_csv(file, sep="\t") for file in file_names4]
for i, jail in enumerate(state_jail):
    globals()[f"jail_{i+2010}"] = jail

## Read state prisoners estimates ##
state_prisoners = pd.read_excel("data.xlsx")

## Read state spending ##
file_pattern5 = "ASFIN{}.xlsx"
file_names5 = [file_pattern5.format(i) for i in range(2010, 2019)]
state_spending = [pd.read_excel(file) for file in file_names5]
for i, spending in enumerate(state_spending):
    globals()[f"spending_{i+2010}"] = spending

## Read state crime ##
file_pattern6 = "crime{}.xls"
file_names6 = [file_pattern6.format(i) for i in range(2010, 2019)]
state_crime = [pd.read_excel(file) for file in file_names6]
for i, crime in enumerate(state_crime):
    globals()[f"crime_{i+2010}"] = crime


#### 2010 - 2018 data cleaning ####
## create state identifiers ##
state_name = spending_2018.iloc[0]
state_name = state_name.reset_index()
state_name = state_name.iloc[2::3, :]
state_name = state_name.iloc[1:152, 0]
state_name = state_name.reset_index(drop=True)

state_initial = probation_2018.iloc[1:52, 1]
state_initial = state_initial.drop(labels = 9)
state_initial = state_initial.reset_index(drop=True)

state_num = np.arange(1,52)
state_num = pd.Series(state_num)
state_num = state_num.drop(labels = 8)
state_num = state_num.reset_index(drop=True)

state_name_rep = list(state_name) * 9
state_initial_rep = list(state_initial) * 9
state_num_rep = list(state_num) * 9

## grab years and population estimates ##
pop_years = state_population.iloc[8:59,3:12]
pop_years.columns = ["2010", "2011", "2012", "2013", "2014", "2015", "2016", "2017", "2018"]
pop_years = pop_years.drop(labels = 16)
pop_years = pop_years.reset_index(drop = True)
pop_long = pd.melt(pop_years, id_vars=None, value_vars=None, var_name="years", value_name="population")
year = pop_long.iloc[:,0]
population = pop_long.iloc[:,1]

## clean poverty_rate data ##
poverty_temp = []
for i in range(2010, 2019):
    df_name = f"stats_{i}"
    df = globals()[df_name]
    selected_df = df.iloc[135]
    selected_df = selected_df.reset_index()
    selected_df = selected_df.iloc[2::2,:]
    selected_df = selected_df.drop(labels = [18, 104])
    selected_df = selected_df.iloc[:,1]
    selected_df = selected_df.reset_index(drop = True)
    selected_df = selected_df.str.replace(r"\D","", regex=True).astype(float)
    selected_df = selected_df / 10
    poverty_temp.append(selected_df)
all_poverty = pd.concat(poverty_temp, axis=1)
all_poverty.columns = ["2010", "2011", "2012", "2013", "2014", "2015", "2016", "2017", "2018"]
poverty_long = pd.melt(all_poverty, id_vars=None, value_vars=None, var_name="years", value_name="poverty_rate")

## clean unemployment_rate data ##
unemploy_temp = []
for i in range(2010, 2019):
    df_name = f"stats_{i}"
    df = globals()[df_name]
    selected_df = df.iloc[5]
    selected_df = selected_df.reset_index()
    selected_df = selected_df.iloc[2::2,:]
    selected_df = selected_df.drop(labels = [18, 104])
    selected_df = selected_df.iloc[:,1]
    selected_df = selected_df.reset_index(drop = True)
    selected_df = selected_df.str.replace(r"\D","", regex=True).astype(float)
    selected_df = selected_df / 10
    unemploy_temp.append(selected_df)
all_unemploy = pd.concat(unemploy_temp, axis=1)
all_unemploy.columns = ["2010", "2011", "2012", "2013", "2014", "2015", "2016", "2017", "2018"]
unemploy_long = pd.melt(all_unemploy, id_vars=None, value_vars=None, var_name="years", value_name="unemploy_rate")

## clean probation data ##
probation_temp = []
for i in range(2010,2019):
    df_name = f"probation_{i}"
    df = globals()[df_name]
    selected_df = df.iloc[1:52,24]
    selected_df = selected_df.drop(index = 9)
    selected_df = selected_df.reset_index(drop=True)
    probation_temp.append(selected_df)
all_probation = pd.concat(probation_temp, axis=1)
all_probation.columns = ["2010", "2011", "2012", "2013", "2014", "2015", "2016", "2017", "2018"]
probation_long = pd.melt(all_probation, id_vars=None, value_vars=None, var_name="years", value_name="probationers")

## clean parole data ##
parole_temp = []
for i in range(2010,2019):
    df_name = f"parole_{i}"
    df = globals()[df_name]
    selected_df = df.iloc[1:52,24]
    selected_df = selected_df.drop(index = 9)
    selected_df = selected_df.reset_index(drop=True)
    parole_temp.append(selected_df)
all_parole = pd.concat(parole_temp, axis=1)
all_parole.columns = ["2010", "2011", "2012", "2013", "2014", "2015", "2016", "2017", "2018"]
parole_long = pd.melt(all_parole, id_vars=None, value_vars=None, var_name="years", value_name="parolees")

## clean jail data ##
jail_2010 = jail_2010.rename({"state":"STATE", "finalweight":"FINALWT", "totpop":"TOTPOP"}, axis=1)
jail_2011 = jail_2011.rename({"state":"STATE", "finalweight":"FINALWT", "totpop":"TOTPOP"}, axis=1)
jail_2012 = jail_2012.rename({"state":"STATE", "finalweight":"FINALWT", "totpop":"TOTPOP"}, axis=1)
jail_2013 = jail_2013.rename({"WEIGHT":"FINALWT"}, axis=1)
jail_2014 = jail_2014.rename({"WEIGHT":"FINALWT"}, axis=1)

state_num_temp = jail_2010.loc[:,"STATE"].unique()
state_num_temp = pd.DataFrame(state_num_temp)
jail_temp = []
jail_temp.append(state_num_temp)
for i in range(2010,2019):
    df_name = f"jail_{i}"
    df = globals()[df_name]
    selected_df = df.loc[:,["STATE", "FINALWT", "TOTPOP"]]
    selected_df["jailed"] = selected_df["FINALWT"] * selected_df["TOTPOP"]
    selected_df = selected_df.groupby(by="STATE")
    selected_df = selected_df.agg(sum)
    selected_df = selected_df.loc[:,["jailed"]]
    selected_df = selected_df.reset_index(drop=True)
    jail_temp.append(selected_df)
all_jail = pd.concat(jail_temp, axis=1)
all_jail.columns = ["STATE","2010", "2011", "2012", "2013", "2014", "2015", "2016", "2017", "2018"]
jail_long = pd.melt(all_jail, id_vars="STATE", value_vars=None, var_name="years", value_name="jailed")

## clean prisoners data ##
prisoners = state_prisoners.iloc[0:51, :]
prisoners.columns = prisoners.iloc[0]
prisoners = prisoners.drop(prisoners.index[0])
prisoners = prisoners.sort_values("State")
prisoners = prisoners.iloc[0:51, 1:10]
prisoners = prisoners.reset_index(drop=True)
prison_long = pd.melt(prisoners, id_vars=None, value_vars=None, var_name="years", value_name="prisoners")

## clean spending data ##
spending_temp = []

welfare_exp2010 = spending_2010.iloc[42]
welfare_exp2010 = welfare_exp2010.reset_index()
welfare_exp2010 = welfare_exp2010.iloc[2:52, 1]
welfare_exp2010 = welfare_exp2010.reset_index(drop=True)
spending_temp.append(welfare_exp2010)

welfare_exp2011 = spending_2011.iloc[42]
welfare_exp2011 = welfare_exp2011.reset_index()
welfare_exp2011 = welfare_exp2011.iloc[2:52, 1]
welfare_exp2011 = welfare_exp2011.reset_index(drop=True)
spending_temp.append(welfare_exp2011)

for i in range(2012,2018):
    df_name = f"spending_{i}"
    df = globals()[df_name]
    selected_df = df.iloc[36]
    selected_df = selected_df.reset_index()
    selected_df = selected_df.iloc[2:52, 1]
    selected_df = selected_df.reset_index(drop=True)
    spending_temp.append(selected_df)

welfare_exp2018 = spending_2018.iloc[37]
welfare_exp2018 = welfare_exp2018.reset_index()
welfare_exp2018 = welfare_exp2018.iloc[2::3, :]
welfare_exp2018 = welfare_exp2018.iloc[1:152, 1]
welfare_exp2018 = welfare_exp2018.reset_index(drop=True)
spending_temp.append(welfare_exp2018)

all_spending = pd.concat(spending_temp, axis=1)
all_spending.columns = ["2010", "2011", "2012", "2013", "2014", "2015", "2016", "2017", "2018"]
spending_long = pd.melt(all_spending, id_vars=None, value_vars=None, var_name="years", value_name="welfare")

## clean violent crime data ##
states_temp = crime_2018.iloc[13:197,0]
states_temp = states_temp.reset_index()
states_temp = states_temp.iloc[0::3,:]
states_temp = states_temp.drop([18,30,33,51,75,78,84,108,123,138,141,168])
states_temp = states_temp.iloc[:,1]
states_temp = states_temp.reset_index(drop=True)

violent_temp = []
violent_temp.append(states_temp)

crime_2012 = crime_2012.drop(labels=0)
crime_2012 = crime_2012.reset_index(drop=True)
crime_2013 = crime_2013.drop(labels=0)
crime_2013 = crime_2013.reset_index(drop=True)
crime_2014 = crime_2014.drop(labels=0)
crime_2014 = crime_2014.reset_index(drop=True)

for i in range(2010,2019):
    df_name = f"crime_{i}"
    df = globals()[df_name]
    selected_df = df.iloc[14:198,3]
    selected_df = selected_df.reset_index()
    selected_df = selected_df.iloc[0::3, :]
    selected_df = selected_df.drop([18,30,33,51,75,78,84,108,123,138,141,168])
    selected_df = selected_df.iloc[:,1]
    selected_df = selected_df.reset_index(drop=True)
    violent_temp.append(selected_df)
all_violent = pd.concat(violent_temp, axis=1)
all_violent = all_violent.sort_values("Table 4")
all_violent = all_violent.iloc[:,1:10]
all_violent.columns = ["2010", "2011", "2012", "2013", "2014", "2015", "2016", "2017", "2018"]
violent_long = pd.melt(all_violent, id_vars=None, value_vars=None, var_name="years", value_name="violent")

## clean property crime data ##
property_temp = []
property_temp.append(states_temp)

for i in range(2010,2019):
    df_name = f"crime_{i}"
    df = globals()[df_name]
    selected_df = df.iloc[14:198,13]
    selected_df = selected_df.reset_index()
    selected_df = selected_df.iloc[0::3, :]
    selected_df = selected_df.drop([18,30,33,51,75,78,84,108,123,138,141,168])
    selected_df = selected_df.iloc[:,1]
    selected_df = selected_df.reset_index(drop=True)
    property_temp.append(selected_df)
all_property = pd.concat(property_temp, axis=1)
all_property = all_property.sort_values("Table 4")
all_property = all_property.iloc[:,1:10]
all_property.columns = ["2010", "2011", "2012", "2013", "2014", "2015", "2016", "2017", "2018"]
property_long = pd.melt(all_property, id_vars=None, value_vars=None, var_name="years", value_name="property")


## create dataframe for all clean data ##
clean_data2 = {"state_name":state_name_rep, 
      "state_initial":state_initial_rep, 
      "state_num":state_num_rep,
      "year":year,
      "population":population,
      "poverty_rate":poverty_long.iloc[:,1],
      "unemploy_rate":unemploy_long.iloc[:,1],
      "probationers":probation_long.iloc[:,1],
      "parolees":parole_long.iloc[:,1],
      "prisoners":prison_long.iloc[:,1],
      "welfare_exp":spending_long.iloc[:,1],
      "violent_crime":violent_long.iloc[:,1],
      "property_crime":property_long.iloc[:,1]
      }
clean_data2 = pd.DataFrame(clean_data2)
clean_data2 = pd.merge(clean_data2, jail_long, how="left", left_on=["state_num","year"], right_on=["STATE","years"])
clean_data2 = clean_data2.drop(columns= ["STATE", "years"])
clean_data2 = clean_data2.fillna(0)
clean_data2 = clean_data2.replace({-9:np.nan})
clean_data2 = clean_data2.dropna()

calc_data = clean_data2.loc[:, ["state_name", "state_initial", "state_num", "year", "poverty_rate", "unemploy_rate"]]
calc_data["justice_rate"] = ((clean_data2["prisoners"] + 
                                 clean_data2["probationers"] + 
                                 clean_data2["parolees"] + 
                                 clean_data2["jailed"]) / clean_data2["population"]) * 100
calc_data["violent_rate"] = (clean_data2["violent_crime"] / clean_data2["population"]) * 100
calc_data["property_rate"] = (clean_data2["property_crime"] / clean_data2["population"]) * 100
calc_data["welfare_povcap"] = clean_data2["welfare_exp"] / ((clean_data2["poverty_rate"] / 100) * clean_data2["population"])
calc_data["welfare_percap"] = clean_data2["welfare_exp"] / clean_data2["population"]

###### Visuals #######

sns.lmplot(data = calc_data, x = "welfare_povcap", y = "poverty_rate")
sns.lmplot(data = calc_data, x = "welfare_povcap", y = "unemploy_rate")
sns.lmplot(data = calc_data, x = "welfare_povcap", y = "violent_rate")
sns.lmplot(data = calc_data, x = "welfare_povcap", y = "property_rate")

####### Summary Stats #########
summary_stats = calc_data.describe()
summary_stats2 = clean_data2.describe()

###### Regressions #######
# Perform PooledOLS
pooled_y=calc_data["justice_rate"]
pooled_x=calc_data[["welfare_povcap", "violent_rate", "property_rate"]]
pooled_x = sm.add_constant(pooled_x)
pooled_olsr_model = sm.OLS(endog=pooled_y, exog=pooled_x)
pooled_olsr_model_results = pooled_olsr_model.fit()
print(pooled_olsr_model_results.summary())
print('Mean value of residual errors='+str(pooled_olsr_model_results.resid.mean()))

sm.qqplot(data=pooled_olsr_model_results.resid, line='45')
plt.show()

import statsmodels.graphics.tsaplots as tsap
tsap.plot_acf(x=pooled_olsr_model_results.resid)
plt.show()


######## USING FULL DATASET ##############
##### Entity/State - Varied Effects ######
## Get dummies ##
unit_col_name="state_initial"
time_period_col_name="year"
full_dummies = pd.get_dummies(calc_data[unit_col_name])
full_panel_with_dummies = calc_data.join(full_dummies)

## justice_rate ##
y_name = "justice_rate"
X_names = ["welfare_povcap", "violent_rate", "property_rate"]

entity_name = calc_data["state_initial"].unique()

formula = y_name + ' ~ '
i = 0
for X_name in X_names:
    if i > 0:
        formula = formula + ' + ' + X_name
    else:
        formula = formula + X_name
    i = i + 1
for dummy_name in entity_name[:-1]:
    formula = formula + ' + ' + dummy_name

full_model = smf.ols(formula=formula, data=full_panel_with_dummies)
full_model_results = full_model.fit()
print(full_model_results.summary())

## unemploy_rate ##
y_name = "unemploy_rate"
X_names = ["welfare_povcap", "violent_rate", "property_rate"]

entity_name = calc_data["state_initial"].unique()

formula = y_name + ' ~ '
i = 0
for X_name in X_names:
    if i > 0:
        formula = formula + ' + ' + X_name
    else:
        formula = formula + X_name
    i = i + 1
for dummy_name in entity_name[:-1]:
    formula = formula + ' + ' + dummy_name

full_model = smf.ols(formula=formula, data=full_panel_with_dummies)
full_model_results = full_model.fit()
print(full_model_results.summary())

### examine VIF ###
from statsmodels.stats.outliers_influence import variance_inflation_factor
  
X = calc_data[["welfare_povcap",'property_rate', 'violent_rate']]

vif_data = pd.DataFrame()
vif_data["feature"] = X.columns
vif_data["VIF"] = [variance_inflation_factor(X.values, i)
                          for i in range(len(X.columns))]
  
print(vif_data)