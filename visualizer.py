import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

class Visualizer:
    def __init__(self, predictor):
        self.predictor = predictor
        self.df = self.predictor.df()
        self.last = self.predictor.last_date()
        self.pred = self.predictor.predicted_date()
    
    def plot_current_cycle(self):
        c_outline = "black"
        lw = 0.5

        today = datetime.today()
        donut = [
            int((today - self.last).days),
            int((self.pred - today).days)
        ]

        inner_circle = plt.Circle( (0,0), 0.7, color = 'white', ec = c_outline, linewidth = lw) # to change pie into donut 

        sns.set_style("white")
        sns.set_context("talk")

        plt.clf()
        plt.pie(donut, colors = ["blue", "white"], 
            wedgeprops = {"edgecolor":c_outline,'linewidth': lw, 'linestyle': 'solid', 'antialiased': True})
        p_pred = plt.gcf() # get current figure
        p_pred.gca().add_artist(inner_circle) # get current axes + adds circle

        plt.title("Estimated next date: " + str(prediction.date()) + 
            "\nLast date: " + str(df.loc[df.index[-1], "date"].date()) )

        plt.text(0, 0,                   # coordinates (center)
            "Next period\nin " + str(int((prediction - today).days)) + " days",    
            horizontalalignment='center',
            verticalalignment='center',
            fontsize=14,
            fontweight='bold')

        plt.show()

    def plot_series(self):
        cyclelength_min = self.df["delta_clean"].min()
        cyclelength_max = self.df["delta_clean"].max() # max length of cycle is set when defining delta_clean 
        c_main = "#84127f"

        plt.clf()
        # This makes the line to interrupt when data are missing
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
    
    dm = DataManager()
    visualizer = Visualizer(dm)
    
    # Add sample data with one interpolated
    dm.add_period('2024-01-15', is_interpolated=False)
    dm.add_period('2024-02-12', is_interpolated=False)
    dm.add_period('2024-03-10', is_interpolated=False)
    dm.add_period('2024-04-08', is_interpolated=False)
    dm.add_period('2024-05-06', is_interpolated=False)
    dm.add_period('2024-06-05', is_interpolated=True)  # Interpolated
    dm.add_period('2024-07-02', is_interpolated=False)
    
    print("Trend:", visualizer.get_trend_description())
    print("\nShowing cycle length chart...")
    visualizer.plot_cycle_lengths()
    
    print("\nShowing trend chart...")
    visualizer.plot_cycle_trend()