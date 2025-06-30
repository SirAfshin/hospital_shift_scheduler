from ortools.sat.python import cp_model
from app.models.staff_data import staff_list, Role

# Constants
NUM_DAYS = 31  # Tir 1404
# TODO: apply the real holidays
HOLIDAYS = [6-1, 13-1, 14-1, 15-1, 20-1, 27-1] # days start from 0 not 1 in the python code i wrote

TOTAL_STAFF = len(staff_list)
NUM_PROF = int(TOTAL_STAFF * 0.55)
NUM_HELP = TOTAL_STAFF - NUM_PROF
TOTAL_RELIEF_MAX_SHIFTS = 25
MONTHLY_LEAVE_TOTAL = 78 # int(TOTAL_STAFF * 2.5)
MIN_LEAVE_ASSIGNED = 39 # MONTHLY_LEAVE_TOTAL // 2
MONTHLY_TRAINING_TOTAL = 8 # round(TOTAL_STAFF * 3 / 12)
MAX_MONTHLY_WORKLOAD = 26 

# TODO: should i remove DE beacuse a D followed by E would be that
SHIFT_TYPES = ["M", "A", "D", "E", "N", "DE"]
TOTAL_SHIFT_TYPE = len(SHIFT_TYPES)
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


###########################################
#TODO: add role based constraints
def add_my_custom_shift_constraints(model: cp_model.CpModel, shifts):
    # One shift per person per day
    for p in range(TOTAL_STAFF):
        for d in range(NUM_DAYS):
            model.Add(sum(shifts[p, d, s] for s in range(TOTAL_SHIFT_TYPE)) <= 1)

    # Total workload of each person in month
    for p in range(TOTAL_STAFF):
        workload = sum(
            shifts[p, d, SHIFT_INDICES["M"]] +
            shifts[p, d, SHIFT_INDICES["A"]] +
            shifts[p, d, SHIFT_INDICES["D"]] +
            shifts[p, d, SHIFT_INDICES["E"]] +
            2 * shifts[p, d, SHIFT_INDICES["N"]] +
            2 * shifts[p, d, SHIFT_INDICES["DE"]]
            for d in range(NUM_DAYS)
        )
    model.Add(workload <= MAX_MONTHLY_WORKLOAD)

    # No shit after a night the other day
    for p in range(TOTAL_STAFF):
        for d in range(NUM_DAYS - 1):
            model.Add( (shifts[p, d, SHIFT_INDICES["N"]] + 
                        shifts[p, d + 1, SHIFT_INDICES["D"]] + 
                        shifts[p, d + 1, SHIFT_INDICES["E"]] +
                        shifts[p, d + 1, SHIFT_INDICES["N"]] + 
                        shifts[p, d + 1, SHIFT_INDICES["DE"]] +
                        shifts[p, d + 1, SHIFT_INDICES["A"]] +
                        shifts[p, d + 1, SHIFT_INDICES["M"]] ) <= 1) # TODO: must add other shift things as well

    # No shit after a DE the other day
    for p in range(TOTAL_STAFF):
        for d in range(NUM_DAYS - 1):
            model.Add( (shifts[p, d, SHIFT_INDICES["DE"]] + 
                        shifts[p, d + 1, SHIFT_INDICES["D"]] + 
                        shifts[p, d + 1, SHIFT_INDICES["E"]] +
                        shifts[p, d + 1, SHIFT_INDICES["N"]] + 
                        shifts[p, d + 1, SHIFT_INDICES["DE"]] +
                        shifts[p, d + 1, SHIFT_INDICES["A"]] +
                        shifts[p, d + 1, SHIFT_INDICES["M"]] ) <= 1) # TODO: must add other shift things as well


    # Holiday shift count    
    for d in HOLIDAYS:
        # total_staff_today = sum(shifts[p, d, s] for p in range(TOTAL_STAFF) for s in range(TOTAL_SHIFT_TYPE))
        # model.Add(total_staff_today == (TOTAL_STAFF // 2) + 1)
        model.Add(sum( (shifts[p, d, SHIFT_INDICES["D"]]+shifts[p, d, SHIFT_INDICES["DE"]]) for p in range(TOTAL_STAFF)) == 6)
        model.Add(sum( (shifts[p, d, SHIFT_INDICES["E"]]+shifts[p, d, SHIFT_INDICES["DE"]]) for p in range(TOTAL_STAFF)) == 5)
        model.Add(sum(shifts[p, d, SHIFT_INDICES["N"]] for p in range(TOTAL_STAFF)) == 4)

    # Normal day shift count
    for d in range(NUM_DAYS):
        if d not in HOLIDAYS:
            model.Add(sum( (shifts[p, d, SHIFT_INDICES["D"]]+shifts[p, d, SHIFT_INDICES["DE"]]) for p in range(TOTAL_STAFF)) == 9)
            model.Add(sum( (shifts[p, d, SHIFT_INDICES["E"]]+shifts[p, d, SHIFT_INDICES["DE"]]) for p in range(TOTAL_STAFF)) == 8)
            model.Add(sum(shifts[p, d, SHIFT_INDICES["N"]] for p in range(TOTAL_STAFF)) == 6)


    # Total leave count between
    leave_vars = [shifts[p, d, SHIFT_INDICES["M"]] for p in range(TOTAL_STAFF) for d in range(NUM_DAYS)]
    model.Add(sum(leave_vars) == MIN_LEAVE_ASSIGNED) 
    # model.Add(sum(leave_vars) >= MIN_LEAVE_ASSIGNED)
    # model.Add(sum(leave_vars) <= MONTHLY_LEAVE_TOTAL)
    
    # Individual leave count
    for p in range(TOTAL_STAFF):
        person_leave_count = sum(shifts[p, d, SHIFT_INDICES["M"]] for d in range(NUM_DAYS))
        model.Add(person_leave_count < 3)


    # Total monthly training shifts
    training_vars = [shifts[p, d, SHIFT_INDICES["A"]] for p in range(TOTAL_STAFF) for d in range(NUM_DAYS)]
    model.Add(sum(training_vars) == MONTHLY_TRAINING_TOTAL)
    # Individual training constraint
    for p in range(TOTAL_STAFF):
        person_train_count = sum(shifts[p,d,SHIFT_INDICES['A']] for d in range(NUM_DAYS))
        model.add(person_train_count <= 3)

    # No shifts if on Leave (Morakhasi)
    for p in range(TOTAL_STAFF):
        for d in range(NUM_DAYS):
            leave = shifts[p, d, SHIFT_INDICES["M"]]
            model.Add( sum(shifts[p, d, s] for s in range(TOTAL_SHIFT_TYPE) 
                           if s != SHIFT_INDICES["M"]) == 0).OnlyEnforceIf(leave)

    # No DE or N after DE
    # for p in range(TOTAL_STAFF):
    #     for d in range(NUM_DAYS - 1):
    #         model.Add(shifts[p, d, SHIFT_INDICES["DE"]] + shifts[p, d + 1, SHIFT_INDICES["DE"]] + shifts[p, d + 1, SHIFT_INDICES["N"]]  <= 1)


    # # Max N and DE shifts per person
    # for p in range(TOTAL_STAFF):
    #     total_n_shifts = sum(shifts[p, d, SHIFT_INDICES["N"]] + shifts[p, d, SHIFT_INDICES["DE"]] for d in range(NUM_DAYS))
    #     model.Add(total_n_shifts <= 6)


def add_my_costum_role_constraints(model: cp_model.CpModel, shifts):
    # Staff indices by role
    professionals = [s.id for s in staff_list if s.role == Role.PROFESSIONAL]
    helpers = [s.id for s in staff_list if s.role == Role.HELPER]
    reliefs = [s.id for s in staff_list if s.role == Role.RELIEF]

    # Staff indices by gender
    females = [s.id for s in staff_list if s.gender == "F"]
    males = [s.id for s in staff_list if s.gender == "M"]

    # Supervisors
    supervisors = [s.id for s in staff_list if s.is_supervisor]
    head_nurse_id = next(s.id for s in staff_list if s.supervisor_type == "HEAD_NURSE")
    shift_supervisor_id = next(s.id for s in staff_list if s.supervisor_type == "SHIFT_SUPERVISOR")
    evening_supervisor_id = next(s.id for s in staff_list if s.supervisor_type == "EVENING_SUPERVISOR")
    even_night_supervisor_id = next(s.id for s in staff_list if s.supervisor_type == "EVEN_NIGHT_SUPERVISOR")
    odd_night_supervisor_id = next(s.id for s in staff_list if s.supervisor_type == "ODD_NIGHT_SUPERVISOR")

 
    '''Head Nurse'''
    # Head Nurse D every days except holidays
    for d in range(NUM_DAYS):
        if d not in HOLIDAYS:
            model.Add(shifts[head_nurse_id, d, SHIFT_INDICES["D"]] == 1)
            # All other shifts on those days are 0
            for s in SHIFT_INDICES.values():
                if s != SHIFT_INDICES["D"]:
                    model.Add(shifts[head_nurse_id, d, s] == 0)
    # Head Nurse no shift on holidays
    for d in HOLIDAYS:
        for s in SHIFT_INDICES.values():
            model.Add(shifts[head_nurse_id, d, s] == 0)

    '''Shift Supervisor (staff)'''
    # Shift supervisor is D everyday except holidays
    for d in range(NUM_DAYS):
        if d not in HOLIDAYS:
            model.Add(shifts[shift_supervisor_id, d, SHIFT_INDICES["D"]] == 1)
            # No other shifts allowed on those days
            for s in SHIFT_INDICES.values():
                if s != SHIFT_INDICES["D"]:
                    model.Add(shifts[shift_supervisor_id, d, s] == 0)
    
    # At most one D shift on holidays
    # Collect total D shifts on holidays
    holiday_D_shifts = [shifts[shift_supervisor_id, d, SHIFT_INDICES["D"]] for d in HOLIDAYS]
    
    # No other shifts on holidays
    for d in HOLIDAYS:
        for s in SHIFT_INDICES.values():
            if s != SHIFT_INDICES["D"]:
                model.Add(shifts[shift_supervisor_id, d, s] == 0)

    # At most one E shift across all holidays
    model.Add(sum(holiday_D_shifts) <= 1)


    '''EVENING SUPERVISOR'''
    # Only E shifts on normal days
    for d in range(NUM_DAYS):
        if d not in HOLIDAYS:
            model.Add(shifts[evening_supervisor_id, d, SHIFT_INDICES["E"]] == 1)
            # No other shifts
            for s in SHIFT_INDICES.values():
                if s != SHIFT_INDICES["E"]:
                    model.Add(shifts[evening_supervisor_id, d, s] == 0)
    
    # At most one E shift on holidays
    # Collect total E shifts on holidays
    holiday_E_shifts = [shifts[evening_supervisor_id, d, SHIFT_INDICES["E"]] for d in HOLIDAYS]

    # No other shifts on holidays
    for d in HOLIDAYS:
        for s in SHIFT_INDICES.values():
            if s != SHIFT_INDICES["E"]:
                model.Add(shifts[evening_supervisor_id, d, s] == 0)

    # At most one E shift across all holidays
    model.Add(sum(holiday_E_shifts) <= 1)



    '''NIGHT SUPERVISORs'''
    # EVEN_NIGHT_SUPERVISOR
    even_night_holiday_shifts = []

    for d in range(NUM_DAYS):
        if d not in HOLIDAYS:
            if d % 2 == 0:
                # Can work N shift on even days
                model.Add(shifts[even_night_supervisor_id, d, SHIFT_INDICES["N"]] == 1)
            else:
                # No shifts at all on odd days
                for s in SHIFT_INDICES.values():
                    model.Add(shifts[even_night_supervisor_id, d, s] == 0)
        else:
            # On holidays: collect N shifts to count later
            even_night_holiday_shifts.append(shifts[even_night_supervisor_id, d, SHIFT_INDICES["N"]])
            # No other shifts on holidays
            for s in SHIFT_INDICES.values():
                if s != SHIFT_INDICES["N"]:
                    model.Add(shifts[even_night_supervisor_id, d, s] == 0)

    # At most 1 N shift on holidays
    model.Add(sum(even_night_holiday_shifts) <= 1)

    # ODD_NIGHT_SUPERVISOR
    odd_night_holiday_shifts = []

    for d in range(NUM_DAYS):
        if d not in HOLIDAYS:
            if d % 2 == 1:
                # Can work N shift on odd days
                model.Add(shifts[odd_night_supervisor_id, d, SHIFT_INDICES["N"]] == 1)
            else:
                # No shifts at all on even days
                for s in SHIFT_INDICES.values():
                    model.Add(shifts[odd_night_supervisor_id, d, s] == 0)
        else:
            # On holidays: collect N shifts to count later
            odd_night_holiday_shifts.append(shifts[odd_night_supervisor_id, d, SHIFT_INDICES["N"]])
            # No other shifts on holidays
            for s in SHIFT_INDICES.values():
                if s != SHIFT_INDICES["N"]:
                    model.Add(shifts[odd_night_supervisor_id, d, s] == 0)

    # At most 1 N shift on holidays
    model.Add(sum(odd_night_holiday_shifts) <= 1)

    # TODO: no feasible answer for the M and for Off it finds is it OK?
    '''That one person with 16,20 leave'''
    # for d in range(15, 20):  # days 16,17,18,19,20
    #     model.Add(shifts[5, d, SHIFT_INDICES["M"]] == 1)
    for d in range(15, 20):
        model.Add(sum(shifts[5, d, s] for s in range(TOTAL_SHIFT_TYPE)) == 0)

    


def add_my_costum_other_constraints(model: cp_model.CpModel, shifts):
    important_shifts = [
        SHIFT_INDICES["D"],
        SHIFT_INDICES["E"],
        SHIFT_INDICES["DE"],
        SHIFT_INDICES["N"],
    ]

    # At least one man and at least one woman rule
    for d in range(NUM_DAYS):
        for s in important_shifts:
            male_count = sum(shifts[staff.id, d, s] for staff in staff_list if staff.gender == "M")
            female_count = sum(shifts[staff.id, d, s] for staff in staff_list if staff.gender == "F")
            
            model.Add(male_count >= 1)
            model.Add(female_count >= 1)

    '''Releif Personnel'''
    # Relief staff shift constraints
    for staff in staff_list:
        if staff.role == Role.RELIEF:
            staff_shift_vars = [
                shifts[staff.id, d, s]
                for d in range(NUM_DAYS)
                for s in range(len(SHIFT_TYPES))
            ]

            # Allow only DE, D, E, N shifts
            for d in range(NUM_DAYS):
                for s in range(len(SHIFT_TYPES)):
                    shift_name = SHIFT_TYPES[s]
                    if shift_name not in ["D", "E", "N", "DE"]:
                        model.Add(shifts[staff.id, d, s] == 0)

    # Total shift count for relief staff (DE, D, E, N only)
    relief_shift_vars = [
        shifts[staff.id, d, s]
        for staff in staff_list
        if staff.role == Role.RELIEF
        for d in range(NUM_DAYS)
        for s in range(len(SHIFT_TYPES))
        if SHIFT_TYPES[s] in ["D", "E", "N", "DE"]
    ]

    model.Add(sum(relief_shift_vars) <= 25)



    # TODO: this one makes the solution to not be feasible
    # # %50 rule for professionals and helpers
    # for d in range(NUM_DAYS):
    #     for s in important_shifts:
    #         professionals = [
    #             shifts[staff.id, d, s] for staff in staff_list 
    #             if staff.role in [Role.PROFESSIONAL, Role.RELIEF]
    #         ]
    #         helpers = [
    #             shifts[staff.id, d, s] for staff in staff_list 
    #             if staff.role == Role.HELPER
    #         ]
            
    #         total_staff_in_shift = sum(professionals) + sum(helpers)
            
    #         # Now enforce that half of the people in this shift are professionals, half helpers
    #         half_staff = model.NewIntVar(0, TOTAL_STAFF, f"half_staff_d{d}_s{s}")
    #         model.Add(half_staff * 2 == total_staff_in_shift)
            
    #         model.Add(sum(professionals) == half_staff)
    #         model.Add(sum(helpers) == total_staff_in_shift - half_staff)
    important_shifts = [
        SHIFT_INDICES["D"],
        SHIFT_INDICES["E"],
        SHIFT_INDICES["N"]
    ]

    for d in range(NUM_DAYS):
        for s in important_shifts:
            professionals = []
            helpers = []

            for staff in staff_list:
                if staff.role in [Role.PROFESSIONAL, Role.RELIEF]:
                    # DE counts for both D and E
                    if s in [SHIFT_INDICES["D"], SHIFT_INDICES["E"]]:
                        professionals.append(shifts[staff.id, d, s])
                        professionals.append(shifts[staff.id, d, SHIFT_INDICES["DE"]])
                    else:
                        professionals.append(shifts[staff.id, d, s])
                elif staff.role == Role.HELPER:
                    if s in [SHIFT_INDICES["D"], SHIFT_INDICES["E"]]:
                        helpers.append(shifts[staff.id, d, s])
                        helpers.append(shifts[staff.id, d, SHIFT_INDICES["DE"]])
                    else:
                        helpers.append(shifts[staff.id, d, s])

            if d in HOLIDAYS:
                if s == SHIFT_INDICES["D"]:
                    model.Add(sum(professionals) >= 3)
                    model.Add(sum(helpers) >= 3)
                elif s == SHIFT_INDICES["E"]:
                    model.Add(sum(professionals) >= 3)
                    model.Add(sum(helpers) >= 2)
                elif s == SHIFT_INDICES["N"]:
                    model.Add(sum(professionals) >= 2)
                    model.Add(sum(helpers) >= 2)
            else:
                if s == SHIFT_INDICES["D"]:
                    model.Add(sum(professionals) >= 5)
                    model.Add(sum(helpers) >= 4)
                elif s == SHIFT_INDICES["E"]:
                    model.Add(sum(professionals) >= 4)
                    model.Add(sum(helpers) >= 4)
                elif s == SHIFT_INDICES["N"]:
                    model.Add(sum(professionals) >= 3)
                model.Add(sum(helpers) >= 3)


def apply_all_constraints(model: cp_model.CpModel, shifts):
    # add_basic_constraints(model, shifts)
    # add_leave_constraints(model, shifts)
    # add_training_constraints(model, shifts)
    # add_holiday_staffing_constraints(model, shifts)
    # add_supervisor_fixed_shifts(model, shifts)
    # add_prof_help_balance_constraint(model, shifts)
    # add_shift_distribution_constraints(model, shifts)
    
    # New Era
    add_my_custom_shift_constraints(model, shifts)
    add_my_costum_role_constraints(model, shifts)
    add_my_costum_other_constraints(model, shifts)