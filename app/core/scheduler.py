#TODO: remove in the final stages
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
##############################################################################

from ortools.sat.python import cp_model
from app.services.report import schedule_json_to_excel
from app.core.constraints import apply_all_constraints
from app.core.constraints import *

SHIFT_TYPES = ["M", "A", "D", "E", "N", "DE"]

def generate_schedule():
    model = cp_model.CpModel()

    # Create shift variables: shifts[p, d, s] = 1 if person p works shift s on day d
    shifts = {}
    for p in range(TOTAL_STAFF):
        for d in range(NUM_DAYS):
            for s in range(len(SHIFT_TYPES)):
                shifts[p, d, s] = model.NewBoolVar(f"sh_p{p}_d{d}_s{s}")

    # Apply all constraints
    apply_all_constraints(model, shifts)

    # Objective: spread shifts evenly (optional)
    # model.Minimize(
    #     sum(
    #         abs(
    #             sum(shifts[p, d, s] for d in range(NUM_DAYS) for s in range(len(SHIFT_TYPES)))
    #             - (NUM_DAYS * len(SHIFT_TYPES) / TOTAL_STAFF)
    #         ) for p in range(TOTAL_STAFF)
    #     )
    # )

    # Compute target number of shifts per staff member
    target_shifts_per_staff = int(NUM_DAYS * len(SHIFT_TYPES) / TOTAL_STAFF)

    # List to hold deviation variables
    deviation_vars = []

    for p in range(TOTAL_STAFF):
        # Total shifts for person p
        total_shifts = model.NewIntVar(0, NUM_DAYS * len(SHIFT_TYPES), f"total_shifts_p{p}")
        model.Add(total_shifts == sum(shifts[p, d, s] for d in range(NUM_DAYS) for s in range(len(SHIFT_TYPES))))
        
        # Deviation variable for this person
        deviation = model.NewIntVar(0, NUM_DAYS * len(SHIFT_TYPES), f"deviation_p{p}")
        model.AddAbsEquality(deviation, total_shifts - target_shifts_per_staff)
        
        deviation_vars.append(deviation)

    # Minimize total deviation across all staff
    model.Minimize(sum(deviation_vars))


    solver = cp_model.CpSolver()

    # Enable log for the solver
    # solver.parameters.log_search_progress = True 

    status = solver.Solve(model)

    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        print("No feasible solution found.")
        return None

    # Extract schedule
    schedule = []
    for d in range(NUM_DAYS):
        day_sched = {st: [] for st in SHIFT_TYPES}
        for s_index, st in enumerate(SHIFT_TYPES):
            for p in range(TOTAL_STAFF):
                if solver.Value(shifts[p, d, s_index]):
                    day_sched[st].append(p)
        schedule.append(day_sched)

    return schedule

if __name__ == "__main__":
    import json

    sched = generate_schedule()
    
    # print(json.dumps(sched, indent=2, ensure_ascii=False))
    if sched is not None:
        # Save JSON for reference (optional)
        with open("schedule.json", "w", encoding="utf-8") as f:
            json.dump(sched, f, ensure_ascii=False, indent=2)

        # Convert to Excel
        schedule_json_to_excel(sched, "schedule.xlsx")
