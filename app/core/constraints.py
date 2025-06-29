from ortools.sat.python import cp_model
from app.models.staff_data import staff_list, Role

# Constants
NUM_DAYS = 31  # Tir 1404
HOLIDAYS = [5, 6, 12, 13, 19, 20]

TOTAL_STAFF = len(staff_list)
NUM_PROF = int(TOTAL_STAFF * 0.55)
NUM_HELP = TOTAL_STAFF - NUM_PROF
TOTAL_RELIEF_MAX_SHIFTS = 25

MONTHLY_LEAVE_TOTAL = int(TOTAL_STAFF * 2.5)
MIN_LEAVE_ASSIGNED = MONTHLY_LEAVE_TOTAL // 2
MONTHLY_TRAINING_TOTAL = round(TOTAL_STAFF * 3 / 12)

SHIFT_TYPES = ["M", "A", "D", "E", "N", "DE"]
SHIFT_INDICES = {s: i for i, s in enumerate(SHIFT_TYPES)}

def add_basic_constraints(model: cp_model.CpModel, shifts):
    # One shift per person per day
    for p in range(TOTAL_STAFF):
        for d in range(NUM_DAYS):
            model.Add(sum(shifts[p, d, s] for s in range(6)) <= 1)

    # No shift after a night shift
    for p in range(TOTAL_STAFF):
        for d in range(NUM_DAYS - 1):
            model.Add(shifts[p, d, SHIFT_INDICES["N"]] + sum(shifts[p, d + 1, s] for s in range(6)) <= 1)

    # Relief staff max shift limit
    relief_ids = [i for i, p in enumerate(staff_list) if p.role == Role.RELIEF]
    model.Add(sum(shifts[p, d, s] for p in relief_ids for d in range(NUM_DAYS) for s in range(6)) <= TOTAL_RELIEF_MAX_SHIFTS)

def add_leave_constraints(model: cp_model.CpModel, shifts):
    # Total leave count between min and max
    leave_vars = [shifts[p, d, SHIFT_INDICES["M"]] for p in range(TOTAL_STAFF) for d in range(NUM_DAYS)]
    model.Add(sum(leave_vars) >= MIN_LEAVE_ASSIGNED)
    model.Add(sum(leave_vars) <= MONTHLY_LEAVE_TOTAL)

def add_training_constraints(model: cp_model.CpModel, shifts):
    # Total monthly training shifts
    training_vars = [shifts[p, d, SHIFT_INDICES["A"]] for p in range(TOTAL_STAFF) for d in range(NUM_DAYS)]
    model.Add(sum(training_vars) == MONTHLY_TRAINING_TOTAL)

def add_holiday_staffing_constraints(model: cp_model.CpModel, shifts):
    for d in HOLIDAYS:
        total_staff_today = sum(shifts[p, d, s] for p in range(TOTAL_STAFF) for s in range(6))
        model.Add(total_staff_today == (TOTAL_STAFF // 2) + 1)

def add_supervisor_fixed_shifts(model: cp_model.CpModel, shifts):
    supervisor_ids = [i for i, p in enumerate(staff_list) if p.is_supervisor]
    
    for sid in supervisor_ids:
        # Example: Ensure each supervisor gets at least one morning shift per week
        for week in range(4):  # 4 weeks in a 31-day month
            week_days = list(range(week * 7, min((week + 1) * 7, NUM_DAYS)))
            model.Add(sum(shifts[sid, d, SHIFT_TYPES.index("D")] for d in week_days) >= 1)


def add_prof_help_balance_constraint(model: cp_model.CpModel, shifts):
    for d in range(NUM_DAYS):
        total_staff_today = sum(shifts[p, d, s] for p in range(TOTAL_STAFF) for s in range(6))
        prof_count = sum(shifts[p, d, s] for p in range(TOTAL_STAFF)
                         if staff_list[p].role == Role.PROFESSIONAL #"professional"
                         for s in range(6))
        help_count = total_staff_today - prof_count

#############################
        # Define total_staff_today as sum of all shifts on day d
        total_staff_today = model.NewIntVar(0, TOTAL_STAFF, f"total_staff_d{d}")
        model.Add(total_staff_today == sum(shifts[p, d, s] for p in range(TOTAL_STAFF) for s in range(6)))

        # Define prof_count similarly
        prof_count = model.NewIntVar(0, TOTAL_STAFF, f"prof_count_d{d}")
        model.Add(prof_count == sum(shifts[p, d, s] 
            for p in range(TOTAL_STAFF) if staff_list[p].role == Role.PROFESSIONAL for s in range(6)))

        # The inequality prof_count >= 55% of total_staff_today becomes:
        # prof_count * 100 >= 55 * total_staff_today
        # Or equivalently:
        # 100 * prof_count - 55 * total_staff_today >= 0

        # To linearize this, create an auxiliary integer variable delta >= 0 such that:
        delta = model.NewIntVar(0, TOTAL_STAFF * 100, f"delta_d{d}")
        model.Add(delta == 100 * prof_count - 55 * total_staff_today)
        model.Add(delta >= 0)

        help_count = model.NewIntVar(0, TOTAL_STAFF, f"help_count_d{d}")
        model.Add(help_count == total_staff_today - prof_count)

        delta_help = model.NewIntVar(0, TOTAL_STAFF * 100, f"delta_help_d{d}")
        model.Add(delta_help == 45 * total_staff_today - 100 * help_count)
        model.Add(delta_help >= 0)

        # model.Add(prof_count * 100 >= 55 * total_staff_today)
        # model.Add(help_count * 100 <= 45 * total_staff_today)

def add_shift_distribution_constraints(model: cp_model.CpModel, shifts):
    # Example: Balanced Morning / Evening / Night / Long shifts per day
    for d in range(NUM_DAYS):
        total_staff_today = sum(shifts[p, d, s] for p in range(TOTAL_STAFF) for s in range(6))

        # target_m_e = (total_staff_today * 3) // 8 ##########3
        # target_m_e = model.NewIntVar(0, TOTAL_STAFF, f"target_m_e_d{d}")
        # model.AddDivisionEquality(target_m_e, total_staff_today * 3, 8)
        target_m_e = model.NewIntVar(0, TOTAL_STAFF, f"target_m_e_d{d}")
        # Enforce inequalities to approximate the division:
        # target_m_e <= floor((total_staff_today * 3) / 8)
        # target_m_e >= ceil((total_staff_today * 3) / 8) - 1

        # Since multiplication and division by variable is nonlinear, 
        # multiply all terms by 8 to avoid division:

        model.Add(target_m_e * 8 <= total_staff_today * 3)
        model.Add(target_m_e * 8 >= total_staff_today * 3 - 7)


        # target_n = (total_staff_today * 2) // 8 ###########################
        # target_n = model.NewIntVar(0, TOTAL_STAFF, f"target_n{d}")
        # model.AddDivisionEquality(target_n, total_staff_today * 2, 8)
        target_n = model.NewIntVar(0, TOTAL_STAFF, f"target_n_d{d}")
        model.Add(target_n * 8 <= total_staff_today * 2)
        model.Add(target_n * 8 >= total_staff_today * 2 - 7)



        model.Add(sum(shifts[p, d, SHIFT_INDICES["D"]] for p in range(TOTAL_STAFF)) == target_m_e)
        model.Add(sum(shifts[p, d, SHIFT_INDICES["E"]] for p in range(TOTAL_STAFF)) == target_m_e)
        model.Add(sum(shifts[p, d, SHIFT_INDICES["N"]] for p in range(TOTAL_STAFF)) == target_n)

def apply_all_constraints(model: cp_model.CpModel, shifts):
    add_basic_constraints(model, shifts)
    add_leave_constraints(model, shifts)
    add_training_constraints(model, shifts)
    add_holiday_staffing_constraints(model, shifts)
    add_supervisor_fixed_shifts(model, shifts)
    add_prof_help_balance_constraint(model, shifts)
    add_shift_distribution_constraints(model, shifts)
