# Development version of Cycletracker class + its "test"
# It is not a unit test but interactive exploration
# Run the Cycletracker class from petra.py first

import os
from datetime import datetime
from datetime import date
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import seaborn as sns
import io
from IPython.display import Image, display
import base64

matplotlib.use("Qt5Agg") # to show plots interactively

#Colors and style
c_main = "#870765"
c_ring = "#9c5676"
c_outline = "black"
lw = 0.5


# Replace csv with testdata
testdata = pd.read_csv("data/testdata.csv")
testdata["date"] = pd.to_datetime(testdata['date'], format='%d.%m.%Y', errors="coerce")
testdata["date"] = testdata["date"].dt.strftime('%Y-%m-%d')
testdata.to_csv("dates.csv", index=False, header=False)

tracker = CycleTracker()

# Explore dates and df
tracker.dates

tracker.df.head()
tracker.df.tail()

tracker.recent.head()

# Cycle statistics (delta between dates)
tracker.delta_med
tracker.delta_25
tracker.delta_75

# Prediction
tracker.dates['date'].iloc[-1]
tracker.pred_date
tracker.time_med
tracker.time_2575




# Prediction plot ---
donut = [
    tracker.delta_med.days - tracker.time_med,
    tracker.time_med
]
inner_circle = plt.Circle( (0,0), 0.7, color = 'white', ec = c_outline, linewidth = lw) # to change pie into donut 

sns.set_style("white")
sns.set_context("talk")
#sns.set_context("paper")
fig, ax = plt.subplots(figsize = (8, 8))

ax.pie(donut, colors = [c_main, "white"], 
    startangle=90, counterclock=False,
    wedgeprops = {"edgecolor":c_outline,'linewidth': lw, 'linestyle': 'solid', 'antialiased': True})
p_pred = plt.gcf() # get current figure
p_pred.gca().add_artist(inner_circle) # get current axes + adds circle

plt.text(0, 0,                   # coordinates (center)
    pred_text,    
    horizontalalignment='center',
    verticalalignment='center',
    fontsize=14,
    fontweight='bold')

plt.show()

# Test prediction plot
display(Image(base64.b64decode(tracker.plot_pred())))

# Raw data plot ---
# Limit to last 3 years
display(Image(base64.b64decode(tracker.plot_raw())))

fig, ax = plt.subplots(figsize=(8, 4))
ax.scatter(tracker.df["date"], tracker.df["delta_clean"], color = c_main)
ax.set_xlabel("Date")
ax.set_ylabel("Cycle Length (days)")
ax.set_title("Your data")
ax.set_ylim(15, 35)

# This makes the line to interrupt when data are missing
for _, group in tracker.df.groupby((tracker.df["delta_clean"].isna()).cumsum()):
    segment = group.dropna(subset = ["delta_clean"])
if not segment.empty:
    sns.lineplot(data = segment, 
        x = "date", y = "delta_clean", 
        linestyle = ':', color = c_ring, legend = False)








