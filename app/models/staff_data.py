from enum import Enum
from typing import List, Optional

class Role(Enum):
    PROFESSIONAL = "professional"
    HELPER = "helper"
    RELIEF = "relief"

class StaffMember:
    def __init__(
        self,
        id: int,
        name: str,
        role: Role,
        seniority: int,
        gender: str,
        is_supervisor: bool = False,
        supervisor_type: Optional[str] = None,
        annual_leave_days: int = 30,
        training_days_per_year: int = 3,
    ):
        self.id = id
        self.name = name
        self.role = role
        self.seniority = seniority
        self.gender = gender
        self.is_supervisor = is_supervisor
        self.supervisor_type = supervisor_type
        self.annual_leave_days = annual_leave_days
        self.training_days_per_year = training_days_per_year

# Define your 31 staff members here, ordered by seniority
# Staff list definition
staff_list: List[StaffMember] = [
    # Supervisors (first by seniority)
    StaffMember(0, "Afsaneh", Role.PROFESSIONAL, 1, "F", True, "HEAD_NURSE"),
    StaffMember(1, "Mina", Role.PROFESSIONAL, 2, "F", True, "SHIFT_SUPERVISOR"),
    StaffMember(2, "Zahra", Role.PROFESSIONAL, 3, "F", True, "EVENING_SUPERVISOR"),
    StaffMember(3, "Ali", Role.PROFESSIONAL, 4, "M", True, "ODD_NIGHT_SUPERVISOR"),
    StaffMember(4, "Saeed", Role.PROFESSIONAL, 5, "M", True, "EVEN_NIGHT_SUPERVISOR"),

    # Remaining professionals
    StaffMember(5, "Shirin", Role.PROFESSIONAL, 6, "F"),
    StaffMember(6, "Parisa", Role.PROFESSIONAL, 7, "F"),
    StaffMember(7, "Maryam", Role.PROFESSIONAL, 8, "F"),
    StaffMember(8, "Sara", Role.PROFESSIONAL, 9, "F"),
    StaffMember(9, "Mojgan", Role.PROFESSIONAL, 10, "F"),
    StaffMember(10, "Elham", Role.PROFESSIONAL, 11, "F"),
    StaffMember(11, "Haleh", Role.PROFESSIONAL, 12, "F"),
    StaffMember(12, "Nasrin", Role.PROFESSIONAL, 13, "F"),

    # Helpers
    StaffMember(13, "Ladan", Role.HELPER, 14, "F"),
    StaffMember(14, "Niloofar", Role.HELPER, 15, "F"),
    StaffMember(15, "Azam", Role.HELPER, 16, "F"),
    StaffMember(16, "Roya", Role.HELPER, 17, "F"),
    StaffMember(17, "Leila", Role.HELPER, 18, "F"),
    StaffMember(18, "Saba", Role.HELPER, 19, "F"),
    StaffMember(19, "Aida", Role.HELPER, 20, "F"),
    StaffMember(20, "Reyhaneh", Role.HELPER, 21, "F"),
    StaffMember(21, "Mehrdad", Role.HELPER, 22, "M"),
    StaffMember(22, "Peyman", Role.HELPER, 23, "M"),
    StaffMember(23, "Hamed", Role.HELPER, 24, "M"),

    # Additional Professionals (to meet 55%)
    StaffMember(24, "Farideh", Role.PROFESSIONAL, 25, "F"),
    StaffMember(25, "Shabnam", Role.PROFESSIONAL, 26, "F"),
    StaffMember(26, "Morteza", Role.PROFESSIONAL, 27, "M"),
    StaffMember(27, "Amin", Role.PROFESSIONAL, 28, "M"),

    # Relief staff
    StaffMember(28, "Behnaz", Role.RELIEF, 29, "F"),
    StaffMember(29, "Yasaman", Role.RELIEF, 30, "F"),

    # Final Helpers to complete total 31
    StaffMember(30, "Kourosh", Role.HELPER, 31, "M"),
]