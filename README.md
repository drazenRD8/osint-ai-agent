# osint-ai-agent
Python AI agent that combines Gemini with OSINT tools (IP lookup, EXIF, etc.)
# OSINT AI Agent

Python AI agent koji kombinuje **Gemini** model sa OSINT alatima za brzu analizu.

**Verzija:** v1.0.0

## Namena

Agent prima komande na srpskom jeziku i:
- Odgovara na pitanja pomoću Gemini modela.
- Izvršava IP lookup (`/ip`).
- Čita EXIF metapodatke iz slika (`/exif`).
- Može se proširiti novim alatima.

## Instalacija

pip install -r requirements.txt

## Pokretanje

python agent.py

## Komande

| Komanda | Opis |
|---------|------|
| `/ip <adresa>` | Vraća lokaciju IP adrese |
| `/exif <slika>` | Vraća EXIF metapodatke |
| `/ask <pitanje>` | Pita AI agenta |
| `/exit` | Izlaz |

## Primer
ip 8.8.8.8
🌍 Mountain View, United States (Google LLC)

/ask Šta je OSINT?
🤖 OSINT je prikupljanje informacija iz javnih izvora...

```

## Napomena

Potreban je **Gemini API ključ** (besplatan):  
https://aistudio.google.com/app/apikey