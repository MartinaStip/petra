import pytest
import os
import pandas as pd
from cycle_tracker import CycleTracker

# run pytest in your terminal
# Pytest will:
    # Find all files starting with test_
    # Run all functions starting with test_
    # Show green checkmarks (pass) or red X's (fail)

class TestCycleTracker:
    # A fixture is a function that sets up something you need for your tests, and then cleans it up afterwards.
    # It has 3 steps:
        # Setup: "Before each test, create a fresh temporary tracker"
        # Test runs: Uses that tracker
        # Cleanup: "After the test, delete the temporary file"
    @pytest.fixture
    def temp_tracker(self, tmp_path):
        """Creates a temporary tracker for each test"""
        # tmp_path is provided by pytest
        csv_file = tmp_path / "data/testdata.csv"
        tracker = CycleTracker(csv_file=str(csv_file))
        return tracker
    
    def test_empty_tracker(self, temp_tracker):
        """Test tracker with no data"""
        assert len(temp_tracker.dates) == 0
        assert temp_tracker.pred_date == "Not enough data"
    
    def test_add_date(self, temp_tracker):
        """Test adding a date"""
        result = temp_tracker.add_date("2024-01-01")
        assert result == True
        assert len(temp_tracker.dates) == 1
    
    def test_add_duplicate(self, temp_tracker):
        """Test that duplicates are rejected"""
        temp_tracker.add_date("2024-01-01")
        result = temp_tracker.add_date("2024-01-01")
        assert result == False
        assert len(temp_tracker.dates) == 1