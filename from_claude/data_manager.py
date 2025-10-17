# Class groups related data and functions together (functions inside class = methods)
# Unlike separate functions, it knows where to add new entries without calling it explicitly
# The first parameter of a method is self = the class itself
# When DataManager is called, python creates new instance of the class and calls __init__ = fills it with initial values 

# Purpose of this script
# Collect and store data
# Check new entries + suggest interpolation is it is plausible that the the user missed one record
# Sort data chronologically

import pandas as pd
import os
from datetime import datetime, timedelta
from typing import Optional, Tuple

class DataManager:
    def __init__(self, data_file='data/periods.csv'):
        self.data_file = data_file
        self._ensure_data_directory()
        self._ensure_data_file()
    
    def _ensure_data_directory(self):
        """Create data directory if it doesn't exist"""
        directory = os.path.dirname(self.data_file)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
    
    def _ensure_data_file(self):
        """Create CSV file with headers if it doesn't exist"""
        if not os.path.exists(self.data_file):
            df = pd.DataFrame(columns=['date', 'is_interpolated'])
            df.to_csv(self.data_file, index=False)
    
    def load_periods(self) -> pd.DataFrame:
        """Load periods from CSV as DataFrame
        Returns DataFrame with columns: date (datetime), is_interpolated (bool)
        """
        df = pd.read_csv(self.data_file)
        
        if df.empty:
            return df
        
        # Convert date strings to datetime
        df['date'] = pd.to_datetime(df['date'])
        
        # Ensure is_interpolated is boolean
        df['is_interpolated'] = df['is_interpolated'].astype(bool)
        
        # Sort by date
        # After sorting, the old row indices might be out of order, so they are reset and dropped
        df = df.sort_values('date').reset_index(drop=True)
        
        return df
    
    def save_periods(self, df: pd.DataFrame) -> bool:
        """Save DataFrame to CSV
        Args:
            df: DataFrame with date and is_interpolated columns
        Returns:
            True if successful
        """
        try:
            # Convert datetime to string for clean CSV
            df_to_save = df.copy()
            df_to_save['date'] = df_to_save['date'].dt.strftime('%Y-%m-%d')
            df_to_save.to_csv(self.data_file, index=False)
            return True
        except Exception as e:
            print(f"Error saving data: {e}")
            return False
    
    def check_omission(self, new_date: str) -> Optional[Tuple[bool, str]]:
        """Check if a period might have been omitted before this new date
        Args:
            new_date: Date string in 'YYYY-MM-DD' format
        Returns:
            Tuple of (omission_suspected, suggested_interpolated_date) or None
        """
        df = self.load_periods()
        
        if df.empty:
            return None
        
        new_date_dt = pd.to_datetime(new_date)
        last_date = df['date'].iloc[-1]
        
        # Calculate cycle length
        cycle_length = (new_date_dt - last_date).days
        
        # Calculate median cycle length 
        # Need at least 2 cycles in row with plausible time span
        cycle_lengths = df['date'].diff().dt.days.dropna() # computes difference between rows in days
        cycle_lengths = cycle_lengths[cycle_lengths < 36] # limit to plausible values
        
        if len(cycle_lengths) < 2:
            return None
        
        median_cycle = cycle_lengths.median()

        # Check if current cycle is > 1.5x median
        if cycle_length > 1.5 * median_cycle:
            # Calculate midpoint for interpolation
            midpoint = last_date + (new_date_dt - last_date) / 2
            midpoint_str = midpoint.strftime('%Y-%m-%d')
            return (True, midpoint_str)
        
        return None
    
    def add_period(self, date: str, is_interpolated: bool = False) -> bool:
        """Add a single period to the data
        Args:
            date: Date string in 'YYYY-MM-DD' format
            is_interpolated: Whether this is an interpolated date
        Returns:
            True if successful, False if duplicate
        """
        # Validate date format
        try:
            pd.to_datetime(date)
        except ValueError:
            return False
        
        df = self.load_periods()
        
        # Check for duplicates
        date_dt = pd.to_datetime(date)
        if not df.empty and date_dt in df['date'].values:
            return False
        
        # Add new period
        new_row = pd.DataFrame({
            'date': [date_dt],
            'is_interpolated': [is_interpolated]
        })
        
        df = pd.concat([df, new_row], ignore_index=True)
        df = df.sort_values('date').reset_index(drop=True)
        
        return self.save_periods(df)
    
    def add_periods_batch(self, dates_list: list) -> bool:
        """Add multiple periods at once
        Args:
            dates_list: List of tuples (date_string, is_interpolated)
        Returns:
            True if successful
        """
        df = self.load_periods()
        
        new_rows = []
        for date_str, is_interp in dates_list:
            date_dt = pd.to_datetime(date_str)
            # Skip duplicates
            if not df.empty and date_dt in df['date'].values:
                continue
            new_rows.append({'date': date_dt, 'is_interpolated': is_interp})
        
        if new_rows:
            new_df = pd.DataFrame(new_rows)
            df = pd.concat([df, new_df], ignore_index=True)
            df = df.sort_values('date').reset_index(drop=True)
            return self.save_periods(df)
        
        return True
    
    def delete_period(self, date: str) -> bool:
        """Delete a period
        Args:
            date: Date string in 'YYYY-MM-DD' format
        Returns:
            True if successful, False if not found
        """
        df = self.load_periods()
        
        if df.empty:
            return False
        
        date_dt = pd.to_datetime(date)
        
        if date_dt not in df['date'].values:
            return False
        
        df = df[df['date'] != date_dt]
        return self.save_periods(df)
    
    # MOVE TO PREDICTOR?
    def calculate_cycle_lengths(self) -> pd.Series:
        """Calculate cycle lengths from recorded periods
        Returns Series of cycle lengths in days
        """
        df = self.load_periods()
        
        if len(df) < 2:
            return pd.Series(dtype=float)
        
        return df['date'].diff().dt.days.dropna()
    
    # MOVE TO PREDICTOR?
    def get_latest_period(self) -> Optional[str]:
        """Get the most recent period date
        Returns date string or None
        """
        df = self.load_periods()
        
        if df.empty:
            return None
        
        return df['date'].iloc[-1].strftime('%Y-%m-%d')


# Test
# The condition if __name__... makes the code run only if I run THIS file directly, not called from elsewhere
# It is just for testing when writing the script
if __name__ == '__main__':
    dm = DataManager()
    
    # Add some sample periods
    dm.add_period('2024-01-15', is_interpolated=False)
    dm.add_period('2024-02-12', is_interpolated=False)
    dm.add_period('2024-03-10', is_interpolated=False)
    dm.add_period('2025-03-01', is_interpolated=False)

    df = dm.load_periods()
    print("df - Recorded periods:")
    print(dm.load_periods())
    
    # print("\nCycle lengths:")
    # print(dm.calculate_cycle_lengths())
    
    # print("\nLatest period:", dm.get_latest_period())
    
    # Test omission detection
    # print("\nChecking if omission suspected for 2024-05-20:")
    # result = dm.check_omission('2024-05-20')
    # if result:
    #     suspected, interpolated = result
    #     print(f"Omission suspected: {suspected}")
    #     print(f"Suggested interpolated date: {interpolated}")
    


