from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA3_256

# Wiadomość do podpisania
message = b"To jest bardzo tajny dokument, ktory autoryzuje."

# 1. Obliczamy skrót SHA3 wiadomości
hash_obj = SHA3_256.new(message)

# 2. Wczytujemy klucz prywatny (musi być wygenerowany wcześniej!)
try:
    private_key = RSA.import_key(open("private.pem").read())
except FileNotFoundError:
    print("BŁĄD: Brak pliku 'private.pem'. Uruchom najpierw generate_keys.py!")
    exit(1)

# 3. Szyfrujemy skrót kluczem prywatnym (to jest nasz podpis)
signature = pkcs1_15.new(private_key).sign(hash_obj)

# Zapisujemy wiadomość i podpis do plików
with open("message.txt", "wb") as f_out:
    f_out.write(message)
    
with open("signature.sig", "wb") as f_out:
    f_out.write(signature)

print("SUKCES: Wiadomość została podpisana cyfrowo.")
print("Zapisano 'message.txt' oraz 'signature.sig'.")