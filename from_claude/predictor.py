from datetime import datetime, timedelta
from typing import Optional, Tuple
import pandas as pd

class Predictor:
    def __init__(self, data_manager):
        self.data_manager = data_manager
    
    def get_average_cycle_length(self) -> Optional[float]:
        """Calculate average cycle length from historical data
        Returns average in days, or None if insufficient data
        """
        cycle_lengths = self.data_manager.calculate_cycle_lengths()
        
        if cycle_lengths.empty:
            return None
        
        return cycle_lengths.mean()
    
    def get_median_cycle_length(self) -> Optional[float]:
        """Calculate median cycle length (more robust to outliers)
        Returns median in days, or None if insufficient data
        """
        cycle_lengths = self.data_manager.calculate_cycle_lengths()
        
        if cycle_lengths.empty:
            return None
        
        return cycle_lengths.median()
    
    def predict_next_period(self, use_median=True) -> Optional[Tuple[str, int]]:
        """Predict the next period start date
        Args:
            use_median: If True, use median cycle length; if False, use mean
        Returns:
            Tuple of (predicted_date_string, cycle_length_used) or None if insufficient data
        """
        latest_period = self.data_manager.get_latest_period()
        
        if not latest_period:
            return None
        
        # Get cycle length to use for prediction
        if use_median:
            avg_cycle = self.get_median_cycle_length()
        else:
            avg_cycle = self.get_average_cycle_length()
        
        if avg_cycle is None:
            return None
        
        # Calculate next period date
        latest_date = datetime.strptime(latest_period, '%Y-%m-%d')
        next_date = latest_date + timedelta(days=round(avg_cycle))
        
        return (next_date.strftime('%Y-%m-%d'), round(avg_cycle))
    
    def get_cycle_statistics(self) -> dict:
        """Get comprehensive statistics about cycles
        Returns dict with various statistics or empty dict if insufficient data
        """
        cycle_lengths = self.data_manager.calculate_cycle_lengths()
        
        if cycle_lengths.empty:
            return {}
        
        stats = {
            'count': len(cycle_lengths),
            'average': round(cycle_lengths.mean(), 1),
            'median': cycle_lengths.median(),
            'shortest': int(cycle_lengths.min()),
            'longest': int(cycle_lengths.max())
        }
        
        # Calculate standard deviation if we have enough data
        if len(cycle_lengths) >= 2:
            stats['std_dev'] = round(cycle_lengths.std(), 1)
        
        return stats
    
    def days_until_next_period(self) -> Optional[int]:
        """Calculate how many days until the predicted next period
        Returns number of days, or None if prediction not possible
        """
        prediction = self.predict_next_period()
        
        if not prediction:
            return None
        
        predicted_date_str, _ = prediction
        predicted_date = datetime.strptime(predicted_date_str, '%Y-%m-%d')
        today = datetime.now()
        
        days_diff = (predicted_date - today).days
        
        return days_diff
    
    def get_moving_median(self, window=3) -> pd.DataFrame:
        """Calculate moving median of cycle lengths
        Args:
            window: Number of cycles to include in rolling window
        Returns:
            DataFrame with date and moving_median columns
        """
        df = self.data_manager.load_periods()
        
        if len(df) < 2:
            return pd.DataFrame(columns=['date', 'moving_median'])
        
        # Calculate cycle lengths
        df['cycle_length'] = df['date'].diff().dt.days
        
        # Calculate moving median
        df['moving_median'] = df['cycle_length'].rolling(window=window, min_periods=1).median()
        
        # Return only relevant columns (excluding first row which has NaN cycle_length)
        result = df[['date', 'moving_median']].iloc[1:].copy()
        
        return result
    
    def get_moving_average(self, window=3) -> pd.DataFrame:
        """Calculate moving average of cycle lengths
        Args:
            window: Number of cycles to include in rolling window
        Returns:
            DataFrame with date and moving_average columns
        """
        df = self.data_manager.load_periods()
        
        if len(df) < 2:
            return pd.DataFrame(columns=['date', 'moving_average'])
        
        # Calculate cycle lengths
        df['cycle_length'] = df['date'].diff().dt.days
        
        # Calculate moving average
        df['moving_average'] = df['cycle_length'].rolling(window=window, min_periods=1).mean()
        
        # Return only relevant columns (excluding first row)
        result = df[['date', 'moving_average']].iloc[1:].copy()
        
        return result


# Test
if __name__ == '__main__':
    from data_manager import DataManager
    
    dm = DataManager()
    predictor = Predictor(dm)
    
    # Add some sample periods
    dm.add_period('2024-01-15')
    dm.add_period('2024-02-12')  # 28 days
    dm.add_period('2024-03-10')  # 27 days
    dm.add_period('2024-04-08')  # 29 days
    dm.add_period('2024-05-06')  # 28 days
    dm.add_period('2024-06-05')  # 30 days
    
    print("Cycle statistics:", predictor.get_cycle_statistics())
    print("\nAverage cycle length:", predictor.get_average_cycle_length(), "days")
    print("Median cycle length:", predictor.get_median_cycle_length(), "days")
    
    prediction = predictor.predict_next_period()
    if prediction:
        date, cycle_length = prediction
        print(f"\nNext period predicted: {date}")
        print(f"Based on cycle length: {cycle_length} days")
        print(f"Days until next period: {predictor.days_until_next_period()}")
    
    print("\n--- Moving Statistics ---")
    print("\nMoving median (window=3):")
    print(predictor.get_moving_median(window=3))
    
    print("\nMoving average (window=3):")
    print(predictor.get_moving_average(window=3))