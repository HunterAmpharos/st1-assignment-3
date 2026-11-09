from smartcare.data_store import SmartCareDataStore
from smartcare.services import PatientService
from smartcare.services import PractitionerService
from datetime import datetime
from smartcare.domain import AppointmentStatus
from smartcare.services import (
    AppointmentService,
    PatientService,
    PractitionerService,
)
import pytest

#PATIENT ID SEARCH
#first test here checks if a patient can be found via their ID
def test_find_patient_returns_the_registered_patient():
    store = SmartCareDataStore()
    patients = PatientService(store)
    patient = patients.register_patient('P1', 'Alex Example')

    result = patients.find_patient('P1')

    assert result is patient

#if a patient ID is unknown then it should raise an error
def test_find_patient_unknown_id_raises_error():
    store = SmartCareDataStore()
    patients = PatientService(store)

    with pytest.raises(LookupError):
        patients.find_patient('P999')

#if an ID has been typed in with spaces it should still be searchable
def test_find_patient_ignores_spaces_around_id():
    store = SmartCareDataStore()
    patients = PatientService(store)
    patient = patients.register_patient('P1', 'Alex Example')

    assert patients.find_patient('  P1  ') is patient

#IDs are case sensitive so this system should check for case
def test_find_patient_is_case_sensitive():
    store = SmartCareDataStore()
    patients = PatientService(store)
    patients.register_patient('P1', 'Alex Example')

    with pytest.raises(LookupError):
        patients.find_patient('p1')

#if an ID is bad it should raise an error
@pytest.mark.parametrize('bad_id', ['', '   ', None, 5])
def test_find_patient_invalid_id_raises_value_error(bad_id):
    store = SmartCareDataStore()
    patients = PatientService(store)

    with pytest.raises(ValueError):
        patients.find_patient(bad_id)

#PRACTITONER ID SEARCH
#first test here checks if a practitioner can be found via their ID
def test_find_practitioner_returns_the_registered_practitioner():
    store = SmartCareDataStore()
    practitioners = PractitionerService(store)
    practitioner = practitioners.register_practitioner('D1', 'Taylor Example', 'General')

    result = practitioners.find_practitioner('D1')

    assert result is practitioner

#an unknown ID will raise an error
def test_find_practitioner_unknown_id_raises_error():
    store = SmartCareDataStore()
    practitioners = PractitionerService(store)

    with pytest.raises(LookupError):
        practitioners.find_practitioner('D999')

#spaces are ignored when searching for an ID
def test_find_practitioner_ignores_spaces_around_id():
    store = SmartCareDataStore()
    practitioners = PractitionerService(store)
    practitioner = practitioners.register_practitioner('D1', 'Taylor Example', 'General')

    assert practitioners.find_practitioner('  D1  ') is practitioner

#IDs should be case sensitive
def test_find_practitioner_is_case_sensitive():
    store = SmartCareDataStore()
    practitioners = PractitionerService(store)
    practitioners.register_practitioner('D1', 'Taylor Example', 'General')

    with pytest.raises(LookupError):
        practitioners.find_practitioner('d1')

#if an ID is bad it should raise an error
@pytest.mark.parametrize('bad_id', ['', '   ', None, 5])
def test_find_practitioner_invalid_id_raises_value_error(bad_id):
    store = SmartCareDataStore()
    practitioners = PractitionerService(store)

    with pytest.raises(ValueError):
        practitioners.find_practitioner(bad_id)

#APPOINTMENT CANCELLATION
WHEN = datetime(2026, 10, 1, 9, 0)

#creates a store that has 1 patient, 1 practitoner and 1 appointment (A1)
#each future test for appointment cancellation calls this particular booking
def make_booked():
    store = SmartCareDataStore()
    patients = PatientService(store)
    practitioners = PractitionerService(store)
    appointments = AppointmentService(store)
    patients.register_patient('P1', 'Alex Example')
    practitioners.register_practitioner('D1', 'Taylor Example', 'General')
    appointment = appointments.book_appointment('A1', 'P1', 'D1', WHEN)
    return store, appointments, appointment

#cancels the appointment and sets its status to CANCELLED while also returning the same object
def test_cancel_sets_cancelled_and_returns_same_object():
    store, appointments, appointment = make_booked()
    result = appointments.cancel_appointment('A1')
    assert result is appointment
    assert result.status is AppointmentStatus.CANCELLED

#checks that the appointment can still be found even after the appointment has been cancelled
def test_cancelled_appointment_is_retained():
    store, appointments, appointment = make_booked()
    appointments.cancel_appointment('A1')
    assert appointments.find_appointment('A1') is appointment
    assert store.list_appointments() == [appointment]

#if ID is invalid then it will raise a LookupError
def test_cancel_unknown_id_raises_lookup_error():
    store, appointments, appointment = make_booked()
    with pytest.raises(LookupError):
        appointments.cancel_appointment('A999')
    assert appointment.status is AppointmentStatus.SCHEDULED

#checks blank and non-text IDs and raises a ValueError if they are present
@pytest.mark.parametrize('bad_id', ['', '   ', None, 7])
def test_cancel_invalid_id_raises_value_error(bad_id):
    store, appointments, appointment = make_booked()
    with pytest.raises(ValueError):
        appointments.cancel_appointment(bad_id)
    assert appointment.status is AppointmentStatus.SCHEDULED

#an already cancelled appointment should not be cancelled again
def test_cancelling_twice_is_rejected_and_state_unchanged():
    store, appointments, appointment = make_booked()
    appointments.cancel_appointment('A1')
    with pytest.raises(ValueError):
        appointments.cancel_appointment('A1')
    assert appointment.status is AppointmentStatus.CANCELLED

#Stage 7 service tests (T7-11 to T7-19)

#starting store used for future tests
def make_services():
    store = SmartCareDataStore()
    return (
        store,
        PatientService(store),
        PractitionerService(store),
        AppointmentService(store),
    )


#T7-11 (FR-01): checks the returned patient is the stored on and its also the only one in store
def test_register_patient_stores_the_patient():
    store, patients, _, _ = make_services()
    patient = patients.register_patient('P1', 'Alex Example')
    assert patients.find_patient('P1') is patient
    assert store.list_patients() == [patient]

#T7-12 (FR-01, AC-01.2): duplicates are rejected and only the original is kept
#this checks the second patient with the same ID and raises a ValueError
def test_duplicate_patient_id_is_rejected_and_original_kept():
    store, patients, _, _ = make_services()
    original = patients.register_patient('P1', 'Alex Example')
    with pytest.raises(ValueError):
        patients.register_patient('P1', 'Different Example')
    assert patients.find_patient('P1') is original
    assert original.name == 'Alex Example'
    assert store.list_patients() == [original]

#checks ' P1 ' and changes it to 'P1' so it is considered a duplicate
def test_duplicate_patient_id_with_spaces_is_rejected():
    store, patients, _, _ = make_services()
    original = patients.register_patient('P1', 'Alex Example')
    with pytest.raises(ValueError):
        patients.register_patient(' P1 ', 'Different Example')
    assert store.list_patients() == [original]

#checks the same rule for practitioners (the original is once again not overwritten)
def test_duplicate_practitioner_id_is_rejected_and_original_kept():
    store, _, practitioners, _ = make_services()
    original = practitioners.register_practitioner(
        'D1', 'Taylor Example', 'General',
    )
    with pytest.raises(ValueError):
        practitioners.register_practitioner('D1', 'Other Example', 'Dental')
    assert practitioners.find_practitioner('D1') is original
    assert original.specialty == 'General'
    assert store.list_practitioners() == [original]


def test_registering_invalid_patient_stores_nothing():
    # Checks: a rejected registration leaves the store empty.
    store, patients, _, _ = make_services()
    with pytest.raises(ValueError):
        patients.register_patient('   ', 'Alex Example')
    assert store.list_patients() == []


#T7-13 (FR-05): same practitioner and exact time conflicts
def test_same_practitioner_same_time_conflict_is_rejected():
    store, patients, practitioners, appointments = make_services()
    patients.register_patient('P1', 'Alex Example')
    patients.register_patient('P2', 'Sam Example')
    practitioners.register_practitioner('D1', 'Taylor Example', 'General')
    first = appointments.book_appointment('A1', 'P1', 'D1', WHEN)
    with pytest.raises(ValueError):
        appointments.book_appointment('A2', 'P2', 'D1', WHEN)
    assert store.list_appointments() == [first]

#only a 1 minute difference should be allowed
def test_same_practitioner_one_minute_later_is_allowed():
    store, patients, practitioners, appointments = make_services()
    patients.register_patient('P1', 'Alex Example')
    patients.register_patient('P2', 'Sam Example')
    practitioners.register_practitioner('D1', 'Taylor Example', 'General')
    first = appointments.book_appointment('A1', 'P1', 'D1', WHEN)
    later = appointments.book_appointment(
        'A2', 'P2', 'D1', datetime(2026, 10, 1, 9, 1),
    )
    assert store.list_appointments() == [first, later]


#T7-14 (FR-05): another practitioner at the same time should be allowed
def test_different_practitioner_same_time_is_allowed():
    # Checks: the conflict rule is per practitioner.
    store, patients, practitioners, appointments = make_services()
    patients.register_patient('P1', 'Alex Example')
    patients.register_patient('P2', 'Sam Example')
    practitioners.register_practitioner('D1', 'Taylor Example', 'General')
    practitioners.register_practitioner('D2', 'Jordan Example', 'Dental')
    first = appointments.book_appointment('A1', 'P1', 'D1', WHEN)
    second = appointments.book_appointment('A2', 'P2', 'D2', WHEN)
    assert second.status is AppointmentStatus.SCHEDULED
    assert store.list_appointments() == [first, second]


#T7-15 (FR-05, FR-06): after a booking has been cancelled, another appointment should be able to fill that slot
def test_cancelled_booking_does_not_block_the_slot():
    store, patients, practitioners, appointments = make_services()
    patients.register_patient('P1', 'Alex Example')
    patients.register_patient('P2', 'Sam Example')
    practitioners.register_practitioner('D1', 'Taylor Example', 'General')
    first = appointments.book_appointment('A1', 'P1', 'D1', WHEN)
    appointments.cancel_appointment('A1')
    second = appointments.book_appointment('A2', 'P2', 'D1', WHEN)
    assert second.status is AppointmentStatus.SCHEDULED
    assert store.list_appointments() == [first, second]


#T7-18 (FR-04): rejected bookings are not saved and the system stays the same
#invalid patient (unregistered)
def test_booking_unknown_patient_is_rejected_and_nothing_stored():
    store, _, practitioners, appointments = make_services()
    practitioners.register_practitioner('D1', 'Taylor Example', 'General')
    with pytest.raises(LookupError):
        appointments.book_appointment('A1', 'P999', 'D1', WHEN)
    assert store.list_appointments() == []

#invalid practitioner (unregistered)
def test_booking_unknown_practitioner_is_rejected_and_nothing_stored():
    store, patients, _, appointments = make_services()
    patients.register_patient('P1', 'Alex Example')
    with pytest.raises(LookupError):
        appointments.book_appointment('A1', 'P1', 'D999', WHEN)
    assert store.list_appointments() == []

#invalid time
def test_booking_with_invalid_time_is_rejected_and_nothing_stored():
    store, patients, practitioners, appointments = make_services()
    patients.register_patient('P1', 'Alex Example')
    practitioners.register_practitioner('D1', 'Taylor Example', 'General')
    with pytest.raises(ValueError):
        appointments.book_appointment(
            'A1', 'P1', 'D1', datetime(2026, 10, 1, 9, 0, 30),
        )
    assert store.list_appointments() == []

#reusing an appointment ID raises ValueError
def test_duplicate_appointment_id_is_rejected_and_original_kept():
    store, patients, practitioners, appointments = make_services()
    patients.register_patient('P1', 'Alex Example')
    practitioners.register_practitioner('D1', 'Taylor Example', 'General')
    original = appointments.book_appointment('A1', 'P1', 'D1', WHEN)
    with pytest.raises(ValueError):
        appointments.book_appointment(
            'A1', 'P1', 'D1', datetime(2026, 10, 2, 9, 0),
        )
    assert appointments.find_appointment('A1') is original
    assert original.date_time == WHEN
    assert store.list_appointments() == [original]


#T7-19 (FR-08): appointment lookup (a known ID should be "findable")
def test_find_appointment_returns_the_booked_object():
    _, patients, practitioners, appointments = make_services()
    patients.register_patient('P1', 'Alex Example')
    practitioners.register_practitioner('D1', 'Taylor Example', 'General')
    booked = appointments.book_appointment('A1', 'P1', 'D1', WHEN)
    assert appointments.find_appointment('A1') is booked

#unregisted ID raises LookupError
def test_find_appointment_unknown_id_raises_lookup_error():
    _, _, _, appointments = make_services()
    with pytest.raises(LookupError):
        appointments.find_appointment('A999')