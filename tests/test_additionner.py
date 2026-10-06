from src.sncf_project import additionner

def test_additionner_positif():
    assert additionner(1, 2) == 3

def test_additionner_negatif():
    assert additionner(-1, -2) == -3
    
def test_additionner_mixte():
    assert additionner(1, -2) == -1