import re
from collections import Counter

TIPAR = re.compile(r"Failed password for (?:invalid user )?(\S+) from (\S+) port")

def esec(linie):
    m = TIPAR.search(linie)
    if m is None:
        return None
    return (m.group(1), m.group(2))

def citeste_esecuri(cale):
    esecuri = []
    try:
        f = open(cale, encoding="utf-8")
    except FileNotFoundError:
        print("nu gasesc", cale)
        return esecuri
    with f:
        for linie in f:
            r = esec(linie)
            # Dacă r nu e None (e o linie validă de eșec), o adăugăm ca dicționar
            if r is not None:   
                esecuri.append({"user": r[0], "ip": r[1]})
    return esecuri

def pe_ip(esecuri):
    # Întoarce un obiect Counter cu aparițiile fiecărui IP
    return Counter(e["ip"] for e in esecuri)

def main():
    cale_log = "arsenal/aparare/start/auth.log"
    esecuri = citeste_esecuri(cale_log)
    
    print(f"Esecuri de autentificare: {len(esecuri)}")
    
    counts = pe_ip(esecuri)
    for ip, n in counts.most_common():
        print(f"  {ip}: {n}")

if __name__ == "__main__":
    main()