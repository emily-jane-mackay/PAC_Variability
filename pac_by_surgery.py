#%%
import os
import re
import pandas as pd
import numpy as np
dirname = os.path.dirname(__file__)

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.cbook as cbook
from matplotlib import ticker
import seaborn as sns 

from matplotlib.ticker import PercentFormatter


pd.set_option('display.max_columns', 200)
pd.set_option('display.max_rows', 200)

#%%
# load dataset 
pac=pd.read_csv(
    filepath_or_buffer=os.path.join(dirname, "data", "data.csv"),
    index_col=False
)
print(pac)

# %%
# Clean data
df = pac.dropna(how='all')  # Remove fully empty rows
df.columns = df.columns.str.strip()  # Clean column names
df = df.drop(columns=['Unnamed: 1', 'Total'])  # Drop unused columns

# Extract numeric values from 'PAC' and 'No PAC' columns
df['PAC'] = df['PAC'].str.extract(r'(\d[\d,]*)')[0].str.replace(',', '').astype(int)
df['No PAC'] = df['No PAC'].str.extract(r'(\d[\d,]*)')[0].str.replace(',', '').astype(int)

# Calculate percentages
df['PAC %'] = df['PAC'] / (df['PAC'] + df['No PAC']) * 100
df['No PAC %'] = df['No PAC'] / (df['PAC'] + df['No PAC']) * 100

#%%
# Custom surgery labels (edit as needed)
custom_labels = {
    'isolated_cabg': 'Isolated CABG',
    'cabg': '+ CABG',
    'mv_repair': 'MV Repair',
    'mv_replace': 'MV Replace',
    'tricuspid': 'Tricuspid',
    'pulmonic': 'Pulmonic',
    'av_replace': 'AV Replace',
    'avss_av_repair': 'AV Repair / AVSS',
    'aortic_prox': 'Prox. Aortic',
    'aortic_desc': 'Desc. Aortic',
    'lung_tx': 'Lung Transplant',
    'heart_tx': 'Heart Transplant',
    'redo': 'Redo Sternotomy'
}
df['Surgery Label'] = df['Surgery'].map(custom_labels)


#%% 
# Flip order (descending by PAC %)
df_flipped = df.sort_values(by='PAC %', ascending=False).reset_index(drop=True)

# Set style
sns.set_theme(style="whitegrid", font_scale=1.1)

# Create the stacked horizontal bar plot
fig, ax = plt.subplots(figsize=(10, 6))
ax.barh(df_flipped['Surgery Label'], df_flipped['PAC %'], color="#1f77b4", edgecolor='black', label='PAC')
ax.barh(df_flipped['Surgery Label'], df_flipped['No PAC %'], left=df_flipped['PAC %'], color="#ffbf46", edgecolor='black', label='No PAC')

# Axis formatting
ax.set_title('PAC vs No PAC Use (%) by Surgery Type', fontsize=14)
ax.set_xlabel('Percentage of Patients')
ax.set_ylabel('Surgery Type')
ax.xaxis.set_major_formatter(PercentFormatter())
ax.set_xlim(0, 100)
ax.legend(loc='lower right')

plt.tight_layout()

# Add larger % labels inside the bars
for i, row in df_flipped.iterrows():
    if row['PAC %'] > 5:
        ax.text(row['PAC %'] / 2, i, f"{row['PAC %']:.1f}%", color='white', ha='center', va='center', fontsize=10)
    if row['No PAC %'] > 5:
        ax.text(row['PAC %'] + row['No PAC %'] / 2, i, f"{row['No PAC %']:.1f}%", color='black', ha='center', va='center', fontsize=10)

# Move legend to upper right
ax.legend(loc='upper right', frameon=True)

# Move legend outside top-right of the plot
# ax.legend(
#   loc='upper left',
#   bbox_to_anchor=(1.01, 1),
#   borderaxespad=0,
#   frameon=True,
#   title='Monitoring'
#)


# Export to high-resolution formats
fig.savefig("pac_use_stacked_by_surgery.png", dpi=600)
fig.savefig("pac_use_stacked_by_surgery.pdf", format='pdf')
fig.savefig("pac_use_stacked_by_surgery.svg", format='svg')  # Editable vector format

plt.show()

#%% 











