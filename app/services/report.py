import pandas as pd

import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import PatternFill, Alignment
import calendar
from datetime import datetime, timedelta

SHIFT_TYPES = ["M", "A", "D", "E", "N", "DE"]

# Define color codes for each shift type (hex)
SHIFT_COLORS = {
    "M": "FFC7CE",  # Light Red
    "A": "FFEB9C",  # Light Yellow
    "D": "C6EFCE",  # Light Green
    "E": "9BC2E6",  # Light Blue
    "N": "D9D2E9",  # Light Purple
    "DE": "F4B084"  # Light Orange
}

def schedule_json_to_excel(schedule_json, excel_filepath):
    """
    Converts the schedule JSON into an Excel file.
    
    schedule_json: List of dictionaries like
      [
        {"M": [0,2], "A": [1], "D": [...], ...},  # Day 0
        {"M": [...], ...},                        # Day 1
        ...
      ]
    excel_filepath: path to save the Excel file (e.g. "schedule.xlsx")
    """

    # Prepare a list to build DataFrame rows
    rows = []

    # For each day, flatten shift-staff info
    for day_idx, day_schedule in enumerate(schedule_json, start=1):
        # For each shift type
        for shift_type, staff_ids in day_schedule.items():
            if not staff_ids:
                # If no staff assigned, put empty row
                rows.append({
                    "Day": day_idx,
                    "Shift": shift_type,
                    "Staff ID": ""
                })
            else:
                for sid in staff_ids:
                    rows.append({
                        "Day": day_idx,
                        "Shift": shift_type,
                        "Staff ID": sid
                    })

    # Create DataFrame
    df = pd.DataFrame(rows, columns=["Day", "Shift", "Staff ID"])

    # Save as Excel
    df.to_excel(excel_filepath, index=False)

    print(f"Excel file saved to {excel_filepath}")







def create_hospital_style_schedule(schedule_json, excel_filepath, staff_names=None, start_date=None):
    """
    Create an Excel file with days as columns, staff as rows,
    shifts filled in and color-coded.

    schedule_json: list of dicts per day {shift_type: [staff_ids]}
    excel_filepath: path to save Excel file
    staff_names: optional dict mapping staff_id to name
    start_date: datetime.date or string 'YYYY-MM-DD' for day 1 to calculate weekdays

    expamle:
    if sched is not None:
         create_hospital_style_schedule(
             sched, # Json
             "hospital_style_schedule.xlsx",
             staff_names=None,  # or provide {0: "Alice", 1: "Bob", ...}
             start_date="2025-07-01"  # adjust this to your month start date
         )
    """
    TOTAL_STAFF = max(max(staff_ids) if staff_ids else 0 for day in schedule_json for staff_ids in day.values()) + 1
    
    # Default staff_names: just staff_id as string
    if staff_names is None:
        staff_names = {i: f"Staff {i}" for i in range(TOTAL_STAFF)}

    # Prepare DataFrame rows (index=staff, columns=days)
    columns = []
    base_date = None
    if start_date is None:
        # Default: Assume day 1 is a Monday
        base_date = datetime.strptime("2025-07-01", "%Y-%m-%d").date()  # adjust to real start date if you want
    elif isinstance(start_date, str):
        base_date = datetime.strptime(start_date, "%Y-%m-%d").date()
    else:
        base_date = start_date

    for day_idx in range(len(schedule_json)):
        current_date = base_date + timedelta(days=day_idx)
        weekday_name = calendar.day_name[current_date.weekday()]  # e.g. Monday
        columns.append(f"{day_idx + 1} ({weekday_name[:3]})")

    # Initialize empty DataFrame with staff as index and days as columns
    df = pd.DataFrame("", index=[staff_names[i] for i in range(TOTAL_STAFF)], columns=columns)

    # Fill in shifts
    for day_idx, day_schedule in enumerate(schedule_json):
        for shift_type, staff_ids in day_schedule.items():
            for sid in staff_ids:
                current_val = df.at[staff_names[sid], columns[day_idx]]
                # If empty, just put shift, else append
                if current_val:
                    df.at[staff_names[sid], columns[day_idx]] = current_val + ", " + shift_type
                else:
                    df.at[staff_names[sid], columns[day_idx]] = shift_type

    # Save to Excel with color
    df.to_excel(excel_filepath)

    # Now open workbook with openpyxl to apply colors and formatting
    wb = load_workbook(excel_filepath)
    ws = wb.active

    # Center align all cells
    alignment = Alignment(horizontal="center", vertical="center")
    
    # Map shift types to their color fill
    fills = {k: PatternFill(start_color=v, end_color=v, fill_type="solid") for k,v in SHIFT_COLORS.items()}

    # Style header row (days)
    for col_idx in range(2, 2 + len(columns)):
        cell = ws.cell(row=1, column=col_idx)
        cell.alignment = alignment

    # Style staff name column (first column)
    for row_idx in range(2, 2 + TOTAL_STAFF):
        cell = ws.cell(row=row_idx, column=1)
        cell.alignment = alignment

    # Apply color fills for shifts
    for row_idx in range(2, 2 + TOTAL_STAFF):
        for col_idx in range(2, 2 + len(columns)):
            cell = ws.cell(row=row_idx, column=col_idx)
            cell.alignment = alignment
            cell_value = str(cell.value)
            if cell_value:
                # If multiple shifts, just color with the first shift color
                first_shift = cell_value.split(",")[0].strip()
                fill = fills.get(first_shift)
                if fill:
                    cell.fill = fill

    # Adjust column widths
    for col in ws.columns:
        max_length = 0
        col_letter = col[0].column_letter
        for cell in col:
            if cell.value:
                max_length = max(max_length, len(str(cell.value)))
        adjusted_width = max_length + 2
        ws.column_dimensions[col_letter].width = adjusted_width

    # Adjust row heights (optional)
    for row_idx in range(1, 2 + TOTAL_STAFF):
        ws.row_dimensions[row_idx].height = 20

    wb.save(excel_filepath)
    print(f"Hospital style Excel schedule saved to {excel_filepath}")

