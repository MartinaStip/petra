import flet as ft
import os
from datetime import datetime
from datetime import date
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import seaborn as sns
import io
import base64

matplotlib.use("Agg")

# Colors
c_main = "#870765"
c_ring = "#B5B581"
c_outline = "#878760"
lw = 0.5

class CycleTracker:
    def __init__(self, csv_file='dates.csv'):
        self.csv_file = csv_file
        self.dates = None
        self.df = None
        self.load_data()
    
    def load_data(self):
        """Load data from file"""
        if os.path.exists(self.csv_file):
            self.dates = pd.read_csv(self.csv_file, header=None, names=['date'])
        else:
            self.dates = pd.DataFrame(columns=['date'])
        self.process_data()
    
    def process_data(self):
        """Process data: limit to last 3 years + calculate deltas"""
        self.dates = self.dates.sort_values("date").reset_index(drop=True)
        self.df = self.dates.copy()
        self.df['date'] = pd.to_datetime(self.df['date'], errors="coerce")
        self.df = self.df.dropna(subset=['date'])
        # Limit data to last 36 non-missing obs
        self.df = self.df.tail(36)
        self.df["delta"] = self.df['date'].diff().dt.days
        #self.df["delta"] = self.df["delta"].fillna(0).astype(int)
        self.df["delta_clean"] = np.select(
            [(self.df["delta"] > 35)],
            [np.nan],
            default = self.df["delta"])

        # Recent data for prediction = 12 non-missing deltas
        self.recent = self.df.dropna(subset=['delta_clean']).tail(12)

        # Predicted dates = last date + median/quartiles delta
        # Exact timedelta is used to get the dates
        self.delta_med = pd.Timedelta(days = self.recent["delta_clean"].quantile(0.5))
        self.delta_25 = pd.Timedelta(days = self.recent["delta_clean"].quantile(0.25))
        self.delta_75 = pd.Timedelta(days = self.recent["delta_clean"].quantile(0.75))
        
        self.pred50 = (pd.to_datetime(self.dates['date'].iloc[-1]) + self.delta_med).date()
        self.pred25 = (pd.to_datetime(self.dates['date'].iloc[-1]) + self.delta_25).date()
        self.pred75 = (pd.to_datetime(self.dates['date'].iloc[-1]) + self.delta_75).date()

        if len(self.recent) < 3:
            self.pred_date = "Not enough data"
        else:
            self.pred_date = str(self.pred50)

        # Predicted time = remaining time
        self.time_med = (self.pred50 - datetime.now().date()).days
        self.time_2575 = list(set([       # The set step is to remove duplicities 
            (self.pred25 - datetime.now().date()).days,
            (self.pred75 - datetime.now().date()).days
        ]))
    
    def add_date(self, date_str):
        """Add date, returns True if successful"""
        if date_str in self.dates['date'].values:
            return False
        
        self.dates.loc[len(self.dates)] = date_str
        self.dates = self.dates.sort_values("date").reset_index(drop=True)
        self.dates.to_csv(self.csv_file, index=False, header=False)
        self.process_data()
        return True
    
    def delete_date(self, date_str):
        """Delete date, returns True if successful"""
        if date_str not in self.dates['date'].values:
            return False
        
        self.dates = self.dates[self.dates['date'] != date_str]
        self.dates = self.dates.sort_values("date").reset_index(drop=True)
        self.dates.to_csv(self.csv_file, index=False, header=False)
        self.process_data()
        return True
    
    def plot_raw(self):
        """Create plot of raw data as base64 string"""
        if len(self.df) == 0:
            return None
        
        sns.set_style("white")
        sns.set_context("paper")
        
        fig_raw, ax = plt.subplots(figsize=(8, 4))
        ax.scatter(self.df["date"], self.df["delta_clean"], color = c_main)
        ax.set_xlabel("Date")
        ax.set_ylabel("Cycle Length (days)")
        ax.set_ylim(15, 35)
        ax.set_title("Your data")

        # This makes the line to interrupt when data are missing
        for _, group in self.df.groupby((self.df["delta_clean"].isna()).cumsum()):
            segment = group.dropna(subset=["delta_clean"])
            if not segment.empty:
                sns.lineplot(data = segment, 
                    x = "date", y = "delta_clean", 
                    linestyle = ':', color = c_ring, legend = False)

        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        plt.close(fig_raw)
        
        return base64.b64encode(buf.read()).decode()
    
    def plot_pred(self):
        """Create prediction plot as base64 string"""
        if len(self.df) <3:
            return None

        # Prediction text for plot ---
        self.time_abs = [abs(x) for x in self.time_2575]

        if self.time_2575 == [1]: 
            range = "1 day"
        elif len(self.time_2575) == 1: 
            range =  f"{self.time_2575} days"
        else:
            range = f"{min(self.time_abs)} - {max(self.time_abs)} days"

        if max(self.time_2575) < 0:
            pred_text = f"Period was due {range} ago"
        elif min(self.time_2575) <= 0 <= max(self.time_2575): 
            pred_text = f"Period is due"
        else:
            pred_text = f"Next period\nin {range}"

        # Prediction plot ---
        self.donut = [
            self.delta_med.days - self.time_med,
            self.time_med
        ]
        inner_circle = plt.Circle( (0,0), 0.7, color = 'white', ec = c_outline, linewidth = lw) # to change pie into donut 

        sns.set_style("white")
        sns.set_context("talk")
        #sns.set_context("paper")
        fig_pred, ax = plt.subplots(figsize = (8, 8))

        ax.pie(self.donut, colors = [c_ring, "white"], 
            startangle=90, counterclock=False,
            wedgeprops = {"edgecolor":c_outline,'linewidth': lw, 'linestyle': 'solid', 'antialiased': True})
        p_pred = plt.gcf() # get current figure
        p_pred.gca().add_artist(inner_circle) # get current axes + adds circle

        plt.text(0, 0,                   # coordinates (center)
            pred_text,    
            horizontalalignment = 'center',
            verticalalignment = 'center',
            fontsize = 20,
            fontweight ='bold')

        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        plt.close(fig_pred)
        
        return base64.b64encode(buf.read()).decode()


def main(page: ft.Page):
    page.title = "PEriodTRAcker"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    today = datetime.now().strftime('%Y-%m-%d')
    
    # Initialize tracker
    tracker = CycleTracker()
    
    # Navigation functions
    def navigate_to_data(e):
        page.go("/data")
    
    def navigate_to_home(e):
        page.go("/")
    
    # Event handlers
    def add_today(e):
        if not tracker.add_date(today):
            page.snack_bar = ft.SnackBar(
                content=ft.Text("Already there \N{THUMBS UP SIGN}"),
                open=True)
        else:
            page.snack_bar = ft.SnackBar(
                content=ft.Text("Date added successfully!"),
                open=True)
        route_change(page.route)
        page.update()
    
    def add_selected(e):
        date_str = e.control.value.strftime('%Y-%m-%d')
        if not tracker.add_date(date_str):
            page.snack_bar = ft.SnackBar(
                content=ft.Text("Already there \N{THUMBS UP SIGN}"),
                open=True)
        else:
            page.snack_bar = ft.SnackBar(
                content=ft.Text("Date added successfully!"),
                open=True)
        route_change(page.route)
        page.update()
    
    def delete_date_handler(date_str):
        def handler(e):
            # Confirmation dialog
            def close_dialog(e):
                dialog.open = False
                page.update()
            
            def confirm_delete(e):
                if tracker.delete_date(date_str):
                    page.snack_bar = ft.SnackBar(
                        content=ft.Text("Date deleted successfully!"),
                        open=True)
                    dialog.open = False
                    route_change(page.route)
                else:
                    page.snack_bar = ft.SnackBar(
                        content=ft.Text("Error deleting date"),
                        open=True)
                page.update()
            
            dialog = ft.AlertDialog(
                title=ft.Text("Delete Date"),
                content=ft.Text(f"Are you sure you want to delete {date_str}?"),
                actions=[
                    ft.TextButton("Cancel", on_click=close_dialog),
                    ft.TextButton("Delete", on_click=confirm_delete),
                ],
            )
            page.overlay.append(dialog)
            dialog.open = True
            page.update()
        
        return handler
    
    # Data table 
    def build_data_table():
        """Build the data table with delete buttons"""
        all_dates = tracker.dates.sort_values("date", ascending=False)['date'].tolist()
        
        if len(all_dates) == 0:
            return ft.Text("No dates recorded yet", size=16)
        
        rows = []
        for date_str in all_dates:
            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(date_str)),
                        ft.DataCell(
                            ft.IconButton(
                                icon=ft.Icons.DELETE_OUTLINE,
                                icon_color=c_main,
                                tooltip="Delete this date",
                                on_click=delete_date_handler(date_str)
                            )
                        ),
                    ]
                )
            )
        
        return ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("All recorded dates", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("", weight=ft.FontWeight.BOLD)),
            ],
            rows=rows,
        )
    
    # UI elements (buttons)
    add_today_button = ft.FilledButton(
        text="Add today",
        on_click=lambda e: add_today(e),
        style=ft.ButtonStyle(
            color=ft.Colors.WHITE, 
            bgcolor=c_main,
        )
    )

    choose_date_button = ft.FilledButton(
        text="Pick another date",
        icon=ft.Icons.CALENDAR_MONTH,
        style=ft.ButtonStyle(
            color=ft.Colors.WHITE,
            bgcolor=c_main,
        ),
        on_click=lambda e: page.open(
            ft.DatePicker(
            first_date=datetime(year=2000, month=10, day=1),
            last_date=datetime.now(),
            on_change=add_selected,
            confirm_text="Add date",
            )
        )
    )

    data_button = ft.FilledButton(
        text="View & edit data",
        icon=ft.Icons.ANALYTICS,
        on_click=navigate_to_data,
        style=ft.ButtonStyle(
        color=ft.Colors.WHITE,
        bgcolor=c_main,
        )
    )

    # Route change handler
    def route_change(route):
        page.views.clear()
        
        # Main page
        page.views.append(
            ft.View(
                "/",
                [
                    ft.AppBar(
                        title=ft.Text("PEriodTRAcker"),
                        bgcolor=c_main,
                        color=ft.Colors.WHITE,
                    ),
                    ft.Column([
                        ft.Row(
                            [ft.Text(
                                f"Estimated next date: {tracker.pred_date}", 
                                #color=c_main,
                                weight=ft.FontWeight.BOLD)],
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                        ft.Row(
                            [ft.Image(
                                src_base64=tracker.plot_pred(),
                                width=600,
                                height=300,
                            )],
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                        ft.Row(
                            [ft.Text(f"Last date: {tracker.dates['date'].iloc[-1] if len(tracker.dates) > 0 else 'N/A'}")],
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                        ft.Container(
                            content=ft.Row(
                                [add_today_button, choose_date_button],
                                alignment=ft.MainAxisAlignment.CENTER,
                            ),
                            padding=ft.padding.symmetric(vertical = 50),
                        ),
                        ft.Row(
                            [data_button],
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                    ])
                ],
            )
        )
        
        # Data page
        if page.route == "/data":
            page.views.append(
                ft.View(
                    "/data",
                    [
                        ft.AppBar(                    # just to place the back arrow, no text
                            title=ft.Text(""),
                            bgcolor=ft.Colors.WHITE,
                            color=c_main,
                            leading=ft.IconButton(
                                icon=ft.Icons.ARROW_BACK,
                                on_click=navigate_to_home
                            ),
                        ),
                        ft.Column([
                            ft.Row(
                                [ft.Image(
                                    src_base64=tracker.plot_raw(),
                                    width=600,
                                    height=300,
                                )],
                                alignment=ft.MainAxisAlignment.CENTER,
                            ),
                            ft.Row(
                                [build_data_table()],
                                #padding=20
                                alignment=ft.MainAxisAlignment.CENTER,
                            ),
                        ],
                        scroll=ft.ScrollMode.AUTO)
                    ],
                )
            )
        
        page.update()
    
    # Set up routing
    page.on_route_change = route_change
    page.go(page.route)


ft.app(main)