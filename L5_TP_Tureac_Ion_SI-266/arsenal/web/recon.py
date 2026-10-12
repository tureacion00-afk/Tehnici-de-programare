import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import json
import re
import argparse
from arsenal.web.client import cere, exista


# A1. Fingerprinting antete HTTP
def inspecteaza_antete(tinta: str) -> dict:
    try:
        r = cere(tinta)
        print(f"[*] Cod raspuns: {r.status_code}")
        server = r.headers.get("Server", "Necunoscut")
        powered_by = r.headers.get("X-Powered-By", "Nespecificat")
        print(f"[*] Server: {server}")
        print(f"[*] X-Powered-By: {powered_by}")
        return {"cod": r.status_code, "server": server, "x_powered_by": powered_by, "text": r.text}
    except Exception as e:
        print(f"[-] Eroare la conectare catre {tinta}: {e}")
        return {"cod": None, "server": None, "x_powered_by": None, "text": ""}


# A2. robots.txt - extragere reguli Disallow
def inspecteaza_robots(tinta: str) -> list[str]:
    url_robots = tinta.rstrip("/") + "/robots.txt"
    linii_disallow = []
    try:
        r = cere(url_robots)
        if r.status_code == 200:
            print("[*] robots.txt gasit:")
            for linie in r.text.splitlines():
                if linie.strip().lower().startswith("disallow:"):
                    cale = linie.split(":", 1)[1].strip()
                    linii_disallow.append(cale)
                    print(f"     Disallow: {cale}")
        else:
            print(f"[-] robots.txt lipseste (status {r.status_code})")
    except Exception as e:
        print(f"[-] Eroare la citire robots.txt: {e}")
    return linii_disallow


# A3. Descoperitor de directoare dintr-o lista de cuvinte
def descopera_directoare(tinta: str, cuvinte: list[str]) -> list[str]:
    gasite = []
    print("[*] Incepere scanare directoare...")
    for c in cuvinte:
        c = c.strip()
        if not c:
            continue
        url_verif = tinta.rstrip("/") + "/" + c
        try:
            r = cere(url_verif)
            if r.status_code == 200:
                gasite.append(c)
                print(f"     [+] Gasit (200): /{c}")
            elif r.status_code == 403:
                print(f"     [!] Interzis (403 interesant): /{c}")
        except Exception:
            pass
    return gasite


# A4. Extragere link-uri din pagina principala
def extrage_linkuri(text_html: str) -> list[str]:
    linkuri = re.findall(r'href="([^"]+)"', text_html)
    unice = sorted(list(set(linkuri)))
    return unice


def main():
    parser = argparse.ArgumentParser(description="Recon Web - Laborator 5 (Nucleu)")
    parser.add_argument("tinta", help="URL-ul aplicatiei tinta (ex: http://192.168.56.101/ sau http://tinta-lab/)")
    parser.add_argument("--wordlist", default=None, help="Cale catre fisier wordlist custom")
    parser.add_argument("--iesire", default="arsenal/web/fisa.json", help="Calea fisei JSON de iesire")

    args = parser.parse_args()
    tinta = args.tinta

    print("=" * 60)
    print(f"RECON WEB PE TINTA: {tinta}")
    print("=" * 60)

    # A1. Fingerprinting
    info = inspecteaza_antete(tinta)

    # A2. robots.txt
    disallow = inspecteaza_robots(tinta)

    # A3 & A6. Wordlist directoare
    if args.wordlist and os.path.exists(args.wordlist):
        with open(args.wordlist, "r", encoding="utf-8") as f:
            cuvinte = [linie.strip() for linie in f if linie.strip()]
    else:
        cuvinte = ["admin", "login", "backup", "config", "test", "uploads", "phpmyadmin", "dvwa", "mutillidae"]

    directoare_gasite = descopera_directoare(tinta, cuvinte)

    # A4. Extragere linkuri
    linkuri = extrage_linkuri(info.get("text", ""))
    print(f"[*] Link-uri unice gasite ({len(linkuri)}):")
    for link in linkuri[:8]:
        print(f"     -> {link}")

    # A7. Salvare fisa JSON
    fisa = {
        "tinta": tinta,
        "server": info.get("server"),
        "x_powered_by": info.get("x_powered_by"),
        "disallow": disallow,
        "directoare": directoare_gasite,
        "linkuri": linkuri
    }

    os.makedirs(os.path.dirname(args.iesire), exist_ok=True)
    with open(args.iesire, "w", encoding="utf-8") as f:
        json.dump(fisa, f, indent=2, ensure_ascii=False)
    print(f"\n[+] Fisa recon salvata cu succes in: {args.iesire}")


if __name__ == "__main__":
    main()
