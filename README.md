Simple period tracker 

# Front end
## Main window
- plot with current cycle: last period
- new entry: 
    - calendar with pre-filled current day
    - add button
    - add with note button
- data & statistics button

## data & statistics window
- plot series (see the description in the visualizer)
- table with raw data (see the description in the data manager) + buttons to edit/delete each entry

# Backend
## data_manager
a class that manages raw data (period dates):
- loads new entries
- deletes existing entries
- provides path to the csv with raw data:
    - column with period dates
    - column with notes (empty if there is no note)

## predictor
a class that processes the raw data
- creates df with new columns computed from the raw data
- creates several predictions and collects their errors in a separate df
- selects the best prediction and provides predicted date (or range?)
- provides the last recorded date

## visualizer
a class that generates visualizations
- plot current cycle: last + predicted date, countdown till next period
- plot series: 
    - plot all recorded dates as points
    - continual series are connected by a dashed line
    - rolling median or avg or another models is plotted above it