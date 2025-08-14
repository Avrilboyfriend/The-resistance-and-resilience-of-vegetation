# -*- coding: utf-8 -*-
# @Author: GEE hub
# @Date:   2024-06-11 21:13:22
# @Last Modified by:   99382
# @Last Modified time: 2025-08-14 21:42:59
# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
def yday_to_int(yday_str):
    return int(yday_str)
def calculate_resistance_resilience(df):
"""
Calculate the resistance and resilience of vegetation (with a recovery period of 2 months)
    
Parameters:
Df (pd. DataFrame): A DataFrame that contains all data
        
return:
Pd.DataFrame: A new DataFrame containing resistance and resilience results
"""
#Prepare result storage
    results = []
    df['date'] = df['date'].astype(int)
    drought_dates = df[df['FlashDrought'] == True]['date'].unique()
    VR_GPP = df[df['FlashDrought'] == False]['GPP'].mean()
    VR_SIF = df[df['FlashDrought'] == False]['SIF'].mean()  
    for drought_date in drought_dates:
        year = int(str(drought_date)[:4])
        doy = int(str(drought_date)[4:])
        drought_dt = datetime(year, 1, 1) + timedelta(days=doy-1)
        drought_start = drought_dt - timedelta(days=24)
        drought_end = drought_dt + timedelta(days=24)
        start_yday = int(drought_start.strftime('%Y%j'))
        end_yday = int(drought_end.strftime('%Y%j'))   
        mask = (df['date'] >= start_yday) & (df['date'] <= end_yday)
        V0_GPP = df[mask]['GPP'].mean()
        V0_SIF = df[mask]['SIF'].mean()
        recovery_dt = drought_dt + timedelta(days=60)
        recovery_start = recovery_dt - timedelta(days=24)
        recovery_end = recovery_dt + timedelta(days=24)
        recovery_start_yday = int(recovery_start.strftime('%Y%j'))
        recovery_end_yday = int(recovery_end.strftime('%Y%j'))
        mask = (df['date'] >= recovery_start_yday) & (df['date'] <= recovery_end_yday)
        Vn_GPP = df[mask]['GPP'].mean()
        Vn_SIF = df[mask]['SIF'].mean()
        def resistance(VR, V0):
            numerator = 2 * abs(VR - V0)
            denominator = VR + abs(VR - V0)
            return 1 - (numerator / denominator) if denominator != 0 else np.nan
        res_GPP = resistance(VR_GPP, V0_GPP)
        res_SIF = resistance(VR_SIF, V0_SIF)
        def resilience(VR, V0, Vn):
            numerator = 2 * abs(VR - V0)
            denominator = abs(VR - V0) + abs(VR - Vn)
            return (numerator / denominator - 1) if denominator != 0 else np.nan      
        resi_GPP = resilience(VR_GPP, V0_GPP, Vn_GPP)
        resi_SIF = resilience(VR_SIF, V0_SIF, Vn_SIF)
        results.append({
            'drought_date': drought_date,
            'VR_GPP': VR_GPP,
            'VR_SIF': VR_SIF,
            'V0_GPP': V0_GPP,
            'V0_SIF': V0_SIF,
            'Vn_GPP': Vn_GPP,
            'Vn_SIF': Vn_SIF,
            'Resistance_GPP': res_GPP,
            'Resistance_SIF': res_SIF,
            'Resilience_GPP': resi_GPP,
            'Resilience_SIF': resi_SIF
        })
    return pd.DataFrame(results)
df = pd.read_excel('your file/.xlsx')
result_df = calculate_resistance_resilience(df)
result_df.to_excel('your output file/.xlsx', index=False)