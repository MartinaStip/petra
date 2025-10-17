from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Intro -------------------------------------------------------------
# Read data + intro settings
df = pd.read_csv("data/testdata.csv")
df["date"] = pd.to_datetime(df["date"], format="%d.%m.%Y")
df = df.sort_values(by = "date")
df["is_interpolated"] = False

# Cycle length + series characteristics ------------------------------
# Delta = cycle length
df["delta"] = df['date'].diff().dt.days.dropna()

# Delta clean = splits series if cycle is unusually long 
df["delta_clean"] = np.select(
    [(df["delta"] > 35)],
    [np.nan],
    default = df["delta"])

# Day of year
df["day"] = df["date"].dt.dayofyear

# Year
df["year"] = df["date"].dt.year

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
prediction = df.loc[df.index[-1],"pred_"+ best_method]

# Last + pred date visualisation -------------------------------------------
c_main = "blue"
today = datetime.today()
donut = [
    int((today - df.loc[df.index[-1], "date"]).days),
    int((prediction - today).days)
]

inner_circle = plt.Circle( (0,0), 0.7, color = 'white') # to change pie into donut 

sns.set_style("white")
sns.set_context("talk")
#sns.set_context("paper")


plt.clf()
plt.pie(donut)
p = plt.gcf()
p.gca().add_artist(inner_circle)


plt.show()

# Raw data visualisation ---------------------------------------------------
sns.set_style("white")
#sns.set_context("talk")
sns.set_context("paper")

df["theta"] = 2 * np.pi * df["day"] / df["day"].max()

# Create polar plot
fig, ax = plt.subplots(subplot_kw={'projection': 'polar'}, figsize=(8, 8))


plt.clf()
sns.lineplot(df, x = "theta", y = "delta_clean", 
    hue = "year", 
    #sizes=(1, 5),
    errorbar = None, estimator = None)

# PREKLRESLIT PRES TO BREAKS BILOU BARVOU, ABY TO BYLO DOTTED?
sns.lineplot(df, x = "day", y = "delta_clean", 
    hue = "year", 
    errorbar = None, linestyle=':', legend = False)

sns.scatterplot(data=df, x="day", y="delta_clean",
    hue="year", size="year", sizes=(50, 200),
    legend = False)  

#plt.ylim(15, 40)  # set y-axis limits
plt.title("Length of cycles")

sns.despine(left = False, bottom = True) # Remove top/right/left/bottom spines (frame)
plt.ylabel("")
plt.xlabel("Time in calendar year")
plt.gca().xaxis.set_visible(False) # Remove x-axis completely

plt.show()


# Prediction ----------------------------------------------------------------



# Rests ------------------------------------------------------
# Series status:
# start, end = start and end of continual series
# mid = inside continual series
df["series_status"] = np.select([(pd.isna(df["delta"]) | (df["delta"] > 35)), 
    (pd.isna(df["delta_lead"]) | (df["delta_lead"] > 35))],
    ["start", "end"],
    default = "mid"
    )

# df["delta_lead"] = df['delta'].shift(-1)

# # index = index within a 12-cycle sets
# df["index"] = np.concatenate(
#     [np.arange(13 - len(df) % 12, 13, 1),
#     np.tile(np.arange(1, 13, 1), len(df)//12)])  