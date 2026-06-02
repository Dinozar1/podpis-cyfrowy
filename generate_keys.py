import os
import subprocess
from Crypto.PublicKey import RSA

print("=== START: Odświeżanie puli entropii ===")

# 1. Automatyczne odpalenie Twojego programu w C
try:
    print("Uruchamianie sprzętowego TRNG (jitter_rng)...")
    subprocess.run(["./jitter_rng"], check=True)
    print("Świeży plik data.bin został pomyślnie wygenerowany!")
except Exception as e:
    print("BŁĄD: Nie udało się uruchomić pliku wykonywalnego './jitter_rng'.")
    print(f"Szczegóły: {e}")
    exit(1)

# 2. Czytanie świeżej entropii
print("\n=== GENEROWANIE KLUCZY RSA ===")
try:
    trng_file = open("data.bin", "rb")
except FileNotFoundError:
    print("BŁĄD: Brak pliku data.bin!")
    exit(1)

def trng_randfunc(n):
    data = trng_file.read(n)
    if len(data) < n:
        raise ValueError("Zabrakło danych w pliku! Zwiększ bytes_to_generate w C.")
    return data

# Generowanie kluczy w oparciu o świeże TRNG
print("Kalkulowanie parametrów klucza RSA-2048...")
key = RSA.generate(2048, randfunc=trng_randfunc)

# Zapis kluczy
with open("private.pem", "wb") as f_out:
    f_out.write(key.export_key())

with open("public.pem", "wb") as f_out:
    f_out.write(key.publickey().export_key())

trng_file.close()

# 3. Zacieranie śladów (Dobra praktyka bezpieczeństwa)
os.remove("data.bin")

print("SUKCES: Zapisano świeże pliki private.pem oraz public.pem.")
print("Pula entropii (data.bin) została bezpiecznie wyczyszczona z dysku.")