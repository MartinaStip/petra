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
    
    def plot_current_cycle(self, ax=None):
        """Plot donut chart showing progress in current cycle
        Args:
            ax: Optional matplotlib axis. If None, creates new figure and shows it
        Returns:
            ax if provided, otherwise None
        """
        # Refresh data
        self.refresh()
        
        # Check if prediction is available
        if self.pred is None:
            if ax is None:
                print("Not enough data for prediction")
                return
            else:
                ax.text(0.5, 0.5, "Add at least 2 periods\nfor prediction", 
                       ha='center', va='center', transform=ax.transAxes, fontsize=12)
                return ax
        
        c_outline = "black"
        lw = 0.5
        c_main = "#84127f"
        
        today = datetime.today()
        days_since = int((today - self.last).days)
        days_until = int((self.pred - today).days)
        
        # Handle negative days_until (overdue)
        if days_until < 0:
            donut = [days_since, 0]
        else:
            donut = [days_since, days_until]
        
        # Create axis if not provided
        if ax is None:
            fig, ax = plt.subplots(figsize=(6, 6))
            show_plot = True
        else:
            show_plot = False
        
        # Create donut chart
        wedges, _ = ax.pie(donut, colors=[c_main, "white"], 
                          wedgeprops={"edgecolor": c_outline, 'linewidth': lw, 
                                     'linestyle': 'solid', 'antialiased': True})
        
        # Add inner circle for donut effect
        inner_circle = plt.Circle((0, 0), 0.7, color='white', ec=c_outline, linewidth=lw)
        ax.add_artist(inner_circle)
        
        # Title with dates
        ax.set_title(f"Next: {self.pred.date()}\nLast: {self.last.date()}", fontsize=10, pad=10)
        
        # Center text
        if days_until >= 0:
            center_text = f"Next period\nin {days_until} days"
        else:
            center_text = f"Period overdue\nby {abs(days_until)} days"
        
        ax.text(0, 0, center_text,
               ha='center', va='center', fontsize=14, fontweight='bold')
        
        if show_plot:
            sns.set_style("white")
            sns.set_context("talk")
            plt.tight_layout()
            plt.show()
        
        return ax
    
    def plot_series(self, ax=None):
        """Plot cycle lengths over time
        Args:
            ax: Optional matplotlib axis. If None, creates new figure and shows it
        Returns:
            ax if provided, otherwise None
        """
        # Refresh data
        self.refresh()
        
        # Check if there's data
        if self.df["delta_clean"].dropna().empty:
            if ax is None:
                print("Not enough data to plot")
                return
            else:
                ax.text(0.5, 0.5, "Not enough data to plot", 
                       ha='center', va='center', transform=ax.transAxes)
                return ax
        
        cyclelength_min = self.df["delta_clean"].min()
        cyclelength_max = self.df["delta_clean"].max()
        c_main = "#84127f"
        
        # Create axis if not provided
        if ax is None:
            fig, ax = plt.subplots(figsize=(10, 6))
            show_plot = True
        else:
            show_plot = False
        
        # Plot line segments (interrupted where data is missing)
        for _, group in self.df.groupby((self.df["delta_clean"].isna()).cumsum()):
            segment = group.dropna(subset=["delta_clean"])
            if not segment.empty:
                ax.plot(segment["date"], segment["delta_clean"], 
                       linestyle=':', color=c_main, marker='o', markersize=6)
        
        ax.set_title("Cycle Length Over Time", fontweight='bold')
        ax.set_ylabel("Length of cycle (days)")
        ax.set_xlabel("")
        ax.set_ylim(cyclelength_min - 1, cyclelength_max + 1)
        ax.grid(True, alpha=0.3)
        
        if show_plot:
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.show()
        
        return ax


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
    print(f"Predicted next: {predictor.predicted_date().date() if predictor.predicted_date() else 'Not enough data'}")
    
    print("\nShowing current cycle chart...")
    visualizer.plot_current_cycle()  # Opens in new window
    
    print("\nShowing cycle series chart...")
    visualizer.plot_series()  # Opens in new window