# MindGuard

> Aplicație mobilă accesibilă pentru gestionarea anxietății la copii cu dizabilități

[![Python](https://img.shields.io/badge/Python-3.14-blue.svg)](https://www.python.org/)
[![Flet](https://img.shields.io/badge/Flet-cross--platform-purple.svg)](https://flet.dev/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Instagram](https://img.shields.io/badge/Instagram-@mind__guard___-E4405F.svg)](https://www.instagram.com/mind_guard_/)

## Despre proiect

**MindGuard** este o aplicație mobilă concepută special pentru a ajuta copiii — în mod special pe cei cu dizabilități vizuale, auditive, motrice sau de vorbire — să înțeleagă, să gestioneze și să prevină anxietatea.

Misiunea noastră: să facem sprijinul pentru sănătatea mintală incluziv, astfel încât fiecare copil să se simtă înțeles, în siguranță și în control asupra propriilor emoții.

## Echipa

Acest proiect a fost dezvoltat de o echipă de două eleve de clasa a XI-a:

- **Chirilus Anastasia** — Project Manager, UX Design, cercetare utilizatori, implementare Python/Flet
- **Vatamaniuc Karina** — Lead Developer, documentație, Content Creator,  arhitectură tehnică,

## Funcționalități principale

- 🎯 **Onboarding personalizat** — selectarea nevoilor specifice ale copilului (deficiențe vizuale, auditive, motrice, de vorbire) la prima utilizare
- 🌬️ **Exerciții de respirație** ghidate, cu animații vizuale (Balloon Breathing)
- 📋 **Chestionar de auto-evaluare** a stării emoționale curente
- 💬 **Forum comunitar** moderat pentru schimb de experiențe
- 🌗 **Mod de contrast înalt** pentru utilizatori cu deficiențe vizuale severe
- ⚙️ **Setări de accesibilitate** personalizabile

## Tehnologii folosite

- **Python 3.13** — limbaj principal
- **Flet** — framework cross-platform pentru UI (bazat pe Flutter)
- **asyncio** — pentru gestionarea exercițiilor temporizate
- **Git + GitHub** — versionare și colaborare

## Cum funcționează arhitectura aplicației

Aplicația folosește un model unidirecțional simplu:

1. Toată starea aplicației este centralizată într-o clasă `AppState`
2. Acțiunile utilizatorului declanșează modificări ale stării
3. Modificările de stare declanșează re-randarea UI-ului
4. Sistemul de teme (`get_colors()`) returnează paleta de culori activă, permițând comutarea instantanee între moduri vizuale

Acest model este inspirat din paradigma reactivă folosită de React și Flutter.

## Instalare și rulare

### Cerințe

- Python 3.11 sau mai recent
- Minim 200 MB spațiu liber pe disc
- Conexiune la internet (doar la prima instalare)

### Pași

```bash
# 1. Clonează repository-ul
git clone https://github.com/[username]/MindGuard.git
cd MindGuard

# 2. Creează un mediu virtual
python -m venv .venv

# 3. Activează mediul virtual
# Pe Windows:
.venv\Scripts\activate
# Pe macOS/Linux:
source .venv/bin/activate

# 4. Instalează dependențele
pip install flet

# 5. Rulează aplicația
python MindGuard.py
```

## Structura repository-ului

```
MindGuard/
├── MindGuard.py                          # Codul sursă al aplicației
├── README.md                             # Acest fișier
├── LICENSE                               # Licența MIT
├── .gitignore                            # Fișiere ignorate de Git
└── docs/
    ├── MindGuard_Documentatie_Tehnica.docx
    ├── MindGuard_Plan_Dezvoltare.docx
    └── MindGuard_Analiza_Piata.docx
```

## Documentație

Pentru detalii complete despre proiect, consultați documentele din folderul `docs/`:

- **Documentația tehnică** — descriere completă (problemă, soluție, arhitectură, ghid de instalare)
- **Planul de dezvoltare** — etape parcurse, distribuția rolurilor, roadmap viitor
- **Analiza pieței** — comparație cu aplicațiile concurente (Calm, Headspace, Wysa, MindShift)

## Resurse externe folosite

În conformitate cu regulamentul InfoEducația (art. VI), declarăm transparent toate resursele externe folosite în dezvoltarea acestui proiect:

### Biblioteci open-source

| Bibliotecă | Licență | Utilizare |
|------------|---------|-----------|
| [Flet](https://flet.dev/) | Apache 2.0 | Framework UI cross-platform |
| [Python Standard Library](https://docs.python.org/3/library/) | PSF License | asyncio, datetime, etc. |

### Asistență din partea inteligenței artificiale

Pe parcursul dezvoltării proiectului, am folosit instrumente de inteligență artificială (ChatGPT, DeepSeek, Google Gemini, Claude/Anthropic) ca asistență tehnică în următoarele scopuri:

- **Structurarea documentației tehnice** — organizarea capitolelor, formularea explicațiilor
- **Generarea conținutului de referință** pentru analiza de piață și planul de dezvoltare
- **Asistență în generarea și revizuirea codului sursă** în Python și Flet
- **Sugestii de implementare** pentru anumite funcționalități (exerciții de respirație cu asyncio, validare input, gestionare excepții)
- **Debug și explicarea conceptelor tehnice**

Codul a fost dezvoltat colaborativ — am definit cerințele și funcționalitățile, AI-ul a oferit implementări tehnice, iar noi am revizuit, testat și integrat soluțiile.

**Important:** Ideea proiectului, designul, fluxul de utilizare, deciziile despre publicul țintă, validarea conceptului cu specialiști (consilier școlar, studentă psihologie) și prezența pe rețelele sociale aparțin în întregime echipei. Asistența AI a fost folosită ca instrument de productivitate, similar cu utilizarea unui IDE cu autocomplete sau a unei platforme precum Stack Overflow.

### Validare cu specialiști

Conceptul aplicației a fost discutat și validat în consultări informale cu:
- O consilieră școlară (anonimizată la cerere)
- O studentă la psihologie
- Membri ai comunității persoanelor cu deficiențe auditive din vecinătatea liceului nostru

## Roadmap

### Pe termen scurt (iunie–august 2026)
- Acoperire cu teste unitare (target: 70%)
- Persistența datelor utilizatorului (SQLite)
- Suport text-to-speech pentru deficiențe vizuale severe
- Refactorizare cod în module separate

### Pe termen mediu (toamnă 2026)
- 10+ exerciții noi de respirație și relaxare
- Lecții educaționale despre emoții
- Animații pentru limba semnelor românească
- Traducere în limba engleză

### Pe termen lung (2027)
- Publicare pe Google Play Store și Apple App Store
- Parteneriate cu școli speciale și ONG-uri
- Versiuni în multiple limbi (română, engleză, romă)

## Concursuri și prezență publică

- 🏆 **Technovation Girls 2026** — Proiectul a fost înscris (nu s-a calificat la etapa următoare)
- 🎯 **InfoEducația 2026** — Secțiunea Software Utilitar
- 📱 **Instagram**: [@mind_guard_](https://www.instagram.com/mind_guard_/) — comunitate în creștere pe tema sănătății mintale a copiilor

## Licență

Acest proiect este disponibil sub [Licența MIT](LICENSE).
## Surse și referințe

Documentarea proiectului s-a bazat pe următoarele surse:

### Studii și date statistice privind anxietatea la copii cu dizabilități

- Scott, S. et al. — *Mental health in children with disabilities and their families* (PMC, National Library of Medicine, 2024). Raportează o incidență de 30-50% a problemelor de sănătate mintală, inclusiv anxietatea, la copiii cu dizabilități neurodevelopmentale, comparativ cu copiii cu dezvoltare tipică.
- *Anxiety disorders in children and adolescents with intellectual disability: Prevalence and assessment* (ScienceDirect / Research in Developmental Disabilities). Studiile populaționale identifică rate de 30-40% probleme de sănătate mintală la copiii cu dizabilități intelectuale, față de 8-17% în populația tipică.
- *Factors associated with depression and anxiety in children with intellectual disabilities* (PubMed, National Library of Medicine). Prevalența problemelor de depresie și/sau anxietate raportată: 35.4%.
- *Parental Report of Signs of Anxiety and Depression in Children with and Without Disability* — meta-analiză a 44 de țări, publicată în Child Psychiatry & Human Development (Springer, 2023).

### Aplicații analizate în cadrul studiului de piață

- Calm — aplicație de meditație și relaxare (calm.com)
- Headspace — aplicație de mindfulness (headspace.com)
- Wysa — chatbot de sprijin emoțional bazat pe AI (wysa.com)
- MindShift CBT — aplicație de gestionare a anxietății (anxietycanada.com)

### Documentație tehnică

- Documentația oficială Flet — framework-ul folosit pentru interfață (flet.dev)
- Documentația oficială Python 3 (docs.python.org)
- Documentația modulului asyncio din biblioteca standard Python

### Standarde de accesibilitate

- Web Content Accessibility Guidelines (WCAG) 2.1 — World Wide Web Consortium (W3C). Standard internațional pentru accesibilitatea conținutului digital, folosit ca referință pentru modul de contrast înalt al aplicației.

### Asistență din partea inteligenței artificiale

Pe parcursul dezvoltării au fost folosite instrumente de inteligență artificială (ChatGPT, DeepSeek, Google Gemini, Claude/Anthropic) ca asistență tehnică — detaliile complete sunt descrise în secțiunea "Asistență din partea inteligenței artificiale" de mai sus.

### Resurse tehnice (biblioteci)

- Flet 0.27.6 — licență Apache 2.0
- Python 3.13 și biblioteca standard (asyncio) — licență PSF
- Git și GitHub — sistem de versionare și platformă de colaborare

## Contact

Pentru întrebări sau colaborări:
- 📷 Instagram: [@mind_guard_](https://www.instagram.com/mind_guard_/)
- 🐙 GitHub Issues: pentru raportarea bug-urilor sau sugestii

---

*"Sănătatea mintală nu cunoaște granițe — dar instrumentele de combatere a ei, da. Lucrăm să schimbăm asta."*

— Echipa MindGuard
