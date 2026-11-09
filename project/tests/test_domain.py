import pytest

from smartcare.domain import Patient, Practitioner


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