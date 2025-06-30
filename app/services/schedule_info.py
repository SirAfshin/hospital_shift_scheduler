import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import pprint

def count_shifts_by_day_and_category(df, shift_types=None):
    """
    Count number of total, female, male, professional, and helper personnel 
    for each shift in each day.
    
    Parameters:
        df (pd.DataFrame): DataFrame containing schedule data.
        shift_types (list, optional): List of shift codes to track. 
                                      Defaults to ['D', 'E', 'N', 'M', 'DE'].
    
    Returns:
        dict: Nested dictionary with counts for each day and shift.
    """
    if shift_types is None:
        shift_types = ['D', 'E', 'N', 'M', 'DE']

    # Identify schedule columns (days)
    days = [col for col in df.columns if '(' in col]
    
    # Initialize results dictionary
    results = {}

    for day in days:
        results[day] = {}
        for shift in shift_types:
            # Total count
            total = (df[day] == shift).sum()
            
            # Gender counts
            female = ((df[day] == shift) & (df['Gender'] == 'F')).sum()
            male = ((df[day] == shift) & (df['Gender'] == 'M')).sum()
            
            # Role counts
            professional = ((df[day] == shift) & (df['Role'] == 'professional')).sum()
            helper = ((df[day] == shift) & (df['Role'] == 'helper')).sum()

            # Store counts
            results[day][shift] = {
                'Total': total,
                'Female': female,
                'Male': male,
                'Professional': professional,
                'Helper': helper
            }

    return results



def plot_shift_summary(shift_summary):
    """
    Plot total number of personnel in each shift per day as a grouped bar chart.
    
    Parameters:
        shift_summary (dict): Nested dictionary from count_shifts_by_day_and_category().
    """
    # Convert nested dict to a DataFrame for plotting
    data = []
    for day, shifts in shift_summary.items():
        for shift, counts in shifts.items():
            data.append({
                'Day': day,
                'Shift': shift,
                'Total': counts['Total'],
                'Female': counts['Female'],
                'Male': counts['Male'],
                'Professional': counts['Professional'],
                'Helper': counts['Helper']
            })
    
    plot_df = pd.DataFrame(data)

    # Set plot style
    sns.set(style="whitegrid")

    # Plot total personnel per shift per day
    plt.figure(figsize=(14, 7))
    sns.barplot(data=plot_df, x='Day', y='Total', hue='Shift')
    plt.title('Total Personnel per Shift per Day')
    plt.ylabel('Number of Staff')
    plt.xticks(rotation=45)
    plt.legend(title='Shift')
    plt.tight_layout()
    plt.show()

    # Optional: stacked count by gender per shift per day
    for category in ['Female', 'Male']:
        plt.figure(figsize=(14, 7))
        sns.barplot(data=plot_df, x='Day', y=category, hue='Shift')
        plt.title(f'{category} Personnel per Shift per Day')
        plt.ylabel(f'Number of {category} Staff')
        plt.xticks(rotation=45)
        plt.legend(title='Shift')
        plt.tight_layout()
        plt.show()

    # Optional: stacked count by role per shift per day
    for category in ['Professional', 'Helper']:
        plt.figure(figsize=(14, 7))
        sns.barplot(data=plot_df, x='Day', y=category, hue='Shift')
        plt.title(f'{category} Personnel per Shift per Day')
        plt.ylabel(f'Number of {category} Staff')
        plt.xticks(rotation=45)
        plt.legend(title='Shift')
        plt.tight_layout()
        plt.show()



if __name__ == "__main__":
    # Load your data
    df = pd.read_excel(r"D:\Projects\Hospital_Shift_Scheduler\hospital_schedule_hijri1.xlsx")

    # Call the helper function
    shift_summary = count_shifts_by_day_and_category(df)

    # Print results nicely
    # pprint.pprint(shift_summary)

    # Plot the results
    plot_shift_summary(shift_summary)