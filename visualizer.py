import matplotlib.pyplot as plt
import pandas as pd

class Visualizer:
    def __init__(self, data_manager):
        self.data_manager = data_manager
    
    def plot_cycle_lengths(self, save_path=None):
        """Create a line chart showing cycle lengths over time
        Args:
            save_path: Optional path to save the figure (e.g., 'chart.png')
        """
        df = self.data_manager.load_periods()
        
        if len(df) < 2:
            print("Not enough data to visualize (need at least 2 periods)")
            return
        
        # Calculate cycle lengths
        df['cycle_length'] = df['date'].diff().dt.days
        
        # Remove first row (has NaN cycle_length)
        plot_df = df.iloc[1:].copy()
        
        if plot_df.empty:
            print("Not enough data to visualize")
            return
        
        # Create figure
        plt.figure(figsize=(10, 6))
        
        # Separate real and interpolated data for different styling
        real_data = plot_df[~plot_df['is_interpolated']]
        interp_data = plot_df[plot_df['is_interpolated']]
        
        # Plot real data
        if not real_data.empty:
            plt.plot(real_data['date'], real_data['cycle_length'], 
                    marker='o', linewidth=2, markersize=8, color='#E91E63', 
                    label='Recorded', linestyle='-')
        
        # Plot interpolated data
        if not interp_data.empty:
            plt.plot(interp_data['date'], interp_data['cycle_length'], 
                    marker='s', linewidth=2, markersize=6, color='#FF9800', 
                    label='Interpolated', linestyle='--', alpha=0.7)
        
        # Add average line
        avg = plot_df['cycle_length'].mean()
        plt.axhline(y=avg, color='gray', linestyle='--', linewidth=1, 
                   label=f'Average: {avg:.1f} days')
        
        # Formatting
        plt.xlabel('Period Date', fontsize=12)
        plt.ylabel('Cycle Length (days)', fontsize=12)
        plt.title('Cycle Length Over Time', fontsize=14, fontweight='bold')
        plt.grid(True, alpha=0.3)
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path)
        else:
            plt.show()
    
    def plot_cycle_trend(self, save_path=None):
        """Create a visualization showing trend (getting shorter/longer/stable)
        Args:
            save_path: Optional path to save the figure
        """
        df = self.data_manager.load_periods()
        
        if len(df) < 2:
            print("Not enough data for trend analysis (need at least 2 periods)")
            return
        
        # Calculate cycle lengths
        df['cycle_length'] = df['date'].diff().dt.days
        plot_df = df.iloc[1:].copy()
        
        if len(plot_df) < 2:
            print("Not enough data for trend analysis")
            return
        
        # Create figure with bar chart
        plt.figure(figsize=(10, 6))
        
        # Create bars with color gradient based on length
        colors = []
        for _, row in plot_df.iterrows():
            if row['is_interpolated']:
                colors.append('#FF9800')  # Orange for interpolated
            elif row['cycle_length'] < 26:
                colors.append('#4CAF50')  # Green for short
            elif row['cycle_length'] <= 30:
                colors.append('#2196F3')  # Blue for normal
            else:
                colors.append('#F44336')  # Red for long
        
        plt.bar(plot_df['date'], plot_df['cycle_length'], color=colors, 
               alpha=0.7, edgecolor='black')
        
        # Add average line
        avg = plot_df['cycle_length'].mean()
        plt.axhline(y=avg, color='black', linestyle='--', linewidth=2, 
                   label=f'Average: {avg:.1f} days')
        
        # Add trend line (simple linear regression using pandas)
        if len(plot_df) >= 2:
            # Convert dates to numeric for regression
            plot_df['date_numeric'] = (plot_df['date'] - plot_df['date'].min()).dt.days
            
            # Calculate trend line coefficients
            x = plot_df['date_numeric']
            y = plot_df['cycle_length']
            
            # Simple linear regression
            n = len(x)
            x_mean = x.mean()
            y_mean = y.mean()
            
            numerator = ((x - x_mean) * (y - y_mean)).sum()
            denominator = ((x - x_mean) ** 2).sum()
            
            if denominator != 0:
                slope = numerator / denominator
                intercept = y_mean - slope * x_mean
                
                trend_line = slope * x + intercept
                plt.plot(plot_df['date'], trend_line, color='blue', 
                        linewidth=2, label='Trend')
        
        # Formatting
        plt.xlabel('Period Date', fontsize=12)
        plt.ylabel('Cycle Length (days)', fontsize=12)
        plt.title('Cycle Length Trend', fontsize=14, fontweight='bold')
        plt.legend()
        plt.grid(True, alpha=0.3, axis='y')
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path)
        else:
            plt.show()
    
    def get_trend_description(self) -> str:
        """Analyze trend and return a text description
        Returns string describing if cycles are getting shorter/longer/stable
        """
        df = self.data_manager.load_periods()
        
        if len(df) < 2:
            return "Not enough data for trend analysis"
        
        cycle_lengths = df['date'].diff().dt.days.dropna()
        
        if len(cycle_lengths) < 3:
            return "Not enough data for trend analysis"
        
        # Compare first half vs second half
        mid = len(cycle_lengths) // 2
        first_half_avg = cycle_lengths.iloc[:mid].mean()
        second_half_avg = cycle_lengths.iloc[mid:].mean()
        
        diff = second_half_avg - first_half_avg
        
        if abs(diff) < 1:
            return f"Your cycles are stable (around {second_half_avg:.1f} days)"
        elif diff > 0:
            return f"Your cycles are getting longer ({first_half_avg:.1f} → {second_half_avg:.1f} days)"
        else:
            return f"Your cycles are getting shorter ({first_half_avg:.1f} → {second_half_avg:.1f} days)"


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