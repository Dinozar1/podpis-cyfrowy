from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA3_256

try:
    # Wczytujemy wiadomość, podpis i klucz publiczny
    message = open("message.txt", "rb").read()
    signature = open("signature.sig", "rb").read()
    public_key = RSA.import_key(open("public.pem").read())
except FileNotFoundError as e:
    print(f"BŁĄD: Brakuje pliku! Szczegóły: {e}")
    exit(1)

# Obliczamy skrót z otrzymanej wiadomości
hash_obj = SHA3_256.new(message)

# Sprawdzamy, czy podpis pasuje do skrótu
try:
    pkcs1_15.new(public_key).verify(hash_obj, signature)
    print("--------------------------------------------------")
    print("SUKCES: Podpis jest autentyczny!")
    print("Wiadomość pochodzi od nadawcy i nie została zmieniona.")
    print("--------------------------------------------------")
except (ValueError, TypeError):
    print("--------------------------------------------------")
    print("BŁĄD KRYTYCZNY: Podpis jest nieprawidłowy!")
    print("Wiadomość mogła zostać sfałszowana.")
    print("--------------------------------------------------")