import requests

SITES = [
    # Pagini obișnuite (Părțile 2, 3 și 4)
    "https://example.com",
    "https://httpbin.org/html",
    "https://httpbin.org/json",
    "https://httpbin.org/status/200",
    "https://httpbin.org/redirect/1",
    "https://httpbin.org/delay/2",
    # Pagini care eșuează
    "https://httpbin.org/status/404",
    "https://httpbin.org/status/500",
    "https://httpbin.org/delay/10",
    "http://this-site-does-not-exist.invalid",
    # Anteturi de securitate (Partea 5)
    "https://httpbin.org/response-headers?X-Frame-Options=DENY&X-Content-Type-Options=nosniff",
    "https://httpbin.org/response-headers?x-frame-options=DENY",
    # Răspunde aleatoriu cu 200 sau 500 (Partea 6)
    "https://httpbin.org/status/200,500",
]

SECURITY_HEADERS = [
    "Strict-Transport-Security",
    "Content-Security-Policy",
    "X-Frame-Options",
    "X-Content-Type-Options",
]


def build_url(host, path):
    """Returnează o adresă completă, de exemplu https://example.com/login."""
    host = host.strip()
    if not host.startswith(("http://", "https://")):
        host = "https://" + host
    host = host.rstrip("/")
    if not path:
        return host
    return f"{host}/{path.lstrip('/')}"


def is_https(url):
    """Returnează True dacă adresa începe cu https://, altfel False."""
    return url.startswith("https://")


def show_response(url):
    """Trimite un GET la url și afișează statusul și Content-Type."""
    try:
        r = requests.get(url, timeout=5)
        print(f"Status: {r.status_code}")
        print(f"Content-Type: {r.headers.get('Content-Type', 'unknown')}")
    except requests.exceptions.RequestException as e:
        print(f"Eroare: {e}")


def check_site(url):
    """Returnează un dicționar cu status, content_type, length, server."""
    try:
        r = requests.get(url, timeout=5)
        ct = r.headers.get("Content-Type", "unknown").split(";")[0].strip()
        return {
            "status": r.status_code,
            "content_type": ct,
            "length": len(r.content),
            "server": r.headers.get("Server", "unknown"),
        }
    except requests.exceptions.RequestException as e:
        return {"status": None, "error": str(e)[:100]}


def scan_sites():
    """Verifică toate site-urile din SITES, afișează-le pe cele cu 200 și un rezumat."""
    rez = []
    for url in SITES:
        rez.append((url, check_site(url)))

    ok = [(u, r) for u, r in rez if r.get("status") == 200]
    ok.sort(key=lambda x: x[1].get("length", 0), reverse=True)

    for u, r in ok:
        print(f"{u} -> {r['status']}, {r['length']} octeti")

    print(f"Reușite: {len(ok)} | Eșuate: {len(rez) - len(ok)}")


def check_headers(url):
    """Verifică antetele de securitate: present, missing, score."""
    try:
        r = requests.get(url, timeout=5)
        chei = {k.lower() for k in r.headers.keys()}
        present = [h for h in SECURITY_HEADERS if h.lower() in chei]
        missing = [h for h in SECURITY_HEADERS if h.lower() not in chei]
        score = int(len(present) / len(SECURITY_HEADERS) * 100)
        return {"present": present, "missing": missing, "score": score}
    except requests.exceptions.RequestException as e:
        return {"status": None, "error": str(e)[:100]}


def retry_check(url, attempts=3):
    """Încearcă din nou la eroare de conexiune sau status >= 500."""
    last_status = None
    last_error = None

    for i in range(1, attempts + 1):
        try:
            r = requests.get(url, timeout=5)
            last_status = r.status_code
            last_error = None
            if r.status_code < 500:
                return {"status": last_status, "attempts": i}
        except requests.exceptions.RequestException as e:
            last_error = str(e)[:100]

    rez = {"status": last_status, "attempts": attempts}
    if last_status is None and last_error is not None:
        rez["error"] = last_error
    return rez