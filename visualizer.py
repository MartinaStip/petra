import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from datetime import datetime

class Visualizer:
    def __init__(self, predictor):
        self.predictor = predictor
        self.df = self.predictor.df
        self.last = self.predictor.last_date()
        self.pred = self.predictor.predicted_date()
    
    def refresh(self):
        """Refresh data from predictor"""
        self.df = self.predictor.df
        self.last = self.predictor.last_date()
        self.pred = self.predictor.predicted_date()

    def plot_current_cycle(self):
        c_outline = "black"
        lw = 0.5
        c_main = "#84127f"

        # Refresh data
        self.refresh()

        # Check if prediction is available
        if self.pred is None:
            print("Not enough data for prediction")
            return

        self.df = self.predictor.df # Refresh before plotting
        today = datetime.today()
        days_since = int((today - self.last).days)
        days_until = int((self.pred - today).days)

        # Handle negative days_until (overdue)
        if days_until < 0:
            donut = [days_since, 0]
        else:
            donut = [days_since, days_until]

        donut = [12,15]
        inner_circle = plt.Circle( (0,0), 0.7, color = 'white', ec = c_outline, linewidth = lw) # to change pie into donut 

        sns.set_style("white")
        sns.set_context("talk")

        plt.clf()
        plt.pie(donut, colors = [c_main, "white"], 
            wedgeprops = {"edgecolor":c_outline,'linewidth': lw, 'linestyle': 'solid', 'antialiased': True})
        p_pred = plt.gcf() # get current figure
        p_pred.gca().add_artist(inner_circle) # get current axes + adds circle

        # plt.title(f"Estimated next date: {str(self.pred.date())}\nLast date: {str(self.last_date())}")

        # Center text
        if days_until >= 0:
            center_text = f"Next period\nin {days_until} days"
        else:
            center_text = f"Period overdue\nby {abs(days_until)} days"

        # plt.text(0, 0,  center_text,
        #     horizontalalignment='center',
        #     verticalalignment='center',
        #     fontsize=14,
        #     fontweight='bold')

        plt.show()

    def plot_series(self):
        """Plot cycle lengths over time"""
        # Refresh data
        self.refresh()
        
        # Check if there's data
        if self.df["delta_clean"].dropna().empty:
            print("Not enough data to plot")
            return

        self.df = self.predictor.df  # Refresh before plotting
        cyclelength_min = self.df["delta_clean"].min()
        cyclelength_max = self.df["delta_clean"].max() # max length of cycle is set when defining delta_clean 
        c_main = "#84127f"

        plt.clf()
         # Plot line segments (interrupted where data is missing)
        for _, group in self.df.groupby((self.df["delta_clean"].isna()).cumsum()):
            segment = group.dropna(subset=["delta_clean"])
            if not segment.empty:
                sns.lineplot(data = segment, 
                    x = "date", y = "delta_clean", 
                    linestyle = ':', color = c_main, legend = False)

        sns.scatterplot(data = self.df, x = "date", y = "delta_clean", 
        color = c_main)  

        plt.title("Your data")
        plt.ylim(cyclelength_min - 1, cyclelength_max + 1)  # set y-axis limits
        sns.despine(left = False, bottom = True) # Remove top/right/left/bottom spines (frame)
        plt.ylabel("Length of cycle")
        plt.xlabel("")

        plt.show()

# Test
if __name__ == '__main__':
    from data_manager import DataManager
    from predictor import Predictor
    
    # Setup
    dm = DataManager()
    
    # Add sample data
    print("Adding sample periods...")
    dm.add_period('2024-01-15')
    dm.add_period('2024-02-12')
    dm.add_period('2024-03-10')
    dm.add_period('2024-04-08')
    dm.add_period('2024-05-06')
    dm.add_period('2024-06-05')
    dm.add_period('2024-07-02')
    dm.add_period('2024-07-30')
    dm.add_period('2024-08-28')
    dm.add_period('2024-09-26')
    
    # Create predictor and visualizer
    predictor = Predictor(dm)
    visualizer = Visualizer(predictor)
    
    print(f"\nLast period: {predictor.last_date().date()}")

    if predictor.predicted_date():
        print(f"Predicted next period: {predictor.predicted_date().date()}")  
    else:
        print('Not enough data')
    
    print("\nShowing current cycle chart...")
    visualizer.plot_current_cycle()
    
    print("\nShowing cycle series chart...")
    visualizer.plot_series()
