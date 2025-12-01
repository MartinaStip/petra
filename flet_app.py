import flet as ft
import os
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import seaborn as sns

matplotlib.use("svg")

def main(page: ft.Page):
    page.title = "Main page"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    # Colors
    c_main = "#b80d62"

    # Raw data ---
    today = datetime.now().strftime('%Y-%m-%d')
    
    #csv_file = "dates.csv"
    
    if os.path.exists('dates.csv'):
        dates = pd.read_csv("dates.csv", header = None, names = ['date'])
    else:
        dates = pd.DataFrame(columns=['date'])

    # Data processing (df = processed data) ---
    df = dates.copy()

    # Delta = cycle length
    df['date'] = pd.to_datetime(df['date'], errors="coerce")
    df = df.dropna(subset=['date'])
    df["delta"] = df['date'].diff().dt.days
    df["delta"] = df["delta"].fillna(0).astype(int)

    cyclelength_min = max(15, min(df["delta"]))
    cyclelength_max = 35

# Delta clean = splits series if cycle is unusually long 
# This may be due to omitted recording, pregnancy, medical treatment etc. 
# I dont want to speculate about the cause and try to fix possible omission
    df["delta_clean"] = np.select(
        [(df["delta"] > 35)],
        [np.nan],
        default = df["delta"])

    # Raw data plot ---
    sns.set_style("white")
    #sns.set_context("talk")
    sns.set_context("paper")

    fig_raw, ax = plt.subplots()
    sns_plot = ft.MatplotlibChart(fig_raw, expand=True)
    ax.scatter(df["date"], df["delta_clean"])

    # Functions with classical parameters (not events)
    def add_date(selected_date):
        if selected_date in dates['date'].values:
            return False
        else:
            dates.loc[len(dates)] = selected_date
            dates = dates.sort_values("date")
            dates.to_csv('dates.csv', index = False)
            return True

    # Event handlers (functions of what happens after an event) ---
      # Add today
    def add_today(e):
        if not add_date(today): # This executes the function first (i.e. date is added if not already there)
            # Show message for duplicate date
            print("Duplicate detected!") 
            page.snack_bar = ft.SnackBar(
                content = ft.Text("Already there \N{THUMBS UP SIGN}"),
                open = True)
        page.update()

    # Add date picked from calendar
    def add_selected(e):
         if not add_date(e.control.value.strftime('%Y-%m-%d')):
            page.snack_bar = ft.SnackBar(
                content = ft.Text("Already there \N{THUMBS UP SIGN}"),
                open = True)
         page.update()

    # UI elements to be placed in the layout below ---
    # Controls = buttons, text fields etc.
    add_today_button = ft.FilledButton(
        text="Add today",
        #icon = ft.Icons.ADD_OUTLINED,
        on_click = add_today,
        style = ft.ButtonStyle(
            color = ft.Colors.WHITE,
            bgcolor = c_main,
        )
    )

    # choose date button opens a calendar dialogue
    choose_date = ft.FilledButton(
        text = "Pick another date",
        icon=ft.Icons.CALENDAR_MONTH,
        style = ft.ButtonStyle(
            color = ft.Colors.WHITE,
            bgcolor = c_main,
        ),
        on_click = lambda e: page.open(
            ft.DatePicker(
                first_date = datetime(year=2000, month=10, day=1),
                last_date = datetime(year=int(today[0:4]), month = int(today[5:7]), day = int(today[8:10])),
                on_change = add_selected,
                confirm_text = "Add date",
            )
        )
    )

    # Outline of the page + liking event handlers to the events ---
    page.add(
        ft.Row(
            [
                add_today_button,
                choose_date,
                ft.MatplotlibChart(fig_raw, expand=True)
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        )
    )

# Run the app
ft.app(main)

# Test in terminal
# C:\Users\mmars\AppData\Local\Python\pythoncore-3.14-64\Scripts\flet.exe run D:\github\petra\flet_app.py
# flet run --android 


# # Raw data visualisation ---------------------------------------------------
# sns.set_style("white")
# #sns.set_context("talk")
# sns.set_context("paper")

# cyclelength_min = df["delta_clean"].min()
# cyclelength_max = df["delta_clean"].max() # max length of cycle is set when defining delta_clean 

# plt.clf()
# # This makes the line to interrupt when data are missing
# for _, group in df.groupby((df["delta_clean"].isna()).cumsum()):
#     segment = group.dropna(subset=["delta_clean"])
#     if not segment.empty:
#         sns.lineplot(data = segment, 
#             x = "date", y = "delta_clean", 
#             linestyle = ':', color = c_main, legend = False)

# sns.scatterplot(data=df, x = "date", y = "delta_clean", 
#     color = c_main)  

# plt.title("Your data")
# plt.ylim(cyclelength_min - 1, cyclelength_max + 1)  # set y-axis limits
# sns.despine(left = False, bottom = True) # Remove top/right/left/bottom spines (frame)
# plt.ylabel("Length of cycle")
# plt.xlabel("")

# plt.show()