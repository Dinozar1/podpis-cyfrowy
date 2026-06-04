# Jitter RNG & RSA Signatures

Projekt łączący język C i Python, demonstrujący bezpieczne generowanie kluczy RSA z wykorzystaniem własnego, sprzętowego generatora liczb losowych (TRNG), a także tworzenie i weryfikację podpisów cyfrowych.

Projekt opiera się na analizie fluktuacji czasu wykonywania instrukcji procesora (*CPU jitter*) przy użyciu funkcji `__rdtsc()`, połączonej z generatorem XORSHIFT oraz post-processingiem AES-256 CTR.

---

## Wymagania

Do skompilowania i uruchomienia projektu potrzebujesz:
* Kompilatora **GCC**
* Bibliotek deweloperskich **OpenSSL** (wymagane do AES-CTR w C)
* **Python 3.x**
* Biblioteki **PyCryptodome** dla Pythona

Aby zainstalować zależności w Pythonie, wykonaj:
```bash
pip install pycryptodome