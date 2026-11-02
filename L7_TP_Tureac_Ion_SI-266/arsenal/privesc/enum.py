# -*- coding: utf-8 -*-
"""Laboratorul 7 - enumerare spre root. Generat din programul
de laborator, cu codul scris de student."""
import argparse, io, json, os

GTFO = {'awk', 'vim.basic', 'nmap', 'bash', 'find', 'python3', 'perl', 'vim', 'cp', 'less'}

#  PARTEA A - aduna si grupeaza
# ---------------------------------------------------------------------------

def citeste_linii(cale):
    """Sarcina 1. Citeste un fisier si intoarce LISTA randurilor folositoare.

    Fiecare rand se curata de spatiile de la capete. Se arunca randurile
    goale si cele care incep cu diez, fiindca sunt comentarii.

    citeste_linii("start/suid.txt")  ->  lista cu 14 randuri
    """
    # TODO: deschide fisierul, parcurge randurile, intoarce lista curatata
    linii_folositoare = []
    with open(cale, 'r', encoding='utf-8') as fisier:
        for rand in fisier:
            rand_curatat = rand.strip()
            if rand_curatat and not rand_curatat.startswith('#'):
                linii_folositoare.append(rand_curatat)
    return linii_folositoare

def nume(cale):
    """Sarcina 2. Intoarce numele fisierului dintr-o cale.
    Numele decide daca binarul e periculos, nu toata calea.
    nume("/usr/bin/find")  ->  "find"
    """
    # TODO: ia ce e dupa ultimul slash. Vezi rsplit("/", 1)
    return cale.rsplit("/", 1)[-1]

def suid_constatari(cale):
    """Sarcina 3. Din fisierul SUID face o LISTA DE DICTIONARE.

    Fiecare cale UNICA, in ordine sortata, devine o fisa cu trei campuri:
        {"cale": ..., "nume": ..., "risc": "mare" sau "normal"}
    Riscul e "mare" daca numele se afla in multimea GTFO, altfel "normal".

    Atentie: in captura o cale apare de doua ori. Fisa ei apare o data.
    """
    # TODO: citeste caile, pastreaza-le pe cele unice, sorteaza-le
    #       si construieste cate un dictionar pentru fiecare
    linii = citeste_linii(cale)
    
    cai_unice = sorted(set(linii))
    
    rezultat = []
    for c in cai_unice:
        nume_fisier = nume(c)
        if nume_fisier in GTFO:
            risc_curent = "mare"
        else:
            risc_curent = "normal"
        fisa = {
            "cale": c,
            "nume": nume_fisier,
            "risc": risc_curent
        }
        rezultat.append(fisa)
    return rezultat


def sudo_constatari(cale):
    """Sarcina 4. Din fisierul sudo face o lista de dictionare.

    Un rand are forma  utilizator : drept
    Il despachetezi intr-un tuplu de doua valori, taind la PRIMUL separator:
        user, drept = rand.split(" : ", 1)
    Fiecare rand devine:
        {"user": ..., "drept": ..., "risc": "mare" sau "normal"}
    Riscul e "mare" daca in drept apare NOPASSWD, fiindca atunci comanda
    se ruleaza fara sa se ceara parola.
    """
    # TODO: pentru fiecare rand, despacheteaza si adauga dictionarul
    rezultat = []
    linii = citeste_linii(cale)
    for rand in linii:
        user, drept = rand.split(" : ", 1)
        if "NOPASSWD" in drept:
            risc = "mare"
        else:
            risc = "normal"

        fisa = {"user": user, "drept": drept, "risc": risc}
        rezultat.append(fisa)
    return rezultat


def cron_constatari(cale):
    """Sarcina 5. Din crontab face o lista de dictionare.

    Un rand de crontab are cinci campuri de timp, apoi utilizatorul si
    comanda. Desparti randul in campuri cu split(), iar:
        campul 5 (al saselea) este utilizatorul
        tot ce urmeaza, lipit la loc cu spatii, este comanda

    Fiecare rand devine:  {"user": ..., "comanda": ...}
    """
    # TODO: desparte randul in campuri si construieste dictionarul
    rezultat = []
    linii=citeste_linii(cale)
    for rand in linii:
        parti = rand.split()
        user = parti[5]
        comanda = " ".join(parti[6:])
        fisa = {"user": user, "comanda": comanda}
        rezultat.append(fisa)
    return rezultat


def enumereaza(dosar):
    """Sarcina 6. Aduna toate constatarile intr-un singur DICTIONAR.

    Primeste calea folderului cu capturi si intoarce un dictionar cu o
    cheie pe categorie, iar valoarea este lista de constatari:

        {"suid": [...], "sudo": [...], "cron": [...]}

    Pentru a lipi calea unui fisier de folder, foloseste os.path.join.
    """
    # TODO: cheama cele trei functii de mai sus si intoarce dictionarul
    cale_suid = os.path.join(dosar, "suid.txt")
    cale_sudo = os.path.join(dosar, "sudo.txt")
    cale_cron = os.path.join(dosar, "crontab.txt")
    return {"suid": suid_constatari(cale_suid),"sudo": sudo_constatari(cale_sudo),"cron": cron_constatari(cale_cron)}


def utilizatori_implicati(raport):
    """Sarcina 7. Intoarce MULTIMEA utilizatorilor care apar in raport.

    Sunt utilizatorii din constatarile sudo REUNITI cu cei din cron.
    Reuniunea a doua multimi se face cu operatorul  |  si arunca dublurile.

    Primeste dictionarul intors de enumereaza.
    """
    # TODO: fa o multime din userii sudo, alta din userii cron, reuneste-le
    raport["sudo"]
    useri_sudo = set()
    useri_cron = set()
    for intrare in raport["sudo"]:
        useri_sudo.add(intrare["user"])
    for fisa in raport["cron"]:
        useri_cron.add(fisa["user"])
    return useri_sudo | useri_cron




# ---------------------------------------------------------------------------
#  PARTEA B - ce e nou fata de un sistem curat
# ---------------------------------------------------------------------------

def cai(fisier):
    """Sarcina 8. Intoarce MULTIMEA cailor dintr-un fisier.

    Foloseste citeste_linii, pe care ai scris-o deja la sarcina 1.
    O multime arunca singura dublurile, de aceea aici iese 13, nu 14.
    """
    # TODO: intoarce multimea cailor
    multimea_cailor = set()
    multimea_cailor.update(citeste_linii(fisier))
    return multimea_cailor


def suid_noi(acum, baza):
    """Sarcina 9. Ce e in acum, dar nu si in baza.

    Amandoua sunt multimi de cai. Rezultatul este tot o multime: fisierele
    SUID aparute fata de sistemul curat.

    Se face cu UN SINGUR operator, nu cu doua bucle una in alta.
    """
    # TODO: scade multimile
    return acum - baza


def risc_pe_nume(multime_cai):
    """Sarcina 10. Fisa nume -> risc, ca DICTIONAR.

    Pentru fiecare cale din multimea primita, cheia este numele fisierului,
    iar valoarea este "mare" daca numele se afla in GTFO, altfel "normal".

    Se scrie pe un singur rand, cu dict comprehension.
    """
    # TODO: intoarce dictionarul
    rezultat = {}
    for ceva in multime_cai:
        nume_fisier = nume(ceva)
        if nume_fisier in GTFO:
            rezultat[nume_fisier] = "mare"
        else:
            rezultat[nume_fisier] = "normal"
    return rezultat


def periculoase_noi(noi):
    """Sarcina 11. Lista cailor noi care sunt periculoase, sortata.

    Din multimea primita pastrezi doar caile al caror nume e in GTFO si le
    intorci ca lista, in ordine sortata.
    """
    # TODO: filtreaza si sorteaza
    rezultat = []
    for ceva in sorted(noi):
        nume_ceva = nume(ceva)
        if nume_ceva in GTFO:
            rezultat.append(ceva)
    return rezultat


# ===========================================================================
#
#   Sub randul urmator incepe programul care te verifica.
#   Nu e nevoie sa intelegi codul de mai jos si nu il modifica.
#
# ===========================================================================
#  


def main():
    p = argparse.ArgumentParser()
    p.add_argument("capturi")
    p.add_argument("--json", action="store_true")
    a = p.parse_args()
    raport = enumereaza(a.capturi)
    if a.json:
        print(json.dumps(raport, indent=2, ensure_ascii=False))
        return
    for categorie, lista in raport.items():
        mari = [c for c in lista if c.get("risc") == "mare"]
        print("%s: %d gasite, %d cu risc mare" % (categorie, len(lista), len(mari)))
    useri = utilizatori_implicati(raport)
    print("utilizatori implicati:", ", ".join(sorted(useri)))
    with io.open("enum.json", "w", encoding="utf-8") as fis:
        json.dump(raport, fis, indent=2, ensure_ascii=False)
    print("Raport salvat in enum.json")


if __name__ == "__main__":
    main()
