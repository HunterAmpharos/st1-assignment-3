from datetime import datetime, timezone

import pytest

from smartcare.domain import (
    Appointment,
    AppointmentStatus,
    Patient,
    Practitioner,
)

WHEN = datetime(2026, 10, 1, 9, 0) #fixed date

#a new appointment that can be used for future tests
def make_appointment(status=AppointmentStatus.SCHEDULED):
    patient = Patient('P1', 'Alex Example')
    practitioner = Practitioner('D1', 'Taylor Example', 'General')
    return Appointment('A1', patient, practitioner, WHEN, status)

#PATIENT AND PRACTITONER DOMAIN TESTS

#T7-01: only valid patient data should be stored
def test_patient_stores_valid_id_and_name():
    patient = Patient('P1', 'Alex Example')
    assert patient.patient_id == 'P1'
    assert patient.name == 'Alex Example'

#T7-02: any blank fields should be rejected (raise ValueError)
#checks bad ID
@pytest.mark.parametrize('bad_id', ['', '   ', None])
def test_patient_blank_id_is_rejected(bad_id):
    with pytest.raises(ValueError):
        Patient(bad_id, 'Alex Example')

#checks bad name
@pytest.mark.parametrize('bad_name', ['', '   ', None])
def test_patient_blank_name_is_rejected(bad_name):
    with pytest.raises(ValueError):
        Patient('P1', bad_name)


#T7-03: IDs are trimmed but stay case sensetive
def test_patient_id_is_trimmed():
    assert Patient('  P1  ', 'Alex Example').patient_id == 'P1'


def test_patient_id_is_case_sensitive():
    assert Patient('p1', 'Alex Example').patient_id == 'p1'


#T7-04: only valid practitioner data should be stored
def test_practitioner_stores_valid_fields():
    practitioner = Practitioner('D1', 'Taylor Example', 'General')
    assert practitioner.practitioner_id == 'D1'
    assert practitioner.name == 'Taylor Example'
    assert practitioner.specialty == 'General'


#T7-05: any blank fields should be rejected (raise ValueError)
#check bad ID
@pytest.mark.parametrize('bad_id', ['', '   ', None])
def test_practitioner_blank_id_is_rejected(bad_id):
    with pytest.raises(ValueError):
        Practitioner(bad_id, 'Taylor Example', 'General')

#check bad Name
@pytest.mark.parametrize('bad_name', ['', '   ', None])
def test_practitioner_blank_name_is_rejected(bad_name):
    with pytest.raises(ValueError):
        Practitioner('D1', bad_name, 'General')

#check bad Specialty
@pytest.mark.parametrize('bad_specialty', ['', '   ', None])
def test_practitioner_blank_specialty_is_rejected(bad_specialty):
    with pytest.raises(ValueError):
        Practitioner('D1', 'Taylor Example', bad_specialty)

#APPOINTMENT DOMAIN TESTS

#T7-06: a new appointment should keep its data and starts SCHEDULED
def test_new_appointment_starts_scheduled_and_keeps_its_data():
    patient = Patient('P1', 'Alex Example')
    practitioner = Practitioner('D1', 'Taylor Example', 'General')
    appointment = Appointment('A1', patient, practitioner, WHEN)
    assert appointment.appointment_id == 'A1'
    assert appointment.patient is patient
    assert appointment.practitioner is practitioner
    assert appointment.date_time == WHEN
    assert appointment.status is AppointmentStatus.SCHEDULED


#T7-07: invalid appointment inputs should be rejected
#a bad ID
@pytest.mark.parametrize('bad_id', ['', '   ', None])
def test_appointment_blank_id_is_rejected(bad_id):
    patient = Patient('P1', 'Alex Example')
    practitioner = Practitioner('D1', 'Taylor Example', 'General')
    with pytest.raises(ValueError):
        Appointment(bad_id, patient, practitioner, WHEN)

#a bad patient
@pytest.mark.parametrize('bad_patient', ['P1', None])
def test_appointment_requires_a_patient_object(bad_patient):
    practitioner = Practitioner('D1', 'Taylor Example', 'General')
    with pytest.raises(ValueError):
        Appointment('A1', bad_patient, practitioner, WHEN)

#a bad practitioner
@pytest.mark.parametrize('bad_practitioner', ['D1', None])
def test_appointment_requires_a_practitioner_object(bad_practitioner):
    patient = Patient('P1', 'Alex Example')
    with pytest.raises(ValueError):
        Appointment('A1', patient, bad_practitioner, WHEN)

#checks that status is AppointmentStatus
def test_appointment_rejects_an_invalid_status():
    patient = Patient('P1', 'Alex Example')
    practitioner = Practitioner('D1', 'Taylor Example', 'General')
    with pytest.raises(ValueError):
        Appointment('A1', patient, practitioner, WHEN, 'scheduled')

#checks for a bad time
@pytest.mark.parametrize('bad_time', [
    '2026-10-01 09:00',                              #this is text and not in the right format
    datetime(2026, 10, 1, 9, 0, 30),                 #has seconds added
    datetime(2026, 10, 1, 9, 0, tzinfo=timezone.utc),  #provides an unnecessary timezone
])

#only minute datetime should be accepted
def test_appointment_rejects_invalid_date_time(bad_time):
    patient = Patient('P1', 'Alex Example')
    practitioner = Practitioner('D1', 'Taylor Example', 'General')
    with pytest.raises(ValueError):
        Appointment('A1', patient, practitioner, bad_time)


#T7-08: check to see if cancelling an appointment works (should set status to CANCELLED)
def test_cancel_changes_scheduled_to_cancelled():
    appointment = make_appointment()
    appointment.cancel()
    assert appointment.status is AppointmentStatus.CANCELLED


#T7-09: repeated cancellation is rejected (so no second cancel())
def test_repeated_cancellation_is_rejected_and_status_unchanged():
    appointment = make_appointment()
    appointment.cancel()
    with pytest.raises(ValueError):
        appointment.cancel()
    assert appointment.status is AppointmentStatus.CANCELLED


#T7-10: if an appointment already has the status COMPLETED it cannot be cancelled afterwards
def test_completed_appointment_cannot_be_cancelled():
    appointment = make_appointment(AppointmentStatus.COMPLETED)
    with pytest.raises(ValueError):
        appointment.cancel()
    assert appointment.status is AppointmentStatus.COMPLETED