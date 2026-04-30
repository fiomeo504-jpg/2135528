import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

DATA_FILE = "books_data.json"
GENRES = ["Художественная литература", "Детектив", "Фантастика", "Фэнтези", 
          "Научная литература", "Биография", "Поэзия", "Приключения", "Роман", "Классика"]


class BookTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Book Tracker - Трекер прочитанных книг")
        self.root.geometry("900x600")
        self.root.resizable(True, True)

        self.books = []
        self.load_data()

        self.create_widgets()
        self.refresh_table()

    def create_widgets(self):
        # === Рамка добавления книги ===
        add_frame = tk.LabelFrame(self.root, text="Добавить книгу", padx=15, pady=10)
        add_frame.pack(fill="x", padx=10, pady=5)

        # Название
        tk.Label(add_frame, text="Название книги:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.title_entry = tk.Entry(add_frame, width=30)
        self.title_entry.grid(row=0, column=1, padx=5, pady=5)

        # Автор
        tk.Label(add_frame, text="Автор:").grid(row=0, column=2, sticky="e", padx=5, pady=5)
        self.author_entry = tk.Entry(add_frame, width=20)
        self.author_entry.grid(row=0, column=3, padx=5, pady=5)

        # Жанр
        tk.Label(add_frame, text="Жанр:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.genre_var = tk.StringVar(value=GENRES[0])
        self.genre_combo = ttk.Combobox(add_frame, textvariable=self.genre_var, values=GENRES, width=25)
        self.genre_combo.grid(row=1, column=1, padx=5, pady=5)

        # Количество страниц
        tk.Label(add_frame, text="Количество страниц:").grid(row=1, column=2, sticky="e", padx=5, pady=5)
        self.pages_entry = tk.Entry(add_frame, width=10)
        self.pages_entry.grid(row=1, column=3, padx=5, pady=5)

        # Кнопка добавить
        tk.Button(add_frame, text="➕ Добавить книгу", command=self.add_book,
                  bg="lightgreen", font=("Arial", 10)).grid(row=2, column=0, columnspan=4, pady=10)

        # === Рамка фильтрации ===
        filter_frame = tk.LabelFrame(self.root, text="Фильтрация", padx=15, pady=10)
        filter_frame.pack(fill="x", padx=10, pady=5)

        # Фильтр по жанру
        tk.Label(filter_frame, text="Фильтр по жанру:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.filter_genre_var = tk.StringVar(value="Все")
        genres_filter = ["Все"] + GENRES
        self.filter_genre_combo = ttk.Combobox(filter_frame, textvariable=self.filter_genre_var,
                                                values=genres_filter, width=25)
        self.filter_genre_combo.grid(row=0, column=1, padx=5, pady=5)

        # Фильтр по страницам
        tk.Label(filter_frame, text="Количество страниц >").grid(row=0, column=2, sticky="e", padx=5, pady=5)
        self.filter_pages_entry = tk.Entry(filter_frame, width=8)
        self.filter_pages_entry.grid(row=0, column=3, padx=5, pady=5)
        tk.Label(filter_frame, text="стр.").grid(row=0, column=4, padx=0, pady=5)

        # Кнопки фильтрации
        tk.Button(filter_frame, text="🔍 Применить фильтр", command=self.apply_filter,
                  bg="lightblue").grid(row=0, column=5, padx=10, pady=5)
        tk.Button(filter_frame, text="❌ Сбросить фильтр", command=self.reset_filter,
                  bg="lightgray").grid(row=0, column=6, padx=5, pady=5)

        # === Таблица книг ===
        table_frame = tk.LabelFrame(self.root, text="Список прочитанных книг", padx=10, pady=10)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)

        columns = ("ID", "Название", "Автор", "Жанр", "Страницы")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=12)

        self.tree.heading("ID", text="ID")
        self.tree.heading("Название", text="Название")
        self.tree.heading("Автор", text="Автор")
        self.tree.heading("Жанр", text="Жанр")
        self.tree.heading("Страницы", text="Страницы")

        self.tree.column("ID", width=40)
        self.tree.column("Название", width=250)
        self.tree.column("Автор", width=150)
        self.tree.column("Жанр", width=150)
        self.tree.column("Страницы", width=80)

        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill="both", expand=True)
        scrollbar.pack(side=tk.RIGHT, fill="y")

        # === Кнопки управления ===
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(fill="x", padx=10, pady=10)

        tk.Button(btn_frame, text="💾 Сохранить в JSON", command=self.save_data,
                  bg="lightyellow", width=15).pack(side="left", padx=5)
        tk.Button(btn_frame, text="📂 Загрузить из JSON", command=self.load_data_interactive,
                  bg="lightyellow", width=15).pack(side="left", padx=5)
        tk.Button(btn_frame, text="🗑 Удалить выбранное", command=self.delete_selected,
                  bg="salmon", width=15).pack(side="left", padx=5)

        # Статистика
        self.stats_label = tk.Label(btn_frame, text="", font=("Arial", 9), fg="blue")
        self.stats_label.pack(side="right", padx=10)
        self.update_stats()

    def validate_inputs(self, title, author, genre, pages_str):
        if not title.strip():
            messagebox.showerror("Ошибка", "Название книги не может быть пустым")
            return False
        if not author.strip():
            messagebox.showerror("Ошибка", "Автор не может быть пустым")
            return False
        if not genre.strip():
            messagebox.showerror("Ошибка", "Жанр не может быть пустым")
            return False
        try:
            pages = int(pages_str)
            if pages <= 0:
                messagebox.showerror("Ошибка", "Количество страниц должно быть положительным числом")
                return False
        except ValueError:
            messagebox.showerror("Ошибка", "Количество страниц должно быть целым числом")
            return False
        return True

    def add_book(self):
        title = self.title_entry.get().strip()
        author = self.author_entry.get().strip()
        genre = self.genre_var.get()
        pages_str = self.pages_entry.get().strip()

        if not self.validate_inputs(title, author, genre, pages_str):
            return

        pages = int(pages_str)
        book_id = len(self.books) + 1

        book = {
            "id": book_id,
            "title": title,
            "author": author,
            "genre": genre,
            "pages": pages
        }

        self.books.append(book)
        self.refresh_table()
        self.clear_inputs()
        self.update_stats()
        messagebox.showinfo("Успех", f"Книга «{title}» добавлена в список")

    def clear_inputs(self):
        self.title_entry.delete(0, tk.END)
        self.author_entry.delete(0, tk.END)
        self.pages_entry.delete(0, tk.END)

    def refresh_table(self, books_to_show=None):
        for row in self.tree.get_children():
            self.tree.delete(row)

        data = books_to_show if books_to_show is not None else self.books
        for book in data:
            self.tree.insert("", tk.END, values=(
                book["id"],
                book["title"],
                book["author"],
                book["genre"],
                book["pages"]
            ))

    def apply_filter(self):
        filtered = self.books[:]

        # Фильтр по жанру
        genre_filter = self.filter_genre_var.get()
        if genre_filter != "Все":
            filtered = [b for b in filtered if b["genre"] == genre_filter]

        # Фильтр по количеству страниц
        pages_filter_str = self.filter_pages_entry.get().strip()
        if pages_filter_str:
            try:
                pages_threshold = int(pages_filter_str)
                filtered = [b for b in filtered if b["pages"] > pages_threshold]
            except ValueError:
                messagebox.showerror("Ошибка", "Количество страниц в фильтре должно быть числом")
                return

        self.refresh_table(filtered)
        messagebox.showinfo("Фильтр", f"Показано книг: {len(filtered)}")

    def reset_filter(self):
        self.filter_genre_var.set("Все")
        self.filter_pages_entry.delete(0, tk.END)
        self.refresh_table()
        messagebox.showinfo("Фильтр", "Фильтр сброшен")

    def delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите книгу для удаления")
            return

        if messagebox.askyesno("Удаление", "Вы уверены, что хотите удалить выбранную книгу?"):
            for item in selected:
                values = self.tree.item(item, "values")
                book_id = int(values[0])
                self.books = [b for b in self.books if b["id"] != book_id]

            # Перенумеровываем ID
            for i, book in enumerate(self.books):
                book["id"] = i + 1

            self.refresh_table()
            self.update_stats()
            messagebox.showinfo("Удаление", "Книга удалена")

    def update_stats(self):
        total_books = len(self.books)
        total_pages = sum(book["pages"] for book in self.books)
        self.stats_label.config(text=f"📚 Всего книг: {total_books} | 📖 Всего страниц: {total_pages}")

    def save_data(self):
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(self.books, f, ensure_ascii=False, indent=4)
            messagebox.showinfo("Сохранение", f"Данные сохранены в {DATA_FILE}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить: {e}")

    def load_data(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    self.books = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                self.books = []

    def load_data_interactive(self):
        self.load_data()
        self.refresh_table()
        self.update_stats()
        messagebox.showinfo("Загрузка", f"Загружено книг: {len(self.books)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = BookTracker(root)
    root.mainloop()
  
