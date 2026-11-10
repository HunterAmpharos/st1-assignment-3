from datetime import datetime

import pytest

from smartcare.console import run_menu
from smartcare.data_store import SmartCareDataStore
from smartcare.domain import AppointmentStatus
from smartcare.services import (
    AppointmentService,
    PatientService,
    PractitionerService,
)

NINE = datetime(2026, 10, 1, 9, 0)

#a new store that is shared by all services
def make_services():
    store = SmartCareDataStore()
    return (
        store,
        PatientService(store),
        PractitionerService(store),
        AppointmentService(store),
    )

#runs menu and returns everything
def session(*answers):
    #menu always exists
    remaining = iter(list(answers) + ['0'])
    printed = []

    def fake_input(prompt):
        return next(remaining)

    run_menu(fake_input, printed.append)
    return printed


#Integrated service sequence (UI-01)

#WF-01: register, book, conflict, other practitioner, cancel, list, rebook (all the functions)
def test_full_service_workflow():
    store, patients, practitioners, appointments = make_services()
    patients.register_patient('P1', 'Alex Example')
    practitioners.register_practitioner('D1', 'Taylor Example', 'General')
    practitioners.register_practitioner('D2', 'Jordan Example', 'Dental')

    a1 = appointments.book_appointment('A1', 'P1', 'D1', NINE)
    before = list(store.list_appointments())
    with pytest.raises(ValueError):
        appointments.book_appointment('A9', 'P1', 'D1', NINE)
    assert store.list_appointments() == before  # conflict stored nothing

    # The same patient with another practitioner at the same time is
    # allowed: the conflict rule is per practitioner only.
    a2 = appointments.book_appointment('A2', 'P1', 'D2', NINE)
    assert a2.status is AppointmentStatus.SCHEDULED

    appointments.cancel_appointment('A1')
    assert appointments.find_appointment('A1') is a1
    assert a1.status is AppointmentStatus.CANCELLED

    assert appointments.list_practitioner_appointments('D1') == [a1]
    assert appointments.list_practitioner_appointments(
        'D1', AppointmentStatus.SCHEDULED,
    ) == []

    a3 = appointments.book_appointment('A3', 'P1', 'D1', NINE)  # freed slot
    assert appointments.list_practitioner_appointments('D1') == [a1, a3]
    assert appointments.list_practitioner_appointments(
        'D1', AppointmentStatus.SCHEDULED,
    ) == [a3]


#WF-02: failed bookings don't reserve an ID
def test_rejected_operations_preserve_state_and_do_not_reserve_ids():
    store, patients, practitioners, appointments = make_services()
    patient = patients.register_patient('P1', 'Alex Example')
    practitioners.register_practitioner('D1', 'Taylor Example', 'General')
    booked = appointments.book_appointment('A1', 'P1', 'D1', NINE)

    with pytest.raises(ValueError):
        patients.register_patient('P1', 'Other Example')          # duplicate
    with pytest.raises(LookupError):
        appointments.book_appointment('A5', 'P999', 'D1', NINE)   # unknown
    with pytest.raises(ValueError):
        appointments.book_appointment('A6', 'P1', 'D1', NINE)     # conflict

    assert store.list_patients() == [patient]
    assert patient.name == 'Alex Example'
    assert store.list_appointments() == [booked]

    #ID should still be avaliable
    later = appointments.book_appointment(
        'A5', 'P1', 'D1', datetime(2026, 10, 1, 10, 0),
    )
    assert later.appointment_id == 'A5'


#WF-03: no repeated cancellation
def test_repeated_cancellation_rejected_and_history_retained():
    store, patients, practitioners, appointments = make_services()
    patients.register_patient('P1', 'Alex Example')
    practitioners.register_practitioner('D1', 'Taylor Example', 'General')
    a1 = appointments.book_appointment('A1', 'P1', 'D1', NINE)
    appointments.cancel_appointment('A1')
    with pytest.raises(ValueError):
        appointments.cancel_appointment('A1')
    assert a1.status is AppointmentStatus.CANCELLED
    assert store.list_appointments() == [a1]


#The real console menu (UI-01 / UI-02)

#CON-01: UI demonstration from start
def test_console_ui01_demonstration():
    out = session(
        '1', 'P1', 'Alex Example',
        '3', 'D1', 'Taylor Example', 'General',
        '3', 'D2', 'Jordan Example', 'Dental',
        '2', 'P1',
        '4', 'D1',
        '5', 'A1', 'P1', 'D1', '2026-10-01 09:00',
        '5', 'A9', 'P1', 'D1', '2026-10-01 09:00',
        '5', 'A2', 'P1', 'D2', '2026-10-01 09:00',
        '6', 'A1',
        '7', 'A1',
        '8', 'D1', '',
        '8', 'D1', 'scheduled',
        '5', 'A3', 'P1', 'D1', '2026-10-01 09:00',
        '8', 'D1', '',
    )
    assert 'Registered patient P1: Alex Example' in out
    assert 'Found patient P1: Alex Example' in out
    assert 'Found practitioner D1: Taylor Example (General)' in out
    assert 'Booked A1: P1 with D1, 2026-10-01 09:00, scheduled' in out
    assert ('Error: Practitioner already has a SCHEDULED appointment '
            'at this time') in out
    assert 'Booked A2: P1 with D2, 2026-10-01 09:00, scheduled' in out
    assert 'Cancelled A1: P1 with D1, 2026-10-01 09:00, cancelled' in out
    assert 'A1: P1 with D1, 2026-10-01 09:00, cancelled' in out
    assert 'No matching appointments.' in out  # D1 scheduled-only, slot free
    assert 'Booked A3: P1 with D1, 2026-10-01 09:00, scheduled' in out
    assert out[-1] == 'See ya later! Anything unsaved will be lost'


#CON-02: an invalid menu choice should repeat
def test_console_unknown_choice_recovers():
    out = session('9')
    assert 'Unknown choice. Please enter 0-8.' in out
    assert sum(1 for line in out if '-=SmartCare Menu=-' in line) == 2


#CON-03: incorrect date information should not be stored
def test_console_incorrect_date_time_stores_nothing():
    out = session(
        '1', 'P1', 'Alex Example',
        '3', 'D1', 'Taylor Example', 'General',
        '5', 'A5', 'P1', 'D1', 'not a date',
        '7', 'A5',
    )
    assert 'Error: Use date/time format YYYY-MM-DD HH:MM' in out
    assert 'Error: Appointment not found' in out  # A5 was never stored


#CON-04: impossible calendar date rejected
def test_console_impossible_date_is_rejected():
    out = session(
        '1', 'P1', 'Alex Example',
        '3', 'D1', 'Taylor Example', 'General',
        '5', 'A5', 'P1', 'D1', '2026-02-30 09:00',
    )
    assert 'Error: Invalid calendar date/time; use YYYY-MM-DD HH:MM' in out


#CON-05: duplicate registration is rejected
def test_console_duplicate_registration_keeps_original():
    out = session(
        '1', 'P1', 'Alex Example',
        '1', 'P1', 'Other Example',
        '2', 'P1',
    )
    assert 'Error: Patient ID already exists' in out
    assert 'Found patient P1: Alex Example' in out
    assert 'Found patient P1: Other Example' not in out


#CON-06: blank and unknown IDs are reported
def test_console_blank_and_unknown_ids_are_reported():
    out = session('2', '', '2', 'P404', '4', 'D404', '7', 'A404')
    assert 'Error: Patient ID cannot be blank' in out
    assert 'Error: Patient was not found' in out
    assert 'Error: Practitioner was not found' in out
    assert 'Error: Appointment not found' in out


#CON-07: unknown booking participant rejected and nothing stored
def test_console_unknown_booking_participant_stores_nothing():
    out = session(
        '3', 'D1', 'Taylor Example', 'General',
        '5', 'A1', 'P999', 'D1', '2026-10-01 09:00',
        '7', 'A1',
    )
    assert 'Error: Patient was not found' in out
    assert 'Error: Appointment not found' in out


#CON-08: repeated cancellation is rejected and history stays visible
def test_console_repeated_cancellation_is_rejected():
    out = session(
        '1', 'P1', 'Alex Example',
        '3', 'D1', 'Taylor Example', 'General',
        '5', 'A1', 'P1', 'D1', '2026-10-01 09:00',
        '6', 'A1',
        '6', 'A1',
        '7', 'A1',
    )
    assert out.count('Cancelled A1: P1 with D1, 2026-10-01 09:00, cancelled') == 1
    assert any(line.startswith('Error:') for line in out)  # second cancel
    assert out.count('A1: P1 with D1, 2026-10-01 09:00, cancelled') == 1


#CON-09: invalid listing status reported and the menu continues
def test_console_invalid_listing_status_recovers():
    out = session(
        '3', 'D1', 'Taylor Example', 'General',
        '8', 'D1', 'weird',
    )
    assert 'Error: Status must be blank, scheduled, cancelled or completed' in out
    assert out[-1] == 'See ya later! Anything unsaved will be lost'


#CON-10: listing with no matches and with unknown practitioner
def test_console_listing_no_matches_and_unknown_practitioner():
    out = session(
        '3', 'D1', 'Taylor Example', 'General',
        '8', 'D1', '',
        '8', 'D404', '',
    )
    assert 'No matching appointments.' in out
    assert 'Error: Practitioner was not found' in out


#CON-11: each new session starts empty (session-only data)
def test_console_new_session_starts_empty():
    session('1', 'P1', 'Alex Example')
    out = session('2', 'P1')
    assert 'Error: Patient was not found' in out


#CON-12: closed input ends menu instead of crashing
def test_console_closed_input_exits_cleanly():
    printed = []

    def closed_input(prompt):
        raise EOFError

    run_menu(closed_input, printed.append)
    assert 'Input ended. Exiting; session data is discarded.' in printed