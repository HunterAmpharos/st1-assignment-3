"""Console helpers and a small runnable starting demonstration."""


import re
from datetime import datetime

from smartcare.data_store import SmartCareDataStore
from smartcare.domain import Appointment, AppointmentStatus
from smartcare.services import (
    AppointmentService,
    PatientService,
    PractitionerService,
)


def parse_date_time(text: str) -> datetime:
    """Parse YYYY-MM-DD HH:MM; raise ValueError for invalid input."""
    if (
        not isinstance(text, str)
        or re.fullmatch(
            '[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}', text
        ) is None
    ):
        raise ValueError('Use date/time format YYYY-MM-DD HH:MM')
    try:
        return datetime.strptime(text, '%Y-%m-%d %H:%M')
    except ValueError:
        raise ValueError(
            'Invalid calendar date/time; use YYYY-MM-DD HH:MM',
        ) from None


def format_appointment(appointment: Appointment) -> str:
    """Return readable synthetic appointment details without changing
    state.
    """
    return (
        f'{appointment.appointment_id}: '
        f'{appointment.patient.patient_id} with '
        f'{appointment.practitioner.practitioner_id}, '
        f'{appointment.date_time:%Y-%m-%d %H:%M}, {appointment.status.value}'
    )


def run_demo() -> None:
    """Demonstrate supplied registration and booking using synthetic
    records.
    """
    data_store = SmartCareDataStore()
    patients = PatientService(data_store)
    practitioners = PractitionerService(data_store)
    appointments = AppointmentService(data_store)
    patients.register_patient('P1', 'Alex Example')
    practitioners.register_practitioner(
        'DR1',
        'Taylor Example',
        'General practice',
    )
    try:
        appointments.book_appointment(
            'A1',
            'P1',
            'DR1',
            parse_date_time('2026-10-01 09:00'),
        )
        print(format_appointment(appointments.find_appointment('A1')))
    except (ValueError, LookupError) as error:
        print(f'Error: {error}')
    print('Session-only data: records are lost on exit.')

MENU = """
-=SmartCare Menu=-
1. Register a Patient
2. Find a Patient
3. Register a Practitioner
4. Find a Practitioner
5. Book Appointment
6. Cancel Appointment
7. Find an Appointment
8. List a Practitioner's Appointments
0. Exit"""


def parse_status_choice(text: str) -> AppointmentStatus | None:
    """Blank means all statuses; otherwise scheduled/cancelled/completed."""
    text = text.strip().lower()
    if text == '':
        return None
    try:
        return AppointmentStatus(text)
    except ValueError:
        raise ValueError(
            'Status must be blank, scheduled, cancelled or completed',
        ) from None


def run_menu(input_fn=input, output_fn=print) -> None:
    """Run the register/find/book/cancel/list/exit menu.

    One store and one set of services are used for the whole session. Expected
    input errors (ValueError, LookupError) are reported and the menu
    continues. input_fn and output_fn default to input and print; tests pass
    scripted replacements.
    """
    data_store = SmartCareDataStore()
    patients = PatientService(data_store)
    practitioners = PractitionerService(data_store)
    appointments = AppointmentService(data_store)

    def ask(prompt: str) -> str:
        return input_fn(prompt + ': ')

    while True:
        output_fn(MENU)
        try:
            choice = input_fn('Please choose an option: ').strip()
            if choice == '0':
                output_fn('See ya later! Anything unsaved will be lost')
                return
            if choice == '1':
                patient = patients.register_patient(
                    ask('Patient ID'), ask('Patient name'),
                )
                output_fn(
                    f'Registered patient {patient.patient_id}: {patient.name}',
                )
            elif choice == '2':
                patient = patients.find_patient(ask('Patient ID'))
                output_fn(f'Found patient {patient.patient_id}: {patient.name}')
            elif choice == '3':
                practitioner = practitioners.register_practitioner(
                    ask('Practitioner ID'),
                    ask('Practitioner name'),
                    ask('Specialty'),
                )
                output_fn(
                    f'Registered practitioner {practitioner.practitioner_id}: '
                    f'{practitioner.name} ({practitioner.specialty})',
                )
            elif choice == '4':
                practitioner = practitioners.find_practitioner(
                    ask('Practitioner ID'),
                )
                output_fn(
                    f'Found practitioner {practitioner.practitioner_id}: '
                    f'{practitioner.name} ({practitioner.specialty})',
                )
            elif choice == '5':
                appointment_id = ask('Appointment ID')
                patient_id = ask('Patient ID')
                practitioner_id = ask('Practitioner ID')
                date_time = parse_date_time(
                    ask('Date and time (YYYY-MM-DD HH:MM)'),
                )
                appointment = appointments.book_appointment(
                    appointment_id, patient_id, practitioner_id, date_time,
                )
                output_fn('Booked ' + format_appointment(appointment))
            elif choice == '6':
                appointment = appointments.cancel_appointment(
                    ask('Appointment ID'),
                )
                output_fn('Cancelled ' + format_appointment(appointment))
            elif choice == '7':
                appointment = appointments.find_appointment(
                    ask('Appointment ID'),
                )
                output_fn(format_appointment(appointment))
            elif choice == '8':
                practitioner_id = ask('Practitioner ID')
                status = parse_status_choice(
                    ask('Status (blank for all, or scheduled/cancelled/completed)'),
                )
                found = appointments.list_practitioner_appointments(
                    practitioner_id, status,
                )
                if not found:
                    output_fn('No matching appointments.')
                for appointment in found:
                    output_fn(format_appointment(appointment))
            else:
                output_fn('Unknown choice. Please enter 0-8.')
        except (ValueError, LookupError) as error:
            output_fn(f'Error: {error}')
        except EOFError:
            output_fn('Input ended. Exiting; session data is discarded.')
            return

