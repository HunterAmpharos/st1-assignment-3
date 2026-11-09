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