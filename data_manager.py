import json
import os
from datetime import datetime
from typing import List, Optional

class DataManager:
    def __init__(self, data_file='data/periods.json'):
        self.data_file = data_file
        self._ensure_data_directory()
    
    def _ensure_data_directory(self):
        """Create data directory if it doesn't exist"""
        directory = os.path.dirname(self.data_file)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
    
    def load_periods(self) -> List[str]:
        """Load period dates from JSON file
        Returns list of dates in 'YYYY-MM-DD' format, sorted chronologically
        """
        if not os.path.exists(self.data_file):
            return []
        
        try:
            with open(self.data_file, 'r') as f:
                data = json.load(f)
                periods = data.get('periods', [])
                # Sort dates chronologically
                periods.sort()
                return periods
        except (json.JSONDecodeError, IOError):
            return []
    
    def save_period(self, date: str) -> bool:
        """Add a new period date
        Args:
            date: Date string in 'YYYY-MM-DD' format
        Returns:
            True if successful, False otherwise
        """
        # Validate date format
        try:
            datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            return False
        
        periods = self.load_periods()
        
        # Don't add duplicates
        if date in periods:
            return False
        
        periods.append(date)
        periods.sort()
        
        data = {'periods': periods}
        
        try:
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except IOError:
            return False
    
    def delete_period(self, date: str) -> bool:
        """Delete a period date
        Args:
            date: Date string in 'YYYY-MM-DD' format
        Returns:
            True if successful, False if date not found
        """
        periods = self.load_periods()
        
        if date not in periods:
            return False
        
        periods.remove(date)
        data = {'periods': periods}
        
        try:
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except IOError:
            return False
    
    def calculate_cycle_lengths(self) -> List[int]:
        """Calculate cycle lengths from recorded periods
        Returns list of cycle lengths in days
        """
        periods = self.load_periods()
        
        if len(periods) < 2:
            return []
        
        cycle_lengths = []
        for i in range(1, len(periods)):
            prev_date = datetime.strptime(periods[i-1], '%Y-%m-%d')
            curr_date = datetime.strptime(periods[i], '%Y-%m-%d')
            cycle_length = (curr_date - prev_date).days
            cycle_lengths.append(cycle_length)
        
        return cycle_lengths
    
    def get_latest_period(self) -> Optional[str]:
        """Get the most recent period date
        Returns date string or None if no periods recorded
        """
        periods = self.load_periods()
        return periods[-1] if periods else None


# Example usage
if __name__ == '__main__':
    dm = DataManager()
    
    # Add some sample periods
    dm.save_period('2024-01-15')
    dm.save_period('2024-02-12')
    dm.save_period('2024-03-10')
    dm.save_period('2024-04-08')
    
    # Load and display
    print("Recorded periods:", dm.load_periods())
    print("Cycle lengths:", dm.calculate_cycle_lengths())
    print("Latest period:", dm.get_latest_period())