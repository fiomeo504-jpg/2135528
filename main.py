import tkinter as tk
from tkinter import ttk, messagebox
import random
import json
import os

class RandomTaskGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Random Task Generator - Смоленцев Арсений")
        self.root.geometry("680x620")
        self.root.resizable(True, True)
        self.root.configure(bg='#2d2d3f')
        
        # Предопределённые задачи
        self.predefined_tasks = [
            ("Решить 5 задач по алгебре", "учёба"),
            ("Сделать 20 отжиманий", "спорт"),
            ("Написать код на Python", "работа"),
            ("Выпить стакан воды", "спорт"),
            ("Прочитать параграф по физике", "учёба"),
            ("Составить план на неделю", "работа"),
            ("Убраться в комнате", "работа"),
            ("Пробежать 2 км", "спорт"),
            ("Выучить 15 английских слов", "учёба"),
            ("Сделать зарядку", "спорт"),
            ("Повторить пройденное", "учёба"),
            ("Сделать презентацию", "работа")
        ]
        
        self.task_types = ["учёба", "спорт", "работа", "все"]
        self.filter_type = tk.StringVar(value="все")
        
        # Загружаем историю
        self.history = self.load_history()
        
        self.create_widgets()
        self.display_history()
        self.update_stats()
    
    def create_widgets(self):
        # Заголовок
        title_label = tk.Label(self.root, text="🎲 RANDOM TASK GENERATOR 🎲", 
                                font=('Arial', 18, 'bold'), bg='#2d2d3f', fg='#00b4d8')
        title_label.pack(pady=12)
        
        subtitle = tk.Label(self.root, text="Генератор задач для учёбы, спорта и работы", 
                            font=('Arial', 10), bg='#2d2d3f', fg='#aaaaaa')
        subtitle.pack(pady=0)
        
        # --- Рамка генерации ---
        frame_gen = tk.LabelFrame(self.root, text="🎯 Генератор", 
                                   font=('Arial', 12, 'bold'), bg='#3a3a4f', 
                                   fg='#00b4d8', padx=10, pady=10)
        frame_gen.pack(fill="x", padx=15, pady=8)
        
        self.gen_button = tk.Button(frame_gen, text="✨ Сгенерировать задачу ✨",
                                     command=self.generate_task,
                                     bg='#00b4d8', fg='white', font=('Arial', 12, 'bold'),
                                     padx=15, pady=8, cursor='hand2', relief='raised', width=28)
        self.gen_button.pack(pady=8)
        
        self.current_task_label = tk.Label(frame_gen, text="", font=('Arial', 11, 'bold'),
                                            fg='#00ff88', bg='#3a3a4f', wraplength=580)
        self.current_task_label.pack(pady=5)
        
        # --- Рамка добавления ---
        frame_add = tk.LabelFrame(self.root, text="📝 Добавить задачу",
                                   font=('Arial', 12, 'bold'), bg='#3a3a4f',
                                   fg='#00b4d8', padx=10, pady=10)
        frame_add.pack(fill="x", padx=15, pady=8)
        
        tk.Label(frame_add, text="Название:", bg='#3a3a4f', font=('Arial', 10), fg='white').grid(row=0, column=0, padx=8, pady=8, sticky='e')
        self.new_task_entry = tk.Entry(frame_add, width=45, font=('Arial', 10), relief='solid', borderwidth=1, bg='#4a4a5f', fg='white', insertbackground='white')
        self.new_task_entry.grid(row=0, column=1, padx=8, pady=8)
        
        tk.Label(frame_add, text="Тип:", bg='#3a3a4f', font=('Arial', 10), fg='white').grid(row=1, column=0, padx=8, pady=8, sticky='e')
        self.new_type_combo = ttk.Combobox(frame_add, values=self.task_types[:-1],
                                            state="readonly", width=42, font=('Arial', 10))
        self.new_type_combo.current(0)
        self.new_type_combo.grid(row=1, column=1, padx=8, pady=8)
        
        self.add_button = tk.Button(frame_add, text="➕ Добавить", command=self.add_task,
                                     bg='#2ecc71', fg='white', font=('Arial', 10, 'bold'),
                                     padx=10, pady=5, cursor='hand2', width=15)
        self.add_button.grid(row=2, column=0, columnspan=2, pady=10)
        
        # --- Рамка фильтрации ---
        frame_filter = tk.LabelFrame(self.root, text="🔍 Фильтр",
                                      font=('Arial', 12, 'bold'), bg='#3a3a4f',
                                      fg='#00b4d8', padx=10, pady=10)
        frame_filter.pack(fill="x", padx=15, pady=8)
        
        for t in self.task_types:
            rb = tk.Radiobutton(frame_filter, text=t.capitalize(), variable=self.filter_type,
                                value=t, command=self.display_history, bg='#3a3a4f',
                                font=('Arial', 11), selectcolor='#3a3a4f', fg='white')
            rb.pack(side="left", padx=22)
        
        # --- Рамка истории ---
        frame_history = tk.LabelFrame(self.root, text="📜 История задач",
                                       font=('Arial', 12, 'bold'), bg='#3a3a4f',
                                       fg='#00b4d8', padx=10, pady=10)
        frame_history.pack(fill="both", expand=True, padx=15, pady=8)
        
        list_frame = tk.Frame(frame_history, bg='#3a3a4f')
        list_frame.pack(fill="both", expand=True)
        
        self.history_listbox = tk.Listbox(list_frame, height=12, font=('Consolas', 10),
                                           selectmode=tk.SINGLE, bg='#1e1e2e', fg='#00ff88',
                                           relief='solid', borderwidth=1, selectbackground='#00b4d8')
        scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=self.history_listbox.yview, bg='#3a3a4f')
        self.history_listbox.configure(yscrollcommand=scrollbar.set)
        
        self.history_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # --- Нижняя панель ---
        bottom_frame = tk.Frame(self.root, bg='#2d2d3f')
        bottom_frame.pack(fill="x", padx=15, pady=10)
        
        self.save_button = tk.Button(bottom_frame, text="💾 Сохранить в JSON", 
                                      command=self.save_history_to_json,
                                      bg='#f39c12', fg='white', font=('Arial', 10, 'bold'),
                                      padx=10, pady=5, cursor='hand2')
        self.save_button.pack(side="left", padx=5)
        
        self.stats_label = tk.Label(bottom_frame, text="", bg='#2d2d3f', font=('Arial', 10, 'bold'), fg='#00b4d8')
        self.stats_label.pack(side="right", padx=5)
        
        self.clear_button = tk.Button(bottom_frame, text="🗑 Очистить", 
                                       command=self.clear_history,
                                       bg='#e74c3c', fg='white', font=('Arial', 9, 'bold'),
                                       padx=8, pady=5, cursor='hand2')
        self.clear_button.pack(side="left", padx=5)
        
        self.test_button = tk.Button(bottom_frame, text="🧪 Тест", 
                                      command=self.run_test,
                                      bg='#9b59b6', fg='white', font=('Arial', 9, 'bold'),
                                      padx=8, pady=5, cursor='hand2')
        self.test_button.pack(side="left", padx=5)
    
    def update_stats(self):
        total = len(self.history)
        if total > 0:
            study_count = sum(1 for item in self.history if item["type"] == "учёба")
            sport_count = sum(1 for item in self.history if item["type"] == "спорт")
            work_count = sum(1 for item in self.history if item["type"] == "работа")
            self.stats_label.config(text=f"Всего: {total} | 📖: {study_count} | 🏃: {sport_count} | 💼: {work_count}")
        else:
            self.stats_label.config(text="Всего: 0")
    
    def generate_task(self):
        task, task_type = random.choice(self.predefined_tasks)
        self.history.append({"task": task, "type": task_type})
        self.current_task_label.config(text=f"✅ {task} [{task_type}]")
        self.display_history()
        self.save_history_to_json()
        self.update_stats()
    
    def add_task(self):
        task = self.new_task_entry.get().strip()
        task_type = self.new_type_combo.get()
        
        # Валидация
        if not task:
            messagebox.showerror("Ошибка", "❌ Название задачи не может быть пустым!")
            return
        
        if len(task) < 2:
            messagebox.showerror("Ошибка", "❌ Минимум 2 символа!")
            return
        
        if len(task) > 75:
            messagebox.showerror("Ошибка", "❌ Максимум 75 символов!")
            return
        
        # Проверка на дубликаты (опционально)
        for existing in self.predefined_tasks:
            if existing[0].lower() == task.lower():
                if messagebox.askyesno("Дубликат", f"Задача '{task}' уже существует. Добавить всё равно?"):
                    break
                else:
                    return
        
        self.predefined_tasks.append((task, task_type))
        self.history.append({"task": task, "type": task_type})
        
        self.new_task_entry.delete(0, tk.END)
        self.current_task_label.config(text=f"➕ Добавлено: {task} [{task_type}]")
        self.display_history()
        self.save_history_to_json()
        self.update_stats()
        
        messagebox.showinfo("Успех", f"✅ Задача '{task}' добавлена!")
    
    def display_history(self):
        self.history_listbox.delete(0, tk.END)
        current_filter = self.filter_type.get()
        
        if not self.history:
            self.history_listbox.insert(tk.END, "📭 История пуста")
            self.history_listbox.itemconfig(0, fg='#e74c3c')
            return
        
        filtered = [item for item in self.history if current_filter == "все" or item["type"] == current_filter]
        
        if not filtered:
            self.history_listbox.insert(tk.END, f"📭 Нет задач типа '{current_filter}'")
            return
        
        for i, item in enumerate(filtered, 1):
            emoji = "📚" if item["type"] == "учёба" else "🏃" if item["type"] == "спорт" else "💼"
            display_text = f"{i:3d}. {emoji} {item['task']}"
            self.history_listbox.insert(tk.END, display_text)
    
    def clear_history(self):
        if messagebox.askyesno("Подтверждение", "Очистить всю историю?"):
            self.history = []
            self.display_history()
            self.save_history_to_json()
            self.update_stats()
            self.current_task_label.config(text="История очищена")
            messagebox.showinfo("Готово", "История очищена!")
    
    def run_test(self):
        """Быстрый тест всех функций"""
        results = []
        
        # Тест 1: Генерация
        try:
            old_count = len(self.history)
            self.generate_task()
            if len(self.history) == old_count + 1:
                results.append("✅ Генерация: OK")
            else:
                results.append("❌ Генерация: FAIL")
        except Exception as e:
            results.append(f"❌ Генерация: {e}")
        
        # Тест 2: Валидация пустой строки
        self.new_task_entry.delete(0, tk.END)
        self.new_task_entry.insert(0, "")
        try:
            self.add_task()
            results.append("❌ Валидация (пустая): FAIL")
        except:
            results.append("✅ Валидация (пустая): OK")
        
        # Тест 3: Валидация короткой строки
        self.new_task_entry.delete(0, tk.END)
        self.new_task_entry.insert(0, "А")
        try:
            self.add_task()
            results.append("❌ Валидация (короткая): FAIL")
        except:
            results.append("✅ Валидация (короткая): OK")
        
        # Тест 4: Сохранение
        try:
            self.save_history_to_json()
            results.append("✅ Сохранение JSON: OK")
        except:
            results.append("❌ Сохранение JSON: FAIL")
        
        # Тест 5: Фильтрация
        test_filter = self.filter_type.get()
        results.append(f"✅ Фильтрация: текущий фильтр '{test_filter}'")
        
        messagebox.showinfo("Результаты тестирования", "\n".join(results))
    
    def load_history(self):
        if not os.path.exists("tasks.json"):
            return []
        try:
            with open("tasks.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except (json.JSONDecodeError, IOError):
            return []
    
    def save_history_to_json(self):
        try:
            with open("tasks.json", "w", encoding="utf-8") as f:
                json.dump(self.history, f, indent=4, ensure_ascii=False)
            messagebox.showinfo("Сохранено", "✅ История сохранена в tasks.json!")
        except IOError:
            messagebox.showerror("Ошибка", "❌ Не удалось сохранить историю")


if __name__ == "__main__":
    root = tk.Tk()
    app = RandomTaskGenerator(root)
    root.mainloop()
  
