from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from data_manager import DataManager

class Predictor:
    def __init__(self, data_manager):
        self.data_manager = data_manager
        self.df = self.create_df()

    def create_df(self):
        """Create pandas df from raw data 
        Columns: date, delta, delta_clean
        """
        cyclelength_max = 35 # max allowed cycle length to treat the series as continual

        df = pd.read_csv(self.data_manager.get_file_path())
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values(by = "date") 

        # Cycle length
        df["delta"] = df['date'].diff().dt.days
        # delta clean splits series if cycle is unusually long 
        # This may be due to omitted recording, pregnancy, medical treatment etc. 
        # I dont want to speculate about the cause and try to fix possible omission
        df["delta_clean"] = np.select(
            [(df["delta"] > cyclelength_max)],
            [np.nan],
            default = df["delta"])
        
        # Prediction
        df["mm"] = df["delta_clean"].rolling(window = 10, min_periods = 2).median().shift(1)
        df["pred_mm"] = df["date"] + pd.to_timedelta(df["mm"], unit = "d")

        return df

    def refresh_data(self):
        """Reload data from file"""
        self.df = self.create_df()

    def last_date(self):
        """Return last recorded date"""
        return self.df["date"].iloc[-1]

    def predicted_date(self):
        """Return current predicted date"""
        predicted_date = self.df["pred_mm"].iloc[-1]
        
        if pd.isna(predicted_date):
            return None

        return predicted_date.date()
   
# Test
if __name__ == '__main__':
   dm = DataManager()
   predictor = Predictor(dm)
   
   # Add some sample periods
   print("Adding periods...")
   dm.add_period('2024-01-15')
   dm.add_period('2024-02-12')
   dm.add_period('2024-03-10')
   dm.add_period('2024-04-08')
   
   predictor.refresh_data() 

   print(f"Last date: {predictor.last_date()}")
   print(f"Predicted date: {predictor.predicted_date()}")
    
 
xx = predictor.predicted_date()
