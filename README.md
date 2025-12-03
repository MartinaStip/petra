Simple period tracker 

# Front end
## Main window (elements from top to bottom)
- prediction (text)
- donut plot with current cycle: 
    - fill = how much time since last period till the estimated next period
    - the fill is full circle if the period is due or overdue
    - text in the middle of donut: next date in x-y days

- new entry: 
    - add today button
    - pick another date from calendar button 

- plot of raw data: each entry as point + lines between them if they represent a meaningfull series 
    (distance between entries < 35 days) 
- table with raw data + buttons to edit/delete each entry

# Backend = CycleTracker class



# TO DO
- data table (another page?) with a function to delete an entry
- automated tests of the class
- MOVE DEFINITION OF BUTTONS OUTSIDE THE PAGE LAYOUT

# Possible structure when it gets more complex
2-3 files:
- cycle_tracker.py - the CycleTracker class (may be reused for a web app)
- main.py - the Flet UI code
- (optional) config.py - for colors and constants