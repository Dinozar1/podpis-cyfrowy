import tkinter as tk
from tkinter import scrolledtext, messagebox
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA3_256
import os

class DigitalSignatureApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Aplikacja Podpisu Cyfrowego (RSA + SHA3) - Wersja z Inspekcją")
        self.root.geometry("650x650") # Większe okno na podgląd danych
        self.root.configure(padx=20, pady=10)

        # 1. SEKCJA WIADOMOŚCI
        self.label_msg = tk.Label(root, text="Wpisz tajną wiadomość do podpisania:", font=("Arial", 11, "bold"))
        self.label_msg.pack(anchor="w")

        self.text_area = tk.Text(root, height=5, width=75, font=("Arial", 10))
        self.text_area.pack(pady=(5, 10))
        self.text_area.insert(tk.END, "Witaj, to jest tajny dokument autoryzowany moim podpisem.")

        # 2. SEKCJA PRZYCISKÓW
        self.button_frame = tk.Frame(root)
        self.button_frame.pack(pady=5)

        self.sign_btn = tk.Button(self.button_frame, text="✍️ Podpisz wiadomość", font=("Arial", 10, "bold"), bg="#add8e6", command=self.sign_message, width=20)
        self.sign_btn.grid(row=0, column=0, padx=10)

        self.verify_btn = tk.Button(self.button_frame, text="🛡️ Weryfikuj podpis", font=("Arial", 10, "bold"), bg="#90ee90", command=self.verify_signature, width=20)
        self.verify_btn.grid(row=0, column=1, padx=10)

        # 3. SEKCJA INSPEKCJI KRYPTOGRAFICZNEJ (NOWOŚĆ)
        self.label_log = tk.Label(root, text="Inspekcja Kryptograficzna (Podgląd danych):", font=("Arial", 11, "bold"))
        self.label_log.pack(anchor="w", pady=(15, 5))

        # Używamy ScrolledText, żeby można było przewijać długie ciągi znaków (jak klucze RSA)
        self.log_area = scrolledtext.ScrolledText(root, height=15, width=75, font=("Courier", 9), bg="#f4f4f4")
        self.log_area.pack()
        self.log_area.insert(tk.END, "Czekam na akcję...\n")
        self.log_area.config(state=tk.DISABLED) # Blokujemy edycję logów

        # Pasek statusu
        self.status_label = tk.Label(root, text="Status: Gotowy", fg="gray", font=("Arial", 10, "italic"))
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X, pady=10)

    def log(self, text):
        """Pomocnicza funkcja do dopisywania tekstu do okna logów"""
        self.log_area.config(state=tk.NORMAL)
        self.log_area.insert(tk.END, text + "\n")
        self.log_area.see(tk.END) # Przewiń na sam dół
        self.log_area.config(state=tk.DISABLED)

    def clear_logs(self):
        self.log_area.config(state=tk.NORMAL)
        self.log_area.delete("1.0", tk.END)
        self.log_area.config(state=tk.DISABLED)

    def sign_message(self):
        self.clear_logs()
        self.log("=== ROZPOCZĘCIE PROCESU PODPISYWANIA ===")
        try:
            message = self.text_area.get("1.0", tk.END).strip().encode('utf-8')
            if not message:
                messagebox.showwarning("Błąd", "Wiadomość nie może być pusta!")
                return

            if not os.path.exists("private.pem"):
                self.log("BŁĄD: Brak klucza prywatnego!")
                return

            # Krok 1: Hashing
            self.log("[KROK 1] Obliczanie skrótu SHA3-256 wiadomości...")
            hash_obj = SHA3_256.new(message)
            self.log(f"Skrót (HEX): {hash_obj.hexdigest()}\n")

            # Krok 2: Podpisywanie
            self.log("[KROK 2] Wczytywanie klucza prywatnego i szyfrowanie skrótu (PKCS#1 v1.5)...")
            private_key = RSA.import_key(open("private.pem").read())
            signature = pkcs1_15.new(private_key).sign(hash_obj)
            
            # Pokazujemy początek i koniec surowego podpisu w formacie szesnastkowym
            sig_hex = signature.hex().upper()
            formatted_sig = "\n".join([sig_hex[i:i+64] for i in range(0, len(sig_hex), 64)])
            self.log(f"Wygenerowany podpis cyfrowy (HEX):\n{formatted_sig}\n")

            # Zapisujemy do plików
            with open("message.txt", "wb") as f_out:
                f_out.write(message)
            with open("signature.sig", "wb") as f_out:
                f_out.write(signature)

            self.log("=== SUKCES: ZAPISANO message.txt ORAZ signature.sig ===")
            self.status_label.config(text="Status: Wiadomość podpisana pomyślnie!", fg="green")

        except Exception as e:
            self.log(f"WYSTĄPIŁ BŁĄD: {str(e)}")
            self.status_label.config(text="Status: Błąd podpisywania", fg="red")

    def verify_signature(self):
        self.clear_logs()
        self.log("=== ROZPOCZĘCIE PROCESU WERYFIKACJI ===")
        try:
            if not os.path.exists("message.txt") or not os.path.exists("signature.sig"):
                self.log("BŁĄD: Brak plików wiadomości lub podpisu!")
                return
            if not os.path.exists("public.pem"):
                self.log("BŁĄD: Brak klucza publicznego!")
                return

            # Wczytywanie
            message = open("message.txt", "rb").read()
            signature = open("signature.sig", "rb").read()
            public_key_raw = open("public.pem").read()
            public_key = RSA.import_key(public_key_raw)

            self.log("[KROK 1] Wczytano klucz publiczny nadawcy:")
            # Wyświetlamy sam nagłówek i początek klucza, żeby nie zaśmiecać widoku
            self.log(public_key_raw[:120] + "...\n")

            # Obliczanie skrótu z pliku
            self.log("[KROK 2] Obliczanie skrótu SHA3-256 z otrzymanej wiadomości...")
            hash_obj = SHA3_256.new(message)
            self.log(f"Obliczony skrót (HEX): {hash_obj.hexdigest()}\n")

            self.log("[KROK 3] Sprawdzanie zgodności podpisu z obliczonym skrótem...")
            pkcs1_15.new(public_key).verify(hash_obj, signature)

            self.log("=== SUKCES: PODPIS AUTENTYCZNY ===")
            self.status_label.config(text="Status: Weryfikacja udana! Podpis prawidłowy.", fg="green")
            messagebox.showinfo("SUKCES", "Podpis jest AUTENTYCZNY.\nWiadomość nie została sfałszowana.")

        except (ValueError, TypeError):
            self.log("\n!!! BŁĄD KRYTYCZNY !!!")
            self.log("Skrót wyliczony z wiadomości nie zgadza się ze skrótem zaszyfrowanym w podpisie.")
            self.log("=== WERYFIKACJA OBLANA: PLIK SFAŁSZOWANY ===")
            self.status_label.config(text="Status: WERYFIKACJA OBLANA! Ktoś zmienił plik.", fg="red")
            messagebox.showwarning("BŁĄD WERYFIKACJI", "Podpis jest NIEPRAWIDŁOWY!\nWiadomość mogła zostać sfałszowana.")
        except Exception as e:
            self.log(f"WYSTĄPIŁ BŁĄD: {str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = DigitalSignatureApp(root)
    root.mainloop()