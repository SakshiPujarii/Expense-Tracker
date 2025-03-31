import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import sqlite3
import matplotlib.pyplot as plt
from PIL import Image, ImageTk  # For background image

# Initialize Database
def init_db():
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT,
            amount REAL,
            date TEXT
        )
    """)
    
    conn.commit()
    conn.close()

# Function to Add Expense
def add_expense():
    category = category_entry.get()
    amount = amount_entry.get()
    date = date_entry.get_date()

    if not category or not amount:
        messagebox.showerror("Error", "All fields are required")
        return

    try:
        amount = float(amount)
    except ValueError:
        messagebox.showerror("Error", "Amount must be a number")
        return

    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO expenses (category, amount, date) VALUES (?, ?, ?)", 
                   (category, amount, date))
    conn.commit()
    conn.close()
    
    messagebox.showinfo("Success", "Expense added successfully")
    category_entry.delete(0, tk.END)
    amount_entry.delete(0, tk.END)
    load_expenses()

# Function to Load Expenses in Treeview
def load_expenses():
    for row in tree.get_children():
        tree.delete(row)

    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM expenses")
    records = cursor.fetchall()
    conn.close()

    for record in records:
        tree.insert("", "end", values=record)

# Function to Delete Selected Expense
def delete_expense():
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showerror("Error", "Please select an expense to delete.")
        return

    expense_id = tree.item(selected_item)['values'][0]

    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM expenses WHERE id=?", (expense_id,))
    conn.commit()
    conn.close()

    messagebox.showinfo("Success", "Expense deleted successfully.")
    load_expenses()

# Function to Delete All Expenses and Reset ID
def delete_all_expenses():
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()

    # Delete all records
    cursor.execute("DELETE FROM expenses")

    # Reset ID sequence
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='expenses'")

    conn.commit()
    conn.close()

    messagebox.showinfo("Success", "All expenses deleted, and ID reset.")
    load_expenses()

# Function to Visualize Expenses
def visualize_expenses():
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()
    cursor.execute("SELECT category, SUM(amount) FROM expenses GROUP BY category")
    data = cursor.fetchall()
    conn.close()

    if not data:
        messagebox.showinfo("No Data", "No expenses to show.")
        return

    categories, amounts = zip(*data)
    plt.figure(figsize=(6,6))
    plt.pie(amounts, labels=categories, autopct='%1.1f%%', startangle=140, colors=["blue", "red", "green", "purple", "orange"])
    plt.title("Expense Distribution")
    plt.show()

# Initialize Tkinter Window
root = tk.Tk()
root.title("Expense Tracker")
root.geometry("600x500")

# Load Background Image
try:
    bg_image = Image.open("money_background.jpg")  # Ensure this image exists in the same folder
    bg_image = bg_image.resize((600, 500), Image.Resampling.LANCZOS)
    bg_photo = ImageTk.PhotoImage(bg_image)
    
    bg_label = tk.Label(root, image=bg_photo)
    bg_label.place(relwidth=1, relheight=1)
except:
    print("Background image not found, proceeding without it.")

# Title Label
title_label = ttk.Label(root, text="Expense Tracker", font=("Arial", 20, "bold"), background="lightgray")
title_label.pack(pady=10)

# Input Fields
frame = ttk.Frame(root, padding=10)
frame.pack(pady=10)

ttk.Label(frame, text="Category:").grid(row=0, column=0, padx=5, pady=5)
category_entry = ttk.Entry(frame)
category_entry.grid(row=0, column=1, padx=5, pady=5)

ttk.Label(frame, text="Amount (₹):").grid(row=1, column=0, padx=5, pady=5)
amount_entry = ttk.Entry(frame)
amount_entry.grid(row=1, column=1, padx=5, pady=5)

ttk.Label(frame, text="Date:").grid(row=2, column=0, padx=5, pady=5)
date_entry = DateEntry(frame, width=15, background="blue", foreground="white", date_pattern="yyyy-MM-dd")
date_entry.grid(row=2, column=1, padx=5, pady=5)

# Buttons
btn_frame = ttk.Frame(root, padding=10)
btn_frame.pack()

add_button = ttk.Button(btn_frame, text="Add Expense", command=add_expense)
add_button.grid(row=0, column=0, padx=10)

delete_button = ttk.Button(btn_frame, text="Delete Selected Expense", command=delete_expense)
delete_button.grid(row=0, column=1, padx=10)

delete_all_button = ttk.Button(btn_frame, text="Delete All Expenses", command=delete_all_expenses)
delete_all_button.grid(row=0, column=2, padx=10)

view_button = ttk.Button(btn_frame, text="Visualize Expenses", command=visualize_expenses)
view_button.grid(row=0, column=3, padx=10)

# Table for Displaying Expenses
tree_frame = ttk.Frame(root)
tree_frame.pack(pady=10)

columns = ("ID", "Category", "Amount", "Date")
tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=10)

for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=120, anchor="center")

tree.pack()

# Initialize database and load expenses
init_db()
load_expenses()

root.mainloop()
