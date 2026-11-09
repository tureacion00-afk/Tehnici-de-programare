import argparse
import json
from collections import Counter
from arsenal.aparare.parse_auth import citeste_esecuri

def suspecti(counts, prag=10):
    if prag < 1:
        raise ValueError(f"prag invalid: {prag} (cel putin 1)")
    
    lista_suspecti = []
    for ip, n in counts.items():
        if n >= prag:
            lista_suspecti.append((ip, n))
            
    lista_suspecti.sort(key=lambda x: x[1], reverse=True)
    return lista_suspecti

def main():
    p = argparse.ArgumentParser()
    p.add_argument("log")
    p.add_argument("--prag", type=int, default=10)
    p.add_argument("--json", action="store_true")
    # OPTIONAL 3: Am adaugat argumentul --top
    p.add_argument("--top", type=int, help="scoate doar primele N adrese")
    a = p.parse_args()
    
    esecuri = citeste_esecuri(a.log)
    counts = Counter(e["ip"] for e in esecuri)
    sus = suspecti(counts, a.prag)
    
    if a.json:
        raport = {
            "esecuri": esecuri,
            "pe_ip": dict(counts),
            "suspecti": sus
        }
        print(json.dumps(raport, indent=2))
    else:
        print(f"Esecuri de autentificare: {len(esecuri)}")
        
        # OPTIONAL 3: List comprehension peste most_common
        toate_adresele = counts.most_common()
        adrese_de_afisat = [(ip, n) for ip, n in toate_adresele][:a.top] if a.top else toate_adresele
        
        for ip, n in adrese_de_afisat:
            print(f"  {ip}: {n}")
            
        print(f"\nSuspecti (prag {a.prag}):")
        for ip, n in sus:
            print(f"  {ip}  ({n} incercari)  BRUTE FORCE")

if __name__ == "__main__":
    main()