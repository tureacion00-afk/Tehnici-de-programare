import requests
from arsenal.comun import TIMEOUT


def cere(url, **kw):
    # Wrapper peste requests.get cu timeout setat
    return requests.get(url, timeout=TIMEOUT, **kw)


def exista(url):
    # Intoarce True daca resursa returneaza status 200 OK
    try:
        r = cere(url)
        return r.status_code == 200
    except requests.RequestException:
        return False
