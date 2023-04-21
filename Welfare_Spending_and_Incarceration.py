# -*- coding: utf-8 -*-
"""
Created on Tue Apr 18 15:44:13 2023

@author: rmjol
"""

import pandas as pd
import numpy as np
import os

os.chdir("C:/Users/rmjol/OneDrive/Documents/Python/Open Data in Python/Data")

state_population = pd.read_excel("nst-est2019-01.xlsx")
state_spending = pd.read_excel("ASFIN FY2018_2017.xlsx")
state_stats = pd.read_csv("ACSDP1Y2018.DP03-2023-04-19T154739.csv")
state_prisoners = pd.read_excel("data.xlsx")
state_probationers = pd.read_csv("38057-0001-Data.tsv",sep="\t")
state_parolees = pd.read_csv("38058-0001-Data.tsv", sep ="\t")
state_jail = pd.read_csv("37392-0001-Data.tsv", sep="\t")

state_name = state_spending.iloc[0]
state_name = state_name.reset_index()
state_name = state_name.iloc[2::3, :]
state_name = state_name.iloc[1:152, 0]
state_name = state_name.reset_index(drop=True)

state_initial = state_probationers.iloc[1:52, 1]
state_initial = state_initial.drop(labels = 9)
state_initial = state_initial.reset_index(drop=True)

state_num = np.arange(1,52)
state_num = pd.Series(state_num)
state_num = state_num.drop(labels = 8)
state_num = state_num.reset_index(drop=True)

pop_2018 = state_population.iloc[8:59, 11]
pop_2018 = pop_2018.drop(labels = 16)
pop_2018 = pop_2018.reset_index(drop=True)

total_exp = state_spending.iloc[20]
total_exp = total_exp.reset_index()
total_exp = total_exp.iloc[2::3, :]
total_exp = total_exp.iloc[1:152, 1]
total_exp = total_exp.reset_index(drop=True)

welfare_exp = state_spending.iloc[37]
welfare_exp = welfare_exp.reset_index()
welfare_exp = welfare_exp.iloc[2::3, :]
welfare_exp = welfare_exp.iloc[1:152, 1]
welfare_exp = welfare_exp.reset_index(drop=True)

poverty_percent = state_stats.iloc[135]
poverty_percent = poverty_percent.reset_index()
poverty_percent = poverty_percent.iloc[2::2, :]
poverty_percent = poverty_percent.drop(labels = [18, 104])
poverty_percent = poverty_percent.iloc[:, 1]
poverty_percent = poverty_percent.reset_index(drop=True)
poverty_percent = poverty_percent.str.replace(r'\D', '').astype(float)
poverty_percent = poverty_percent / 10

unemploy_rate = state_stats.iloc[5]
unemploy_rate = unemploy_rate.reset_index()
unemploy_rate = unemploy_rate.iloc[2::2, :]
unemploy_rate = unemploy_rate.drop(labels = [18, 104])
unemploy_rate = unemploy_rate.iloc[:, 1]
unemploy_rate = unemploy_rate.reset_index(drop=True)
unemploy_rate = unemploy_rate.str.replace(r'\D', '').astype(float)
unemploy_rate = unemploy_rate / 10


prisoners = state_prisoners.iloc[0:51, :]
prisoners.columns = prisoners.iloc[0]
prisoners = prisoners.drop(prisoners.index[0])
prisoners = prisoners.sort_values("State")
prisoners = prisoners.iloc[0:51, 1]
prisoners = prisoners.reset_index(drop=True)

jailed = state_jail.loc[:,["STATE", "FINALWT", "TOTPOP"]]
jailed["jailed"] = jailed["FINALWT"] * jailed["TOTPOP"]
jailed = jailed.groupby(by="STATE")
jailed = jailed.agg(sum)
jailed = jailed.loc[:,["jailed"]]
jailed = jailed.reset_index()

state_parolees.columns.get_loc("TOTEND")
parolees = state_parolees.iloc[1:52,25]
parolees = parolees.drop(labels = 9)
parolees = parolees.reset_index(drop=True)

probationers = state_probationers.iloc[1:52,24]
probationers = probationers.drop(labels = 9)
probationers = probationers.reset_index(drop=True)


clean_data = {"state_name":state_name, 
      "state_initial":state_initial, 
      "state_num":state_num, 
      "population" : pop_2018, 
      "total_exp": total_exp,
      "welfare_exp": welfare_exp,
      "poverty_rate":poverty_percent,
      "unemploy_rate": unemploy_rate,
      "prisoners":prisoners,
      "parolees":parolees,
      "probationers":probationers
      }
clean_data = pd.DataFrame(clean_data)
clean_data = pd.merge(clean_data, jailed, how="left", left_on="state_num", right_on="STATE")
clean_data = clean_data.drop(columns= ["STATE"])
clean_data = clean_data.fillna(0)

calc_data = clean_data.loc[:, ["state_name", "state_initial", "state_num", "poverty_rate", "unemploy_rate"]]
calc_data["justice_rate"] = ((clean_data["prisoners"] + 
                                 clean_data["probationers"] + 
                                 clean_data["parolees"] + 
                                 clean_data["jailed"]) / clean_data["population"]) * 100
calc_data["welfare_perc"] = (clean_data["welfare_exp"] / clean_data["total_exp"]) * 100
calc_data["welfare_povcap"] = clean_data["welfare_exp"] / ((clean_data["poverty_rate"] / 100) * clean_data["population"])

