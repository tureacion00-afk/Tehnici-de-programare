from arsenal.web.client import exista


def test_exista():
    # Verifica ca functia intoarce True pe o pagina valida de test
    assert exista("http://example.com/") is True


def test_lipsa():
    # Verifica ca functia intoarce False pe o pagina inexistenta
    assert exista("http://example.com/zzz_cale_inexistenta_12345") is False
