# -*- coding: utf-8 -*-
"""Laboratorul 9 - inventar de procese si jurnal ca obiecte."""
import json
from dataclasses import dataclass, asdict

CAI_SUSPECTE = ('\\Temp\\', '\\Roaming\\')
SUSPECTE_ID = {4625, 1102, 7045}


@dataclass
class Proces:
    """Un proces de pe masina, cu patru campuri legate."""
    pid: int
    nume: str
    user: str
    cale: str

    def e_suspect(self):
        """Sarcina 1. True daca procesul ruleaza dintr-o cale suspecta.

        Intoarce True daca una din CAI_SUSPECTE apare in self.cale, altfel
        False. Un proces care ruleaza din Temp sau Roaming e un semn clasic.

        Proces(1, "x.exe", "ana", r"C:\\Users\\ana\\AppData\\Local\\Temp\\x.exe")
            .e_suspect()  ->  True
        """
        for cale in CAI_SUSPECTE:
            if cale in self.cale:
                return True
        return False


@dataclass
class Eveniment:
    """Un eveniment din jurnalul de securitate Windows."""
    id: int
    nivel: str
    sursa: str
    cont: str
    mesaj: str

    def e_suspect(self):
        """Sarcina 2. True daca evenimentul merita atentie.

        Intoarce True daca self.id e in SUSPECTE_ID SAU self.nivel este
        "critical". Altfel False.

        Eveniment(4625, "warning", "Security", "admin", "...").e_suspect() -> True
        Eveniment(6008, "critical", "EventLog", "SYSTEM", "...").e_suspect() -> True
        """
        return self.id in SUSPECTE_ID or self.nivel == "critical"


def procese_din_json(cale):
    """Sarcina 3. Incarca o lista de obiecte Proces dintr-un fisier JSON.

    Citeste fisierul si intoarce o lista de Proces. Proces(**d) despacheteaza
    un dictionar din JSON direct in campurile obiectului, pe nume.

    procese_din_json("start/procese.json")  ->  lista cu 7 obiecte Proces
    """
    with open(cale, "r", encoding="utf-8") as f:
        date = json.load(f)
        return [Proces(**d) for d in date]


def evenimente_din_json(cale):
    """Sarcina 4. Incarca o lista de obiecte Eveniment dintr-un fisier JSON.

    La fel ca procese_din_json, dar pentru Eveniment.

    evenimente_din_json("start/evenimente.json")  ->  lista cu 8 obiecte
    """
    with open(cale, "r", encoding="utf-8") as f:
        date = json.load(f)
        return [Eveniment(**d) for d in date]


# ---------------------------------------------------------------------------
#  PARTEA B - clasa Inventar si raportul
# ---------------------------------------------------------------------------

@dataclass
class Inventar:
    """Tine lista de procese si stie sa o interogheze."""
    procese: list

    @classmethod
    def din_json(cls, cale):
        """Sarcina 5. Constructor alternativ: umple inventarul din JSON.

        E o metoda de clasa (@classmethod): primeste clasa in cls si intoarce
        un Inventar nou, cu lista de procese incarcata din fisier.

        Inventar.din_json("start/procese.json")  ->  un Inventar cu 7 procese
        """
        with open(cale, "r", encoding="utf-8") as f:
            date = json.load(f)
            return cls([Proces(**d) for d in date])

    def __len__(self):
        return len(self.procese)

    def suspecte(self):
        """Sarcina 6. Lista proceselor care se declara suspecte.

        Intoarce lista obiectelor Proces din self.procese pentru care
        p.e_suspect() este True, in ordinea din inventar.
        """
        return [p for p in self.procese if p.e_suspect()]

    def pe_user(self):
        """Sarcina 7. Gruparea numelor de proces pe utilizator.

        Intoarce un dictionar user -> lista de nume de proces ale acelui
        utilizator, in ordinea din inventar. Foloseste setdefault.

        {"SYSTEM": ["System", "svchost.exe"], "ana": ["explorer.exe", ...]}
        """
        grupare = {}
        for p in self.procese:
            grupare.setdefault(p.user, []).append(p.nume)
        return grupare


def raport(dosar):
    """Sarcina 8. Raportul complet, ca dictionar gata de pus in JSON.

    Primeste folderul capturilor. Incarca procesele si evenimentele, apoi
    intoarce un dictionar cu patru chei:

        {"procese": numarul de procese,
         "suspecte": [asdict(p) pentru fiecare proces suspect],
         "evenimente": numarul de evenimente,
         "alarma": [asdict(e) pentru fiecare eveniment suspect]}

    asdict(obiect) transforma un obiect @dataclass inapoi in dictionar.
    Nu tipari nimic aici; doar intoarce.
    """
    import os

    cale_procese = os.path.join(dosar, "procese.json")
    cale_evenimente = os.path.join(dosar, "evenimente.json")

    inv = Inventar.din_json(cale_procese)
    evenimente = evenimente_din_json(cale_evenimente)

    procese_suspecte = [asdict(p) for p in inv.suspecte()]
    evenimente_alarma = [asdict(e) for e in evenimente if e.e_suspect()]

    return {
        "procese": len(inv),
        "suspecte": procese_suspecte,
        "evenimente": len(evenimente),
        "alarma": evenimente_alarma,
    }


#

def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('capturi')
    p.add_argument('--json', action='store_true')
    a = p.parse_args()
    inv = Inventar.din_json(a.capturi + '/procese.json')
    ev = evenimente_din_json(a.capturi + '/evenimente.json')
    alarma = [e for e in ev if e.e_suspect()]
    if a.json:
        print(json.dumps(raport(a.capturi), indent=2, ensure_ascii=False))
        return
    sus = inv.suspecte()
    print('Procese: %d | suspecte: %d' % (len(inv), len(sus)))
    for p in sus:
        print('  [%d] %s  (%s)  %s' % (p.pid, p.nume, p.user, p.cale))
    print('Evenimente: %d | alarma: %d' % (len(ev), len(alarma)))
    for e in alarma:
        print('  %d [%s] %s: %s' % (e.id, e.nivel, e.cont, e.mesaj))


if __name__ == '__main__':
    main()
