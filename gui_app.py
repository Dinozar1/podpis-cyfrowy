import tkinter as tk
from tkinter import scrolledtext, messagebox
import subprocess
import os
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA3_256

class DigitalSignatureApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Aplikacja Podpisu Cyfrowego (RSA + SHA3) - Command Center")
        self.root.geometry("700x700")
        self.root.configure(padx=20, pady=10)

        # 1. SEKCJA WIADOMOŚCI
        self.label_msg = tk.Label(root, text="Wpisz tajną wiadomość do podpisania:", font=("Arial", 11, "bold"))
        self.label_msg.pack(anchor="w")

        self.text_area = tk.Text(root, height=5, width=80, font=("Arial", 10))
        self.text_area.pack(pady=(5, 10))
        self.text_area.insert(tk.END, "Witaj, to jest tajny dokument autoryzowany moim podpisem.")

        # 2. SEKCJA PRZYCISKÓW (Panel Sterowania)
        self.button_frame = tk.Frame(root)
        self.button_frame.pack(pady=5)

        # Generowanie kluczy (korzysta z Twojego zewnętrznego skryptu!)
        self.gen_btn = tk.Button(self.button_frame, text="⚙️ Generuj Klucze (TRNG)", font=("Arial", 10, "bold"), bg="#ffd700", command=self.generate_keys_via_script, width=22)
        self.gen_btn.grid(row=0, column=0, padx=5, pady=5)

        # Podpisywanie
        self.sign_btn = tk.Button(self.button_frame, text="✍️ Podpisz wiadomość", font=("Arial", 10, "bold"), bg="#add8e6", command=self.sign_message, width=22)
        self.sign_btn.grid(row=0, column=1, padx=5, pady=5)

        # Weryfikacja
        self.verify_btn = tk.Button(self.button_frame, text="🛡️ Weryfikuj podpis", font=("Arial", 10, "bold"), bg="#90ee90", command=self.verify_signature, width=22)
        self.verify_btn.grid(row=1, column=0, padx=5, pady=5)

        # Symulacja ataku
        self.hack_btn = tk.Button(self.button_frame, text="😈 Symuluj Atak (Zmień plik)", font=("Arial", 10, "bold"), bg="#ff9999", command=self.simulate_attack, width=22)
        self.hack_btn.grid(row=1, column=1, padx=5, pady=5)

        # 3. SEKCJA INSPEKCJI KRYPTOGRAFICZNEJ
        self.label_log = tk.Label(root, text="Inspekcja Kryptograficzna (Podgląd operacji):", font=("Arial", 11, "bold"))
        self.label_log.pack(anchor="w", pady=(15, 5))

        self.log_area = scrolledtext.ScrolledText(root, height=18, width=85, font=("Courier", 9), bg="#1e1e1e", fg="#00ff00") # Styl "hakerski" terminala
        self.log_area.pack()
        self.log_area.insert(tk.END, "Czekam na akcję...\n")
        self.log_area.config(state=tk.DISABLED)

        # Pasek statusu
        self.status_label = tk.Label(root, text="Status: Gotowy", fg="gray", font=("Arial", 10, "italic"))
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X, pady=10)

    def log(self, text):
        self.log_area.config(state=tk.NORMAL)
        self.log_area.insert(tk.END, text + "\n")
        self.log_area.see(tk.END)
        self.log_area.config(state=tk.DISABLED)

    def clear_logs(self):
        self.log_area.config(state=tk.NORMAL)
        self.log_area.delete("1.0", tk.END)
        self.log_area.config(state=tk.DISABLED)

    # --- FUNKCJE PREZENTACYJNE ---

    def generate_keys_via_script(self):
        """Uruchamia zewnętrzny skrypt generate_keys.py bez dublowania kodu!"""
        self.clear_logs()
        self.log("=== URUCHAMIANIE SPRZĘTOWEGO TRNG (C) ORAZ SKRYPTU PYTHON ===")
        self.log("Wywoływanie: python3 generate_keys.py ...\n")
        self.status_label.config(text="Status: Generowanie entropii w toku...", fg="blue")
        self.root.update() # Odśwież okno

        try:
            # Uruchamiamy zewnętrzny skrypt i przechwytujemy jego wyjście
            result = subprocess.run(["python3", "generate_keys.py"], capture_output=True, text=True)
            
            # Wypisujemy w logach to, co skrypt wypluł do konsoli
            self.log(result.stdout)
            
            if result.returncode == 0:
                self.status_label.config(text="Status: Klucze TRNG gotowe!", fg="green")
            else:
                self.log(f"BŁĄD: {result.stderr}")
                self.status_label.config(text="Status: Błąd podczas generowania kluczy.", fg="red")
        except Exception as e:
            self.log(f"BŁĄD KRYTYCZNY: {e}")

    def simulate_attack(self):
        """Dodaje ukryty tekst do pliku z wiadomością, łamiąc integralność"""
        self.clear_logs()
        self.log("=== SYMULACJA ATAKU HAKERSKIEGO (Man-in-the-Middle) ===")
        if not os.path.exists("message.txt"):
            self.log("BŁĄD: Brak pliku message.txt. Najpierw wygeneruj klucze i podpisz wiadomość!")
            return

        try:
            # Dopisujemy wrogi kod na sam koniec pliku (dodajemy spację i tekst)
            with open("message.txt", "ab") as f_out:
                f_out.write(b" [ZMODYFIKOWANE PRZEZ HAKERA]")
            
            self.log("UWAGA: Plik 'message.txt' na dysku został potajemnie zmodyfikowany.")
            self.log("Osoba trzecia dopisała tekst do przechwyconej wiadomości.")
            self.log("\n-> Teraz kliknij 'Weryfikuj podpis', aby sprawdzić, czy system to wykryje!")
            self.status_label.config(text="Status: Plik message.txt skompromitowany!", fg="red")
            messagebox.showwarning("Atak udany", "Zmodyfikowano plik na dysku. Wykonaj weryfikację.")
        except Exception as e:
            self.log(f"Błąd modyfikacji: {e}")

    def sign_message(self):
        self.clear_logs()
        self.log("=== ROZPOCZĘCIE PROCESU PODPISYWANIA ===")
        try:
            message = self.text_area.get("1.0", tk.END).strip().encode('utf-8')
            if not message:
                messagebox.showwarning("Błąd", "Wiadomość nie może być pusta!")
                return

            if not os.path.exists("private.pem"):
                self.log("BŁĄD: Brak klucza prywatnego! Kliknij 'Generuj Klucze'.")
                return

            self.log("[KROK 1] Obliczanie skrótu SHA3-256 wiadomości...")
            hash_obj = SHA3_256.new(message)
            self.log(f"Skrót (HEX): {hash_obj.hexdigest()}\n")

            self.log("[KROK 2] Wczytywanie klucza prywatnego i szyfrowanie skrótu (PKCS#1 v1.5)...")
            private_key = RSA.import_key(open("private.pem").read())
            signature = pkcs1_15.new(private_key).sign(hash_obj)
            
            sig_hex = signature.hex().upper()
            formatted_sig = "\n".join([sig_hex[i:i+64] for i in range(0, len(sig_hex), 64)])
            self.log(f"Wygenerowany podpis cyfrowy (HEX):\n{formatted_sig}\n")

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

            message = open("message.txt", "rb").read()
            signature = open("signature.sig", "rb").read()
            public_key_raw = open("public.pem").read()
            public_key = RSA.import_key(public_key_raw)

            self.log("[KROK 1] Wczytano klucz publiczny nadawcy.")
            self.log("[KROK 2] Obliczanie skrótu SHA3-256 z otrzymanej wiadomości na dysku...")
            hash_obj = SHA3_256.new(message)
            self.log(f"Obliczony skrót (HEX): {hash_obj.hexdigest()}\n")

            self.log("[KROK 3] Sprawdzanie zgodności podpisu z obliczonym skrótem...")
            pkcs1_15.new(public_key).verify(hash_obj, signature)

            self.log("=== SUKCES: PODPIS AUTENTYCZNY ===")
            self.status_label.config(text="Status: Weryfikacja udana! Podpis prawidłowy.", fg="green")
            messagebox.showinfo("SUKCES", "Podpis jest AUTENTYCZNY.\nWiadomość nie została sfałszowana.")

        except (ValueError, TypeError):
            self.log("\n!!! BŁĄD KRYTYCZNY !!!")
            self.log("Skrót wyliczony z pliku 'message.txt' NIE ZGADZA SIĘ ze skrótem w podpisie.")
            self.log("Oznacza to, że zawartość pliku została potajemnie zmodyfikowana!")
            self.log("=== WERYFIKACJA OBLANA: PLIK SFAŁSZOWANY ===")
            self.status_label.config(text="Status: WERYFIKACJA OBLANA! Plik zmodyfikowany.", fg="red")
            messagebox.showwarning("BŁĄD WERYFIKACJI", "Podpis jest NIEPRAWIDŁOWY!\nWiadomość została sfałszowana.")
        except Exception as e:
            self.log(f"WYSTĄPIŁ BŁĄD: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = DigitalSignatureApp(root)
    root.mainloop()