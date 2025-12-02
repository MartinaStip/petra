from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Preliminary code for my CycleTracker class

# Visual style -----------------------------------------------------
c_main = "#8f1029"
c_outline = "black"
lw = 0.5


# Intro -------------------------------------------------------------
# Read data + intro settings
df = pd.read_csv("data/testdata.csv")
df["date"] = pd.to_datetime(df["date"], format="%d.%m.%Y")
df = df.sort_values(by = "date") 

# Cycle length -------------------------------------------------------
# Delta = cycle length
df["delta"] = df['date'].diff().dt.days.dropna()

# Delta clean = splits series if cycle is unusually long 
# This may be due to omitted recording, pregnancy, medical treatment etc. 
# I dont want to speculate about the cause and try to fix possible omission
df["delta_clean"] = np.select(
    [(df["delta"] > 35)],
    [np.nan],
    default = df["delta"])

# Raw data visualisation ---------------------------------------------------
sns.set_style("white")
#sns.set_context("talk")
sns.set_context("paper")

cyclelength_min = df["delta_clean"].min()
cyclelength_max = df["delta_clean"].max() # max length of cycle is set when defining delta_clean 

fig, ax = plt.subplots(figsize=(8, 4))
ax.scatter(df["date"], df["delta_clean"], color = c_main)
ax.set_xlabel("Date")
ax.set_ylabel("Cycle length (days)")
ax.set_title("Your data")

# This makes the line to interrupt when data are missing
for _, group in df.groupby((df["delta_clean"].isna()).cumsum()):
    segment = group.dropna(subset=["delta_clean"])
    if not segment.empty:
        sns.lineplot(data = segment, 
            x = "date", y = "delta_clean", 
            linestyle = ':', color = c_main, legend = False)

# plt.clf()
# sns.scatterplot(data=df, x = "date", y = "delta_clean", 
#     color = c_main)  
# plt.title("Your data")
# plt.ylim(cyclelength_min - 1, cyclelength_max + 1)  # set y-axis limits
# sns.despine(left = False, bottom = True) # Remove top/right/left/bottom spines (frame)
# plt.ylabel("Length of cycle")
# plt.xlabel("")
# plt.show()

# Prediction---------- --------------------------------------------------------
# Moving median: 10 preceding cycles
df["mm"] = df["delta_clean"].rolling(window = 10, min_periods = 2).median().shift(1)
df["pred_mm"] = df["date"] + pd.to_timedelta(df["mm"], unit = "d")

# Moving average: 10 preceding cycles
df["mavg"] = df["delta_clean"].rolling(window = 10, min_periods = 2).mean().shift(1)
df["pred_mavg"] = df["date"] + pd.to_timedelta(df["mavg"], unit = "d")

# Compute errors MAKE IT A LOOP
df["err_mm"] = np.select([np.isnan(df["delta_clean"].shift(-1))],
    [np.nan],
    default = (df["pred_mm"] - df["date"].shift(-1)).dt.days) 

df["err_mavg"] = np.select([np.isnan(df["delta_clean"].shift(-1))],
    [np.nan],
    default = (df["pred_mavg"] - df["date"].shift(-1)).dt.days)

# Errors dataframe: mae = mean absolute error, rmse = root mean squared error
# rmse penalizes large error more
# only the last 12 predictions are evaluated to base the choice of prediction method on current data
methods = [c.replace("pred_", "") for c in df.columns if c.startswith("pred_")]

errors = pd.DataFrame({"method" : methods,
    "mae" : np.nan,
    "rmse" : np.nan})

# AUTOMATE THIS
errors.loc[errors["method"] == "mm","mae"] = df["err_mm"].abs().mean()
errors.loc[errors["method"] == "mm","rmse"] = np.sqrt((df["err_mm"] ** 2).mean())

errors.loc[errors["method"] == "mavg","mae"] = df["err_mavg"].abs().mean()
errors.loc[errors["method"] == "mavg","rmse"] = np.sqrt((df["err_mavg"] ** 2).mean())

# Pick method with the lowest error
best_method = errors.loc[errors["mae"].idxmin(), "method"]

# Current prediction
prediction = df[f"pred_{best_method}"].iloc[-1]

# Last + pred date visualisation -------------------------------------------
#c_main = "blue"
#c_outline = "black"
#lw = 0.5

today = datetime.today()
pred_dist = int((prediction - today).days)

donut = [
    int((today - df["date"].iloc[-1]).days),
    max(0, pred_dist)
]

# Prediction text
day_word = "day" if abs(pred_dist) == 1 else "days"
if int((prediction - today).days) < 0:
    pred_text = f"Period was due {abs(pred_dist)} {day_word} ago"
else:
    pred_text = f"Next period\nin {pred_dist} {day_word}"

inner_circle = plt.Circle( (0,0), 0.7, color = 'white', ec = c_outline, linewidth = lw) # to change pie into donut 

sns.set_style("white")
sns.set_context("talk")
#sns.set_context("paper")
fig, ax = plt.subplots(figsize=(8, 8))

ax.pie(donut, colors = ["blue", "white"], 
    wedgeprops = {"edgecolor":c_outline,'linewidth': lw, 'linestyle': 'solid', 'antialiased': True})
p_pred = plt.gcf() # get current figure
p_pred.gca().add_artist(inner_circle) # get current axes + adds circle

plt.title("Estimated next date: " + str(prediction.date()) + 
    "\nLast date: " + str(df.loc[df.index[-1], "date"].date()) )

plt.text(0, 0,                   # coordinates (center)
    pred_text,    
    horizontalalignment='center',
    verticalalignment='center',
    fontsize=14,
    fontweight='bold')

plt.show()

# # Viz of aggregated trends --------------------------------------------------
# plt.clf()
# sns.lineplot(df, x = "date", y = "mm", 
#     errorbar = None, legend = False)
# plt.ylim(15, 40)  # set y-axis limits    
# plt.show()


# plt.clf()
# sns.lineplot(df, x = "date", y = "mavg", 
#     errorbar = None, legend = False)

# plt.ylim(15, 40)  # set y-axis limits    
# plt.show()


