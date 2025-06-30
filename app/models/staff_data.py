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
    # Professionals (%55)
    # Supervisors (first by seniority)
    StaffMember(0, "Afsaneh", Role.PROFESSIONAL, 1, "F", True, "HEAD_NURSE"),
    StaffMember(1, "Mina", Role.PROFESSIONAL, 2, "M", True, "SHIFT_SUPERVISOR"),
    StaffMember(2, "Zahra", Role.PROFESSIONAL, 3, "F", True, "EVENING_SUPERVISOR"),
    StaffMember(3, "Ali", Role.PROFESSIONAL, 4, "M", True, "ODD_NIGHT_SUPERVISOR"),
    StaffMember(4, "Saeed", Role.PROFESSIONAL, 5, "F", True, "EVEN_NIGHT_SUPERVISOR"),

    # Remaining professionals
    StaffMember(5, "Shirin", Role.PROFESSIONAL, 6, "M"),
    StaffMember(6, "Parisa", Role.PROFESSIONAL, 7, "F"),
    StaffMember(7, "Maryam", Role.PROFESSIONAL, 8, "M"),
    StaffMember(8, "Sara", Role.PROFESSIONAL, 9, "F"),
    StaffMember(9, "Mojgan", Role.PROFESSIONAL, 10, "M"),
    StaffMember(10, "Elham", Role.PROFESSIONAL, 11, "F"),
    StaffMember(11, "Haleh", Role.PROFESSIONAL, 12, "M"),
    StaffMember(12, "Nasrin", Role.PROFESSIONAL, 13, "F"),
    StaffMember(13, "Ladan", Role.PROFESSIONAL, 14, "M"),
    StaffMember(14, "Niloofar", Role.PROFESSIONAL, 15, "F"),
    StaffMember(15, "Azam", Role.PROFESSIONAL, 16, "M"),
    StaffMember(16, "Roya", Role.PROFESSIONAL, 17, "F"),
    
    # Helpers (%45)
    StaffMember(17, "Leila", Role.HELPER, 18, "M"),
    StaffMember(18, "Saba", Role.HELPER, 19, "F"),
    StaffMember(19, "Aida", Role.HELPER, 20, "M"),
    StaffMember(20, "Reyhaneh", Role.HELPER, 21, "F"),
    StaffMember(21, "Mehrdad", Role.HELPER, 22, "M"),
    StaffMember(22, "Peyman", Role.HELPER, 23, "F"),
    StaffMember(23, "Hamed", Role.HELPER, 24, "M"),
    StaffMember(24, "Farideh", Role.HELPER, 25, "F"),
    StaffMember(25, "Shabnam", Role.HELPER, 26, "M"),
    StaffMember(26, "Morteza", Role.HELPER, 27, "F"),
    StaffMember(27, "Amin", Role.HELPER, 28, "M"),
    StaffMember(28, "Behnaz", Role.HELPER, 29, "F"),
    StaffMember(29, "Yasaman", Role.HELPER, 30, "M"),
    StaffMember(30, "Kourosh", Role.HELPER, 31, "F"),

    # Relief staff -- add if needed
    # StaffMember(31, "aa", Role.RELIEF, 32, "M"),
    # StaffMember(32, "bb", Role.RELIEF, 35, "F"),
    # StaffMember(33, "aa", Role.RELIEF, 32, "M"),
    # StaffMember(34, "bb", Role.RELIEF, 35, "F"),

]