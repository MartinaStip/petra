import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime
from data_manager import DataManager
from predictor import Predictor
from visualizer import Visualizer

class PeriodTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Period Tracker")
        self.root.geometry("600x750")
        self.root.resizable(False, False)
        
        # Initialize components
        self.data_manager = DataManager()
        self.predictor = Predictor(self.data_manager)
        self.visualizer = Visualizer(self.data_manager)
        
        # Set up UI
        self.create_widgets()
        self.update_display()
    
    def create_widgets(self):
        # Title
        title_label = tk.Label(self.root, text="Period Tracker", 
                              font=("Arial", 20, "bold"), fg="#E91E63")
        title_label.pack(pady=20)
        
        # Prediction section
        self.prediction_frame = tk.LabelFrame(self.root, text="Next Period Prediction", 
                                             font=("Arial", 12, "bold"), padx=20, pady=15)
        self.prediction_frame.pack(padx=20, pady=10, fill="x")
        
        self.prediction_label = tk.Label(self.prediction_frame, text="", 
                                        font=("Arial", 14))
        self.prediction_label.pack()
        
        self.days_until_label = tk.Label(self.prediction_frame, text="", 
                                         font=("Arial", 11), fg="#666")
        self.days_until_label.pack(pady=5)
        
        # Add new period section
        input_frame = tk.LabelFrame(self.root, text="Add New Period", 
                                   font=("Arial", 12, "bold"), padx=20, pady=15)
        input_frame.pack(padx=20, pady=10, fill="x")
        
        # Date input
        date_row = tk.Frame(input_frame)
        date_row.pack(pady=5)
        
        tk.Label(date_row, text="Date:", font=("Arial", 11)).pack(side="left", padx=5)
        
        # Day
        self.day_var = tk.StringVar(value=str(datetime.now().day))
        day_spinner = tk.Spinbox(date_row, from_=1, to=31, width=5, 
                                textvariable=self.day_var, font=("Arial", 11))
        day_spinner.pack(side="left", padx=2)
        
        # Month
        self.month_var = tk.StringVar(value=str(datetime.now().month))
        month_spinner = tk.Spinbox(date_row, from_=1, to=12, width=5, 
                                  textvariable=self.month_var, font=("Arial", 11))
        month_spinner.pack(side="left", padx=2)
        
        # Year
        self.year_var = tk.StringVar(value=str(datetime.now().year))
        year_spinner = tk.Spinbox(date_row, from_=2020, to=2030, width=8, 
                                 textvariable=self.year_var, font=("Arial", 11))
        year_spinner.pack(side="left", padx=2)
        
        # Add button
        add_button = tk.Button(input_frame, text="Add Period", 
                              command=self.add_period, bg="#E91E63", fg="white", 
                              font=("Arial", 11, "bold"), padx=20, pady=5)
        add_button.pack(pady=10)
        
        # Statistics section
        stats_frame = tk.LabelFrame(self.root, text="Cycle Statistics", 
                                   font=("Arial", 12, "bold"), padx=20, pady=15)
        stats_frame.pack(padx=20, pady=10, fill="x")
        
        self.stats_label = tk.Label(stats_frame, text="", 
                                   font=("Arial", 10), justify="left")
        self.stats_label.pack()
        
        # Recorded periods section
        periods_frame = tk.LabelFrame(self.root, text="Recorded Periods", 
                                     font=("Arial", 12, "bold"), padx=20, pady=15)
        periods_frame.pack(padx=20, pady=10, fill="both", expand=True)
        
        # Listbox with scrollbar
        list_frame = tk.Frame(periods_frame)
        list_frame.pack(fill="both", expand=True)
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")
        
        self.periods_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, 
                                         font=("Arial", 10), height=6)
        self.periods_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.periods_listbox.yview)
        
        # Delete button
        delete_button = tk.Button(periods_frame, text="Delete Selected", 
                                 command=self.delete_period, bg="#F44336", fg="white", 
                                 font=("Arial", 10, "bold"), padx=15, pady=3)
        delete_button.pack(pady=5)
        
        # Visualization buttons
        viz_frame = tk.Frame(self.root)
        viz_frame.pack(pady=10)
        
        chart_button = tk.Button(viz_frame, text="Show Chart", 
                                command=self.show_chart, bg="#4CAF50", fg="white", 
                                font=("Arial", 11, "bold"), padx=20, pady=5)
        chart_button.pack(side="left", padx=5)
        
        trend_button = tk.Button(viz_frame, text="Show Trend", 
                                command=self.show_trend, bg="#2196F3", fg="white", 
                                font=("Arial", 11, "bold"), padx=20, pady=5)
        trend_button.pack(side="left", padx=5)
    
    def add_period(self):
        try:
            day = int(self.day_var.get())
            month = int(self.month_var.get())
            year = int(self.year_var.get())
            
            # Validate date
            date_obj = datetime(year, month, day)
            date_str = date_obj.strftime('%Y-%m-%d')
            
            # Check for omission
            omission_result = self.data_manager.check_omission(date_str)
            
            if omission_result:
                suspected, suggested_date = omission_result
                
                # Show omission dialog
                dialog = OmissionDialog(self.root, suggested_date)
                
                if dialog.user_confirmed:
                    # Add both interpolated and new period
                    periods_to_add = [
                        (dialog.interpolated_date, True),  # Interpolated
                        (date_str, False)  # New period
                    ]
                    
                    if self.data_manager.add_periods_batch(periods_to_add):
                        messagebox.showinfo("Success", 
                                          f"Added interpolated period: {dialog.interpolated_date}\n"
                                          f"Added new period: {date_str}")
                        self.update_display()
                    else:
                        messagebox.showwarning("Error", "Could not add periods")
                else:
                    # User declined interpolation, just add the new period
                    if self.data_manager.add_period(date_str, is_interpolated=False):
                        messagebox.showinfo("Success", f"Period added: {date_str}")
                        self.update_display()
                    else:
                        messagebox.showwarning("Duplicate", "This date is already recorded")
            else:
                # No omission detected, just add normally
                if self.data_manager.add_period(date_str, is_interpolated=False):
                    messagebox.showinfo("Success", f"Period added: {date_str}")
                    self.update_display()
                else:
                    messagebox.showwarning("Duplicate", "This date is already recorded")
                    
        except ValueError:
            messagebox.showerror("Error", "Invalid date")
    
    def delete_period(self):
        selection = self.periods_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a period to delete")
            return
        
        # Get the date from the listbox text (format: "YYYY-MM-DD" or "YYYY-MM-DD (interpolated)")
        list_text = self.periods_listbox.get(selection[0])
        date_str = list_text.split()[0]  # Get just the date part
        
        if messagebox.askyesno("Confirm Delete", f"Delete period: {date_str}?"):
            if self.data_manager.delete_period(date_str):
                messagebox.showinfo("Success", "Period deleted")
                self.update_display()
    
    def update_display(self):
        # Update prediction
        prediction = self.predictor.predict_next_period()
        if prediction:
            date, cycle_length = prediction
            self.prediction_label.config(text=f"📅 {date}")
            
            days_until = self.predictor.days_until_next_period()
            if days_until is not None:
                if days_until > 0:
                    self.days_until_label.config(text=f"In {days_until} days")
                elif days_until == 0:
                    self.days_until_label.config(text="Today!")
                else:
                    self.days_until_label.config(text=f"{abs(days_until)} days ago (overdue)")
        else:
            self.prediction_label.config(text="Add at least 2 periods for prediction")
            self.days_until_label.config(text="")
        
        # Update statistics
        stats = self.predictor.get_cycle_statistics()
        if stats:
            stats_text = f"Average: {stats['average']} days  |  "
            stats_text += f"Median: {stats['median']} days\n"
            stats_text += f"Range: {stats['shortest']}-{stats['longest']} days  |  "
            stats_text += f"Total cycles: {stats['count']}"
            
            if 'std_dev' in stats:
                stats_text += f"\nVariability: ±{stats['std_dev']} days"
            
            trend = self.visualizer.get_trend_description()
            stats_text += f"\n{trend}"
            
            self.stats_label.config(text=stats_text)
        else:
            self.stats_label.config(text="No statistics available yet")
        
        # Update periods list
        self.periods_listbox.delete(0, tk.END)
        df = self.data_manager.load_periods()
        
        # Show newest first
        for idx in reversed(df.index):
            date_str = df.loc[idx, 'date'].strftime('%Y-%m-%d')
            is_interp = df.loc[idx, 'is_interpolated']
            
            if is_interp:
                display_text = f"{date_str} (interpolated)"
            else:
                display_text = date_str
            
            self.periods_listbox.insert(tk.END, display_text)
    
    def show_chart(self):
        df = self.data_manager.load_periods()
        if len(df) < 2:
            messagebox.showinfo("No Data", "Add at least 2 periods to see the chart")
            return
        self.visualizer.plot_cycle_lengths()
    
    def show_trend(self):
        df = self.data_manager.load_periods()
        if len(df) < 3:
            messagebox.showinfo("No Data", "Add at least 3 periods to see the trend")
            return
        self.visualizer.plot_cycle_trend()


if __name__ == '__main__':
    root = tk.Tk()
    app = PeriodTrackerApp(root)
    root.mainloop()