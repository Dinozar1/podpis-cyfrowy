import tkinter as tk
from tkinter import scrolledtext, messagebox, filedialog
import subprocess
import os
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA3_256

class DigitalSignatureApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Narzędzie Podpisu Cyfrowego (RSA-2048 + SHA3-256)")
        self.root.geometry("750x780")
        self.root.configure(padx=20, pady=10)

        # Ścieżki do plików
        self.target_file = None
        self.sig_file_path = None
        self.priv_key_path = "private.pem"
        self.pub_key_path = "public.pem"

        # --- SEKCJA 1: WYBÓR PLIKU I KLUCZY ---
        frame_files = tk.LabelFrame(root, text=" 📂 Konfiguracja Plików ", font=("Arial", 10, "bold"), padx=10, pady=10)
        frame_files.pack(fill=tk.X, pady=5)

        self.lbl_file = tk.Label(frame_files, text="Brak wybranego pliku", fg="red", font=("Arial", 9))
        self.lbl_file.grid(row=0, column=1, sticky="w", padx=10)
        tk.Button(frame_files, text="Wybierz plik docelowy", command=self.select_file, width=25).grid(row=0, column=0, pady=2)

        self.lbl_sig = tk.Label(frame_files, text="Brak pliku podpisu (.sig)", fg="red", font=("Arial", 9))
        self.lbl_sig.grid(row=1, column=1, sticky="w", padx=10)
        tk.Button(frame_files, text="Wskaż plik podpisu (.sig)", command=self.select_sig_file, width=25).grid(row=1, column=0, pady=2)

        self.lbl_priv = tk.Label(frame_files, text=self.priv_key_path, fg="blue", font=("Arial", 9))
        self.lbl_priv.grid(row=2, column=1, sticky="w", padx=10)
        tk.Button(frame_files, text="Wskaż klucz PRYWATNY", command=self.select_priv_key, width=25).grid(row=2, column=0, pady=2)

        self.lbl_pub = tk.Label(frame_files, text=self.pub_key_path, fg="blue", font=("Arial", 9))
        self.lbl_pub.grid(row=3, column=1, sticky="w", padx=10)
        tk.Button(frame_files, text="Wskaż klucz PUBLICZNY", command=self.select_pub_key, width=25).grid(row=3, column=0, pady=2)

        # --- SEKCJA 2: PANEL STEROWANIA ---
        frame_buttons = tk.Frame(root)
        frame_buttons.pack(pady=15)

        self.gen_btn = tk.Button(frame_buttons, text="⚙️ Generuj Klucze (TRNG)", font=("Arial", 10, "bold"), bg="#ffd700", command=self.generate_keys, width=22)
        self.gen_btn.grid(row=0, column=0, padx=5, pady=5)

        self.sign_btn = tk.Button(frame_buttons, text="✍️ Podpisz plik", font=("Arial", 10, "bold"), bg="#add8e6", command=self.sign_file, width=22)
        self.sign_btn.grid(row=0, column=1, padx=5, pady=5)

        self.verify_btn = tk.Button(frame_buttons, text="🛡️ Weryfikuj podpis", font=("Arial", 10, "bold"), bg="#90ee90", command=self.verify_file, width=22)
        self.verify_btn.grid(row=1, column=0, columnspan=2, padx=5, pady=5)

        # --- SEKCJA 3: LOGI ---
        tk.Label(root, text="Terminal Kryptograficzny (Logi systemowe):", font=("Arial", 11, "bold")).pack(anchor="w", pady=(10, 0))
        self.log_area = scrolledtext.ScrolledText(root, height=18, width=85, font=("Courier", 9), bg="#1e1e1e", fg="#00ff00")
        self.log_area.pack()
        self.log_area.insert(tk.END, "System gotowy. Wybierz plik z dysku, aby rozpocząć.\n")
        self.log_area.config(state=tk.DISABLED)

    def log(self, text):
        self.log_area.config(state=tk.NORMAL)
        self.log_area.insert(tk.END, text + "\n")
        self.log_area.see(tk.END)
        self.log_area.config(state=tk.DISABLED)

    def clear_logs(self):
        self.log_area.config(state=tk.NORMAL)
        self.log_area.delete("1.0", tk.END)
        self.log_area.config(state=tk.DISABLED)

    # --- FUNKCJE WYBORU PLIKÓW ---
    def select_file(self):
        filepath = filedialog.askopenfilename(title="Wybierz plik do podpisania/weryfikacji")
        if filepath:
            self.target_file = filepath
            self.lbl_file.config(text=os.path.basename(filepath), fg="black")
            self.log(f"Załadowano plik docelowy: {filepath}")

    def select_sig_file(self):
        filepath = filedialog.askopenfilename(title="Wybierz plik podpisu cyfrowego (.sig)")
        if filepath:
            self.sig_file_path = filepath
            self.lbl_sig.config(text=os.path.basename(filepath), fg="black")
            self.log(f"Załadowano plik podpisu: {filepath}")

    def select_priv_key(self):
        filepath = filedialog.askopenfilename(title="Wybierz klucz prywatny (.pem)")
        if filepath:
            self.priv_key_path = filepath
            self.lbl_priv.config(text=os.path.basename(filepath))

    def select_pub_key(self):
        filepath = filedialog.askopenfilename(title="Wybierz klucz publiczny (.pem)")
        if filepath:
            self.pub_key_path = filepath
            self.lbl_pub.config(text=os.path.basename(filepath))

    # --- FUNKCJE KRYPTOGRAFICZNE ---
    def generate_keys(self):
        self.clear_logs()
        self.log("=== URUCHAMIANIE TRNG W C ===")
        try:
            result = subprocess.run(["python3", "generate_keys.py"], capture_output=True, text=True)
            self.log(result.stdout)
            if result.returncode != 0:
                self.log(f"BŁĄD: {result.stderr}")
        except Exception as e:
            self.log(f"Błąd uruchamiania skryptu: {e}")

    def sign_file(self):
        self.clear_logs()
        if not self.target_file or not os.path.exists(self.target_file):
            messagebox.showwarning("Błąd", "Najpierw wybierz plik z dysku!")
            return

        self.log(f"=== PODPISYWANIE PLIKU: {os.path.basename(self.target_file)} ===")
        try:
            with open(self.target_file, "rb") as f:
                file_data = f.read()
            
            self.log("[KROK 1] Obliczanie skrótu SHA3-256 z zawartości pliku...")
            hash_obj = SHA3_256.new(file_data)
            self.log(f"Skrót (HEX): {hash_obj.hexdigest()}\n")

            if not os.path.exists(self.priv_key_path):
                self.log(f"BŁĄD: Brak pliku klucza ({self.priv_key_path}).")
                messagebox.showerror("Błąd", "Brak klucza prywatnego!")
                return

            self.log(f"[KROK 2] Inicjalizacja algorytmu RSA z użyciem klucza prywatnego...")
            key = RSA.import_key(open(self.priv_key_path).read())
            signature = pkcs1_15.new(key).sign(hash_obj)

            # Zapisanie pliku .sig na dysku
            sig_filename = self.target_file + ".sig"
            with open(sig_filename, "wb") as f_out:
                f_out.write(signature)

            # --- NOWOŚĆ: Automatyczne podpięcie nowo wygenerowanego podpisu do GUI ---
            self.sig_file_path = sig_filename
            self.lbl_sig.config(text=os.path.basename(sig_filename), fg="black")

            self.log("=== SUKCES ===")
            self.log(f"Wygenerowano plik podpisu: {os.path.basename(sig_filename)}")
            messagebox.showinfo("Sukces", f"Plik został pomyślnie podpisany!\nUtworzono: {os.path.basename(sig_filename)}")

        except Exception as e:
            self.log(f"WYSTĄPIŁ BŁĄD: {str(e)}")
            messagebox.showerror("Błąd", f"Wystąpił błąd podczas podpisywania:\n{str(e)}")

    def verify_file(self):
        self.clear_logs()
        if not self.target_file:
            messagebox.showwarning("Błąd", "Wybierz plik docelowy do sprawdzenia!")
            return
        
        if not self.sig_file_path:
            messagebox.showwarning("Błąd", "Wskaż plik z podpisem (.sig), który chcesz zweryfikować!")
            return

        self.log(f"=== WERYFIKACJA PLIKU: {os.path.basename(self.target_file)} ===")

        try:
            if not os.path.exists(self.sig_file_path):
                self.log(f"BŁĄD: Nie znaleziono wskazanego pliku podpisu na dysku.")
                messagebox.showerror("Brak pliku", "Wskazany plik podpisu (.sig) nie istnieje.")
                return
            if not os.path.exists(self.pub_key_path):
                self.log("BŁĄD: Brak klucza publicznego!")
                messagebox.showerror("Brak klucza", "Brak klucza publicznego.")
                return

            file_data = open(self.target_file, "rb").read()
            signature = open(self.sig_file_path, "rb").read()
            public_key = RSA.import_key(open(self.pub_key_path).read())

            self.log(f"[KROK 1] Wczytano plik docelowy oraz sygnaturę: {os.path.basename(self.sig_file_path)}")
            hash_obj = SHA3_256.new(file_data)
            self.log(f"[KROK 2] Obliczono skrót pliku: {hash_obj.hexdigest()}")
            
            self.log("[KROK 3] Kryptograficzna weryfikacja autentyczności (RSA PKCS#1 v1.5)...")
            pkcs1_15.new(public_key).verify(hash_obj, signature)

            self.log("\n=== SUKCES: WYNIK POZYTYWNY ===")
            self.log("Podpis jest zgodny. Plik pochodzi od prawowitego nadawcy.")
            messagebox.showinfo("SUKCES", "Weryfikacja udana!\nPodpis jest autentyczny.")

        except (ValueError, TypeError):
            self.log("\n[!] BŁĄD INTEGRALNOŚCI [!]")
            self.log("Skróty kryptograficzne nie zgadzają się.")
            self.log("Możliwa przyczyna: Plik bazowy został podmieniony lub wybrano zły plik .sig.")
            messagebox.showwarning("Błąd Integralności", "PODPIS NIEPRAWIDŁOWY!\nPlik docelowy lub sygnatura nie pasują.")
        except Exception as e:
            self.log(f"WYSTĄPIŁ BŁĄD: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = DigitalSignatureApp(root)
    root.mainloop()