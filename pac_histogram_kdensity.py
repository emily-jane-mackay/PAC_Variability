#%%
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

import os
import re
import pandas as pd
import numpy as np
dirname = os.path.dirname(__file__)

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.cbook as cbook
from matplotlib import ticker

from matplotlib.ticker import PercentFormatter

pd.set_option('display.max_columns', 200)
pd.set_option('display.max_rows', 200)

#%%
# load dataset 
df=pd.read_csv(
    filepath_or_buffer=os.path.join(dirname, "data", "data.csv"),
    index_col=False
)
# %%

# Use modern seaborn theme setter
sns.set_theme(style="whitegrid")

# Convert proportions to percentages
df['pac_rate_provider_pct'] = df['pac_rate_provider'] * 100
df['pac_rate_pct'] = df['pac_rate'] * 100

# Create the plot
fig, ax = plt.subplots(figsize=(10, 6))
sns.histplot(df['pac_rate_provider_pct'], color="skyblue", label='Anesthesiologist PAC Rate', kde=True, bins=30, alpha=0.6, ax=ax)
sns.histplot(df['pac_rate_pct'], color="orange", label='Hospital PAC Rate', kde=True, bins=30, alpha=0.6, ax=ax)

# Customize labels and format
ax.set_title('Distribution of PAC Use Rates by Anesthesiologist and Hospital', fontsize=14)
ax.set_xlabel('PAC Use Rate (%)', fontsize=12)
ax.set_ylabel('Count', fontsize=12)
ax.xaxis.set_major_formatter(PercentFormatter(xmax=100))
ax.legend()
plt.tight_layout()

# Export to high-resolution formats
fig.savefig('pac_rates_hist_kden.png', dpi=300)
fig.savefig('pac_rates_hist_kden.pdf')  # PDF is vector by default
fig.savefig('pac_rates_hist_kden.svg')  # SVG is vector-editable

# Show plot
plt.show()
# %%
