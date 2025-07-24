import customtkinter as ctk
import time
import difflib
import random
import os
import sys
from datetime import datetime

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class KeyTesterApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("KeyTester")
        self.geometry("600x500")
        self.resizable(False, False)

        self.appearance_mode = "dark"
        self.border_color = "white"

        self.samples = {
            "Kolay": [
                "Merhaba dünya",
                "Bu bir testtir",
                "Python harikadır"
            ],
            "Orta": [
                "Python programlama dili çok yönlüdür.",
                "Bugün hava çok güzel ve güneşli.",
                "Bilgisayarlar veri işler ve sonuç üretir."
            ],
            "Zor": [
                "Yapay zeka, insan benzeri görevleri gerçekleştiren sistemlerdir.",
                "Veri analizi, büyük veri kümelerinden anlam çıkarmayı sağlar.",
                "Python’da threading ve multiprocessing kavramları farklıdır."
            ]
        }

        self.difficulty = "Orta"
        self.sample_text = random.choice(self.samples[self.difficulty])
        self.start_time = None
        self.target_wpm = 40  # Varsayılan hedef

        # Üst çerçeve (seviye ve tema butonları)
        self.top_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.top_frame.pack(side="top", fill="x", padx=10, pady=(5, 0))

        self.level_menu = ctk.CTkOptionMenu(self.top_frame, values=["Kolay", "Orta", "Zor"], command=self.change_difficulty)
        self.level_menu.set(self.difficulty)
        self.level_menu.pack(side="left")

        self.theme_button = ctk.CTkButton(self.top_frame, text="🌙 Tema", command=self.toggle_theme, width=70)
        self.theme_button.pack(side="right")

        # Hedef WPM giriş kutusu ve etiket
        self.target_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.target_frame.place(relx=0.01, rely=0.91)

        self.target_label = ctk.CTkLabel(self.target_frame, text="🎯 Hedef WPM:", font=("Ubuntu", 12))
        self.target_label.pack(side="left")

        self.target_entry = ctk.CTkEntry(self.target_frame, width=50, font=("Ubuntu", 12))
        self.target_entry.insert(0, str(self.target_wpm))
        self.target_entry.pack(side="left")

        # Metin ve giriş
        self.label = ctk.CTkLabel(self, text=self.sample_text, wraplength=550, font=("Ubuntu", 16))
        self.label.pack(pady=(10, 10))

        self.entry = ctk.CTkEntry(self, width=550, font=("Ubuntu", 15), border_color=self.border_color, border_width=1)
        self.entry.pack()
        self.entry.bind("<Key>", self.start_timer)

        self.result_label = ctk.CTkLabel(self, text="", font=("Ubuntu", 14))
        self.result_label.pack(pady=(10, 5))

        self.goal_label = ctk.CTkLabel(self, text="", font=("Ubuntu", 14))
        self.goal_label.pack(pady=(0, 5))

        self.output_box = ctk.CTkTextbox(self, height=80, width=550, font=("Ubuntu", 14), state="disabled", border_color=self.border_color, border_width=1)
        self.output_box.pack(pady=(0, 5))

        self.retry_button = ctk.CTkButton(self, text="Yeniden Dene", command=self.reset)
        self.retry_button.pack()
        self.retry_button.configure(state="disabled")

        # Önceki sonuçlar kutusu
        self.history_label = ctk.CTkLabel(self, text="\U0001F4CA Önceki Sonuçlar", font=("Ubuntu", 13, "bold"))
        self.history_label.pack(pady=(10, 0))

        self.history_box = ctk.CTkTextbox(self, height=100, width=550, font=("Ubuntu", 12), state="disabled", border_color=self.border_color, border_width=1)
        self.history_box.pack(pady=(0, 10))

    def change_difficulty(self, value):
        self.difficulty = value
        self.sample_text = random.choice(self.samples[value])
        self.label.configure(text=self.sample_text)
        self.reset()

    def start_timer(self, event):
        if not self.start_time:
            self.start_time = time.time()
            self.entry.bind("<Return>", self.calculate_wpm)

    def calculate_wpm(self, event):
        if self.entry.cget("state") == "disabled":
            return

        if self.target_entry.get().isdigit():
            self.target_wpm = int(self.target_entry.get())

        end_time = time.time()
        elapsed = end_time - self.start_time
        typed_text = self.entry.get()
        words = len(typed_text.split())
        wpm = (words / elapsed) * 60
        wps = elapsed / max(words, 1)
        accuracy = self.calculate_accuracy(typed_text)

        hedef_basari = wpm >= self.target_wpm
        durum_yazi = "✅ Hedefe Ulaşıldı" if hedef_basari else "❌ Hedefe Ulaşılamadı"
        renk = "green" if hedef_basari else "red"
        self.goal_label.configure(text=durum_yazi, text_color=renk)

        self.result_label.configure(
            text=f"WPM: {wpm:.2f} | WPS: {wps:.2f} sn | Doğruluk: {accuracy:.2f}% | Süre: {elapsed:.2f} sn | {durum_yazi}"
        )

        self.show_colored_text(typed_text)
        self.entry.configure(state="disabled")
        self.retry_button.configure(state="normal")

        # Geçmişe ekle
        now = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
        self.history_box.configure(state="normal")
        self.history_box.insert(ctk.END, f"[{now}] WPM: {wpm:.2f} | Doğruluk: {accuracy:.2f}% | {durum_yazi}\n")
        self.history_box.tag_add("last_entry", "end-2l", "end-1l")
        self.history_box.tag_config("last_entry", foreground=renk)
        self.history_box.configure(state="disabled")

    def calculate_accuracy(self, typed):
        matcher = difflib.SequenceMatcher(None, self.sample_text, typed)
        return matcher.ratio() * 100

    def show_colored_text(self, typed):
        self.output_box.configure(state="normal")
        self.output_box.delete("1.0", ctk.END)

        for i, char in enumerate(typed):
            correct_char = self.sample_text[i] if i < len(self.sample_text) else ""
            tag = "correct" if char == correct_char else "incorrect"
            self.output_box.insert(ctk.END, char, tag)

        self.output_box.tag_config("correct", foreground="green")
        self.output_box.tag_config("incorrect", foreground="red")
        self.output_box.configure(state="disabled")

    def reset(self):
        self.sample_text = random.choice(self.samples[self.difficulty])
        self.label.configure(text=self.sample_text)
        self.entry.configure(state="normal")
        self.entry.delete(0, ctk.END)
        self.result_label.configure(text="")
        self.goal_label.configure(text="")
        self.output_box.configure(state="normal")
        self.output_box.delete("1.0", ctk.END)
        self.output_box.configure(state="disabled")
        self.retry_button.configure(state="disabled")
        self.start_time = None

    def toggle_theme(self):
        if self.appearance_mode == "dark":
            self.appearance_mode = "light"
            self.border_color = "black"
            ctk.set_appearance_mode("light")
            self.theme_button.configure(text="☀️ Tema")
        else:
            self.appearance_mode = "dark"
            self.border_color = "white"
            ctk.set_appearance_mode("dark")
            self.theme_button.configure(text="🌙 Tema")

        self.entry.configure(border_color=self.border_color)
        self.output_box.configure(border_color=self.border_color)
        self.history_box.configure(border_color=self.border_color)

if __name__ == "__main__":
    app = KeyTesterApp()
    app.mainloop()
