from Crypto.PublicKey import RSA

print("Rozpoczynam generowanie kluczy RSA-2048...")

# Próbujemy otworzyć Twój plik z entropią
try:
    trng_file = open("data.bin", "rb")
except FileNotFoundError:
    print("BŁĄD: Nie znaleziono pliku 'data.bin'! Upewnij się, że jest w tym samym folderze co ten skrypt.")
    exit(1)

# Nasza autorska funkcja pobierająca losowość z TRNG zamiast z systemu
def trng_randfunc(n):
    data = trng_file.read(n)
    if len(data) < n:
        raise ValueError("Zabrakło danych w pliku data.bin! Wygeneruj większy plik.")
    return data

print("Generowanie kluczy w oparciu o sprzętowe TRNG (data.bin)...")

# Generujemy klucze
key = RSA.generate(2048, randfunc=trng_randfunc)

# Zapisujemy klucz prywatny
with open("private.pem", "wb") as f_out:
    f_out.write(key.export_key())

# Zapisujemy klucz publiczny
with open("public.pem", "wb") as f_out:
    f_out.write(key.publickey().export_key())

trng_file.close()
print("Sukces! Zapisano pliki: private.pem oraz public.pem")