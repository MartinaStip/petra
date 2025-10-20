# Class groups related data and functions together (functions inside class = methods)
# Unlike separate functions, it knows where to add new entries without calling it explicitly 
# If there is a need to change data handling, it can be done effectively at this one place
# The first parameter of a method is self = the class itself
# When DataManager is called, python creates new instance of the class and calls __init__ = fills it with initial values 

# Purpose of this script
# Collect and store data
# Check new entries for correct format and duplicities
# Sort data chronologically
# Delete entries

import os
from datetime import datetime

class DataManager:
    def __init__(self, data_file = 'data/periods.csv'):
        self.data_file = data_file
        self._ensure_data_directory()
        self._ensure_data_file()
    
    def _ensure_data_directory(self):
        """Create data directory if it doesn't exist"""
        directory = os.path.dirname(self.data_file)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
    
    def _ensure_data_file(self):
        """Create CSV file with header if it doesn't exist"""
        if not os.path.exists(self.data_file):
            with open(self.data_file, 'w') as f:
                f.write('date\n')
    
    def get_file_path(self) -> str:
        """Get the path to the CSV file
        Returns path string for use with pandas.read_csv()
        """
        return self.data_file
    
    def add_period(self, date: str) -> bool:
        """Add a new period date to CSV
        Args:
            date: Date string in 'YYYY-MM-DD' format
        Returns:
            True if successful, False if duplicate or invalid
        """
        # Validate date format
        try:
            datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            return False
        
        # Check for duplicates
        if self._date_exists(date):
            return False
        
        # Append to file
        try:
            with open(self.data_file, 'a') as f:
                f.write(f'{date}\n')
            return True
        except Exception as e:
            print(f"Error adding period: {e}")
            return False
    
    def delete_period(self, date: str) -> bool:
        """Delete a period date from CSV
        Args:
            date: Date string in 'YYYY-MM-DD' format
        Returns:
            True if successful, False if not found
        """
        try:
            # Read all dates
            with open(self.data_file, 'r') as f:
                lines = f.readlines()
            
            # Check if date exists
            date_line = f'{date}\n'
            if date_line not in lines[1:]:  # Skip header
                return False
            
            # Rewrite file without the deleted date
            with open(self.data_file, 'w') as f:
                f.write(lines[0])  # Write header
                for line in lines[1:]:
                    if line.strip() != date:
                        f.write(line)
            
            return True
        except Exception as e:
            print(f"Error deleting period: {e}")
            return False
    
    def _date_exists(self, date: str) -> bool:
        """Check if a date already exists in the file
        Args:
            date: Date string in 'YYYY-MM-DD' format
        Returns:
            True if date exists
        """
        try:
            with open(self.data_file, 'r') as f:
                lines = f.readlines()
                for line in lines[1:]:  # Skip header
                    if line.strip() == date:
                        return True
            return False
        except Exception:
            return False


# Test
# The condition if __name__... makes the code run only if I run THIS file directly, not called from elsewhere
# It is just for testing when writing the script
if __name__ == '__main__':
    dm = DataManager()
    
    # Add some sample periods
    print("Adding periods...")
    dm.add_period('2024-01-15')
    dm.add_period('2024-02-12')
    dm.add_period('2024-03-10')
    dm.add_period('2024-04-08')
    
    print(f"File path: {dm.get_file_path()}")
    
    # Try adding duplicate
    result = dm.add_period('2024-02-12')
    print(f"Adding duplicate: {result}")  # Should be False
    
    # Delete a period
    print("Deleting 2024-02-12...")
    dm.delete_period('2024-02-12')
    
    print("\nCSV contents:")
    with open(dm.get_file_path(), 'r') as f:
        print(f.read())










    


