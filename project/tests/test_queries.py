from datetime import datetime

import pytest

from smartcare.domain import (
    Appointment,
    AppointmentStatus,
    Patient,
    Practitioner,
)
from smartcare.queries import appointment_sort_key, select_appointments

NINE = datetime(2026, 10, 1, 9, 0)
TEN = datetime(2026, 10, 1, 10, 0)

#data for each test
#the list is deliberately out of order
def make_data():
    patient = Patient('P1', 'Alex Example')
    d1 = Practitioner('D1', 'Taylor Example', 'General')
    d2 = Practitioner('D2', 'Jordan Example', 'Dental')
    a1 = Appointment('A1', patient, d1, NINE, AppointmentStatus.SCHEDULED)
    a2 = Appointment('A2', patient, d1, NINE, AppointmentStatus.CANCELLED)
    a3 = Appointment('A3', patient, d1, TEN, AppointmentStatus.COMPLETED)
    b1 = Appointment('B1', patient, d2, NINE, AppointmentStatus.SCHEDULED)
    return [a3, b1, a2, a1]


def ids(appointments):
    return [a.appointment_id for a in appointments]

#the order and key fields for mutation detection
def snapshot(appointments):
    return [
        (a, a.appointment_id, a.practitioner, a.date_time, a.status)
        for a in appointments
    ]


#QRY-01: only the requested practitioner's appointments
def test_select_returns_only_the_requested_practitioner():
    source = make_data()
    assert ids(select_appointments(source, 'D1')) == ['A1', 'A2', 'A3']
    assert ids(select_appointments(source, 'D2')) == ['B1']

#no appointments return an empty list.
def test_select_unknown_practitioner_returns_empty_list():
    # Checks: the pure helper does not validate practitioners; an ID with

    assert select_appointments(make_data(), 'D999') == []


#QRY-02: status filtering
def test_select_default_includes_every_status():
    result = select_appointments(make_data(), 'D1')
    assert {a.status for a in result} == {
        AppointmentStatus.SCHEDULED,
        AppointmentStatus.CANCELLED,
        AppointmentStatus.COMPLETED,
    }


@pytest.mark.parametrize('status', list(AppointmentStatus))
def test_select_each_explicit_status(status):
    expected = {
        AppointmentStatus.SCHEDULED: ['A1'],
        AppointmentStatus.CANCELLED: ['A2'],
        AppointmentStatus.COMPLETED: ['A3'],
    }
    result = select_appointments(make_data(), 'D1', status)
    assert ids(result) == expected[status]


def test_select_status_with_no_match_returns_empty_list():
    result = select_appointments(
        make_data(), 'D2', AppointmentStatus.CANCELLED,
    )
    assert result == []


#QRY-03 / FP-03: ordering as well as the named key
def test_select_orders_by_time_then_appointment_id():
    result = select_appointments(make_data(), 'D1')
    assert ids(result) == ['A1', 'A2', 'A3']

#checks an earlier time even with a later ID
def test_time_is_the_primary_sort_key_not_the_id():
    patient = Patient('P1', 'Alex Example')
    d1 = Practitioner('D1', 'Taylor Example', 'General')
    late_low_id = Appointment('A1', patient, d1, TEN)
    early_high_id = Appointment('A9', patient, d1, NINE)
    result = select_appointments([late_low_id, early_high_id], 'D1')
    assert ids(result) == ['A9', 'A1']

#should return exactly date_time and appointment_id
def test_sort_key_returns_time_then_id():
    appointment = make_data()[3]  # A1
    assert appointment_sort_key(appointment) == (NINE, 'A1')

#checks equal times and compares IDs.
def test_sort_key_orders_equal_times_by_id():
    # Checks: for equal times the key compares by ID.
    a1, a2 = make_data()[3], make_data()[2]  # A1, A2 (both 09:00)
    assert appointment_sort_key(a1) < appointment_sort_key(a2)


#FP-01 / FP-02: purity, new list, unchanged inputs
def test_select_does_not_change_the_source_list_or_objects():
    source = make_data()
    before = snapshot(source)
    select_appointments(source, 'D1')
    assert snapshot(source) == before
    assert ids(source) == ['A3', 'B1', 'A2', 'A1']

#checks the result is a different list
def test_select_returns_a_new_list_with_the_same_objects():
    source = make_data()
    result = select_appointments(source, 'D1')
    assert result is not source
    assert all(any(r is s for s in source) for r in result)

#even an empty or sorted input can get a new list back
@pytest.mark.parametrize('kind', ['empty', 'already_sorted', 'unsorted'])
def test_select_returns_a_distinct_list_for_any_input(kind):
    data = make_data()
    sources = {
        'empty': [],
        'already_sorted': [data[3], data[2], data[0]],  # A1, A2, A3
        'unsorted': data,
    }
    source = sources[kind]
    assert select_appointments(source, 'D1') is not source

#unchanged inputs should have the same result
def test_select_repeated_calls_give_the_same_result():
    source = make_data()
    first = select_appointments(source, 'D1', AppointmentStatus.CANCELLED)
    second = select_appointments(source, 'D1', AppointmentStatus.CANCELLED)
    assert first == second
    assert ids(first) == ['A2']