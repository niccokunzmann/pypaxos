from pytest import *

@fixture()
def lala():
    return []

@fixture()
def lili(lala):
    return [lala]

def test_identity_of_fixtures(lala, lili):
    assert lala is lili[0]

