# main.py
import json
import pandas as pd
import openpyxl
from openpyxl.styles import PatternFill, Alignment
from datetime import datetime, timedelta

from app.core.scheduler import generate_schedule
from app.services.report import  schedule_json_to_excel, create_hospital_style_schedule


def load_schedule_json(filepath):
    """Load schedule JSON file"""
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

if __name__ == "__main__":
    sched = generate_schedule()
    # print(json.dumps(sched, indent=2, ensure_ascii=False))
    schedule_data = load_schedule_json("schedule.json")
    schedule_json_to_excel(schedule_data, "schedule_report.xlsx")
    
    create_hospital_style_schedule(
            schedule_data,
            "hospital_style_schedule.xlsx",
            staff_names=None,  # or provide {0: "Alice", 1: "Bob", ...}
            start_date="2025-07-01"  # adjust this to your month start date
        )

