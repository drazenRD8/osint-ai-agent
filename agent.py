import google.generativeai as genai
import requests
from PIL import Image
from PIL.ExifTags import TAGS

# === PODESAVANJA ===
API_KEY = "TVOJ_GEMINI_API_KEY_OVDE"

genai.configure(api_key=API_KEY)

# === MODEL ===
model = genai.GenerativeModel("gemini-3.6-flash")


# === FUNKCIJE ZA ALATE ===
def ip_lookup(ip):
    """Vraća lokaciju IP adrese."""
    try:
        r = requests.get(f"https://ipapi.co/{ip}/json/", timeout=10)
        data = r.json()
        return f"{data.get('city', '?')}, {data.get('country_name', '?')} ({data.get('org', '?')})"
    except Exception as e:
        return f"Greška: {e}"


def exif_lookup(image_path):
    """Vraća EXIF metapodatke."""
    try:
        with Image.open(image_path) as img:
            exif = img.getexif()
            if not exif:
                return "Nema EXIF podataka."
            return "\n".join(
                f"{TAGS.get(tag_id, tag_id)}: {value}"
                for tag_id, value in exif.items()
                if TAGS.get(tag_id) != "GPSInfo"
            )
    except Exception as e:
        return f"Greška: {e}"


# === AI AGENT ===
def ask_agent(user_input):
    """AI agent koji odgovara na pitanja."""
    prompt = f"""
    Ti si OSINT AI agent. Odgovaraš kratko i jasno na srpskom.

    Korisnik pita: {user_input}

    Ako korisnik traži IP lokaciju, reci mu da koristi /ip komandu.
    Ako korisnik traži EXIF, reci mu da koristi /exif komandu.
    Ako korisnik pita nešto drugo, odgovori kratko.

    Odgovor:
    """

    response = model.generate_content(prompt)
    return response.text


# === GLAVNI DEO ===
if __name__ == "__main__":
    print("=" * 60)
    print("🤖 OSINT AI AGENT")
    print("=" * 60)
    print("Komande:")
    print("  /ip <adresa>      - IP lokacija")
    print("  /exif <slika>     - EXIF metapodaci")
    print("  /ask <pitanje>    - Pitaj AI agenta")
    print("  /exit             - Izlaz")
    print("=" * 60)

    while True:
        try:
            user_input = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n👋 Ćao!")
            break

        if not user_input:
            continue

        if user_input.startswith("/exit"):
            print("👋 Ćao!")
            break

        elif user_input.startswith("/ip "):
            ip = user_input[4:].strip()
            print(f"🌍 {ip_lookup(ip)}")

        elif user_input.startswith("/exif "):
            path = user_input[6:].strip()
            print(f"📷 {exif_lookup(path)}")

        elif user_input.startswith("/ask "):
            question = user_input[5:].strip()
            print(f"🤖 {ask_agent(question)}")

        else:
            print(f"🤖 {ask_agent(user_input)}")