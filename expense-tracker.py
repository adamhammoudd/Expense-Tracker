import tkinter as tk
from tkinter import messagebox, ttk
import os
import json
from datetime import datetime

DATA_FILE = "data.json"
users = {}
current_user = None

# Utility Functions
def save_data():
    try:
        with open(DATA_FILE, 'w') as file:
            json.dump(users, file, indent=4)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save data: {e}")

def load_data():
    global users
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as file:
                users = json.load(file)
        except json.JSONDecodeError:
            users = {}
            messagebox.showerror("Error", "Data file is corrupted. Resetting data.")

def switch_frame(frame):
    frame.tkraise()

def update_balance():
    if current_user:
        balance_label.config(text=f"Current Balance: ${users[current_user]['balance']:.2f}")

# User Authentication
def login():
    global current_user
    email = email_entry.get()
    password = password_entry.get()
    
    if not email or not password:
        messagebox.showerror("Error", "All fields are required!")
        return
    
    if email in users and users[email]["password"] == password:
        current_user = email
        welcome_label.config(text=f"Welcome, {users[email]['name']}!")
        update_balance()
        switch_frame(main_frame)
    else:
        messagebox.showerror("Error", "Invalid email or password!")

def signup():
    global current_user
    name = name_entry.get()
    email = signup_email_entry.get()
    password = signup_password_entry.get()
    
    if not name or not email or not password:
        messagebox.showerror("Error", "All fields are required!")
        return
    
    if email in users:
        messagebox.showerror("Error", "Email already registered!")
        return
    
    users[email] = {
        "name": name,
        "password": password,
        "transactions": [],
        "balance": 0.0
    }
    save_data()
    current_user = email
    welcome_label.config(text=f"Welcome, {name}!")
    update_balance()
    switch_frame(main_frame)
    messagebox.showinfo("Success", "Account created successfully!")

# Transaction Management
def add_transaction(transaction_type):
    if not current_user:
        messagebox.showerror("Error", "No user logged in!")
        return
    
    amount = amount_entry.get()
    category = category_entry.get()
    
    if not amount or not category:
        messagebox.showerror("Error", "All fields are required!")
        return
    
    try:
        amount = float(amount)
        if amount <= 0:
            messagebox.showerror("Error", "Amount must be positive!")
            return
    except ValueError:
        messagebox.showerror("Error", "Amount must be a number!")
        return
    
    transaction = {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "type": transaction_type,
        "amount": amount,
        "category": category
    }
    
    users[current_user]["transactions"].insert(0, transaction)
    
    if transaction_type == "Income":
        users[current_user]["balance"] += amount
    else:
        users[current_user]["balance"] -= amount
    
    save_data()
    messagebox.showinfo("Success", f"{transaction_type} added successfully!")
    amount_entry.delete(0, tk.END)
    category_entry.delete(0, tk.END)
    update_balance()

def remove_transaction():
    if not current_user:
        messagebox.showerror("Error", "No user logged in!")
        return
    
    selected = transaction_tree.selection()
    if not selected:
        messagebox.showerror("Error", "Please select a transaction to remove!")
        return
    
    transactions_to_remove = []
    for item in selected:
        values = transaction_tree.item(item)['values']
        transactions_to_remove.append({
            'date': values[0],
            'type': values[1],
            'amount': float(values[2].replace('$', '').replace('-', '')),
            'category': values[3]
        })
    
    for t in transactions_to_remove:
        for idx, transaction in enumerate(users[current_user]["transactions"]):
            if (transaction['date'] == t['date'] and
                transaction['type'] == t['type'] and
                transaction['amount'] == t['amount'] and
                transaction['category'] == t['category']):
                
                if t['type'] == "Income":
                    users[current_user]['balance'] -= t['amount']
                else:
                    users[current_user]['balance'] += t['amount']
                
                users[current_user]['transactions'].pop(idx)
                break
    
    refresh_transaction_tree()
    save_data()
    update_balance()
    messagebox.showinfo("Success", f"Removed {len(transactions_to_remove)} transaction(s) successfully!")

def refresh_transaction_tree():
    for item in transaction_tree.get_children():
        transaction_tree.delete(item)
    
    for transaction in sorted(users[current_user]["transactions"], key=lambda x: x["date"], reverse=True):
        amount_str = f"${transaction['amount']:.2f}" if transaction['type'] == "Income" else f"-${transaction['amount']:.2f}"
        transaction_tree.insert("", tk.END, values=(
            transaction['date'],
            transaction['type'],
            amount_str,
            transaction['category']
        ))

def show_transactions():
    if not current_user:
        return
    
    transactions_window = tk.Toplevel(root)
    transactions_window.title("Transaction History")
    transactions_window.geometry("600x500")
    transactions_window.configure(bg="white")
    
    main_frame = tk.Frame(transactions_window, bg="white")
    main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    tree_frame = tk.Frame(main_frame, bg="white")
    tree_frame.pack(fill=tk.BOTH, expand=True)
    
    scroll_y = tk.Scrollbar(tree_frame)
    scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
    
    global transaction_tree
    transaction_tree = ttk.Treeview(tree_frame, yscrollcommand=scroll_y.set, selectmode="extended")
    scroll_y.config(command=transaction_tree.yview)
    
    transaction_tree['columns'] = ("Date", "Type", "Amount", "Category")
    transaction_tree.column("#0", width=0, stretch=tk.NO)
    transaction_tree.column("Date", anchor=tk.W, width=120)
    transaction_tree.column("Type", anchor=tk.W, width=100)
    transaction_tree.column("Amount", anchor=tk.W, width=100)
    transaction_tree.column("Category", anchor=tk.W, width=150)
    transaction_tree.heading("Date", text="Date", anchor=tk.W)
    transaction_tree.heading("Type", text="Type", anchor=tk.W)
    transaction_tree.heading("Amount", text="Amount", anchor=tk.W)
    transaction_tree.heading("Category", text="Category", anchor=tk.W)
    
    refresh_transaction_tree()
    transaction_tree.pack(fill=tk.BOTH, expand=True)
    
    button_frame = tk.Frame(main_frame, bg="white")
    button_frame.pack(pady=10)
    
    remove_btn = tk.Button(button_frame, text="Remove Selected", font=("Arial", 10, "bold"), bg="#3E5BA4", fg="white",
                           command=remove_transaction)
    remove_btn.pack(side=tk.LEFT, padx=5)

# Main Window Setup
root = tk.Tk()
root.title("Finance App")
root.geometry("400x600")
root.resizable(False, False)
root.configure(bg="white")

# Frames
welcome_frame = tk.Frame(root, bg="white")
login_frame = tk.Frame(root, bg="white")
signup_frame = tk.Frame(root, bg="white")
main_frame = tk.Frame(root, bg="white")
transaction_frame = tk.Frame(root, bg="white")

for frame in (welcome_frame, login_frame, signup_frame, main_frame, transaction_frame):
    frame.place(x=0, y=0, width=400, height=600)

# Welcome Frame
tk.Label(welcome_frame, text="Finance App", font=("Arial", 24, "bold"), bg="white", fg="#3E5BA4").place(relx=0.5, rely=0.3, anchor="center")
tk.Button(welcome_frame, text="Log In", font=("Arial", 12, "bold"), bg="white", fg="#3E5BA4", command=lambda: switch_frame(login_frame)).place(relx=0.5, rely=0.5, anchor="center")
tk.Button(welcome_frame, text="Sign Up", font=("Arial", 12, "bold"), bg="white", fg="#3E5BA4", command=lambda: switch_frame(signup_frame)).place(relx=0.5, rely=0.6, anchor="center")

# Login Frame
tk.Label(login_frame, text="Log In", font=("Arial", 20, "bold"), bg="white", fg="#3E5BA4").place(relx=0.5, rely=0.2, anchor="center")
tk.Label(login_frame, text="Email", bg="white", fg="#3E5BA4").place(relx=0.5, rely=0.35, anchor="center")
email_entry = tk.Entry(login_frame, font=("Arial", 10), bd=1)
email_entry.place(relx=0.5, rely=0.4, anchor="center", width=250, height=25)
tk.Label(login_frame, text="Password", bg="white", fg="#3E5BA4").place(relx=0.5, rely=0.5, anchor="center")
password_entry = tk.Entry(login_frame, show="*", font=("Arial", 10), bd=1)
password_entry.place(relx=0.5, rely=0.55, anchor="center", width=250, height=25)
tk.Button(login_frame, text="Log In", font=("Arial", 12, "bold"), bg="#3E5BA4", fg="white", command=login).place(relx=0.5, rely=0.7, anchor="center")
tk.Button(login_frame, text="Back", bg="white", fg="#3E5BA4", command=lambda: switch_frame(welcome_frame)).place(relx=0.5, rely=0.8, anchor="center")

# Signup Frame
tk.Label(signup_frame, text="Sign Up", font=("Arial", 20, "bold"), bg="white", fg="#3E5BA4").place(relx=0.5, rely=0.15, anchor="center")
tk.Label(signup_frame, text="Full Name", bg="white", fg="#3E5BA4").place(relx=0.5, rely=0.25, anchor="center")
name_entry = tk.Entry(signup_frame, font=("Arial", 10), bd=1)
name_entry.place(relx=0.5, rely=0.3, anchor="center", width=250, height=25)
tk.Label(signup_frame, text="Email", bg="white", fg="#3E5BA4").place(relx=0.5, rely=0.4, anchor="center")
signup_email_entry = tk.Entry(signup_frame, font=("Arial", 10), bd=1)
signup_email_entry.place(relx=0.5, rely=0.45, anchor="center", width=250, height=25)
tk.Label(signup_frame, text="Password", bg="white", fg="#3E5BA4").place(relx=0.5, rely=0.55, anchor="center")
signup_password_entry = tk.Entry(signup_frame, show="*", font=("Arial", 10), bd=1)
signup_password_entry.place(relx=0.5, rely=0.6, anchor="center", width=250, height=25)
tk.Button(signup_frame, text="Sign Up", font=("Arial", 12, "bold"), bg="#3E5BA4", fg="white", command=signup).place(relx=0.5, rely=0.75, anchor="center")
tk.Button(signup_frame, text="Back", bg="white", fg="#3E5BA4", command=lambda: switch_frame(welcome_frame)).place(relx=0.5, rely=0.85, anchor="center")

# Main Frame
welcome_label = tk.Label(main_frame, text="Welcome!", font=("Arial", 16, "bold"), bg="white", fg="#3E5BA4")
welcome_label.place(relx=0.5, rely=0.1, anchor="center")
balance_label = tk.Label(main_frame, text="Balance: $0.00", font=("Arial", 14), bg="white", fg="#3E5BA4")
balance_label.place(relx=0.5, rely=0.2, anchor="center")
tk.Button(main_frame, text="View Transactions", font=("Arial", 12, "bold"), bg="#3E5BA4", fg="white", command=show_transactions).place(relx=0.5, rely=0.4, anchor="center")
tk.Button(main_frame, text="Add Transaction", font=("Arial", 12, "bold"), bg="#3E5BA4", fg="white", command=lambda: switch_frame(transaction_frame)).place(relx=0.5, rely=0.5, anchor="center")
tk.Button(main_frame, text="Logout", font=("Arial", 12), bg="white", fg="#3E5BA4", command=lambda: switch_frame(welcome_frame)).place(relx=0.5, rely=0.6, anchor="center")

# Transaction Frame
tk.Label(transaction_frame, text="Add Transaction", font=("Arial", 16, "bold"), bg="white", fg="#3E5BA4").place(relx=0.5, rely=0.1, anchor="center")
tk.Label(transaction_frame, text="Amount", bg="white", fg="#3E5BA4").place(relx=0.5, rely=0.25, anchor="center")
amount_entry = tk.Entry(transaction_frame, font=("Arial", 10), bd=1)
amount_entry.place(relx=0.5, rely=0.3, anchor="center", width=250, height=25)
tk.Label(transaction_frame, text="Category", bg="white", fg="#3E5BA4").place(relx=0.5, rely=0.4, anchor="center")
category_entry = tk.Entry(transaction_frame, font=("Arial", 10), bd=1)
category_entry.place(relx=0.5, rely=0.45, anchor="center", width=250, height=25)
tk.Button(transaction_frame, text="Add Expense", font=("Arial", 12, "bold"), bg="#3E5BA4", fg="white", command=lambda: add_transaction("Expense")).place(relx=0.5, rely=0.6, anchor="center")
tk.Button(transaction_frame, text="Add Income", font=("Arial", 12, "bold"), bg="#3E5BA4", fg="white", command=lambda: add_transaction("Income")).place(relx=0.5, rely=0.7, anchor="center")
tk.Button(transaction_frame, text="Back", bg="white", fg="#3E5BA4", command=lambda: switch_frame(main_frame)).place(relx=0.5, rely=0.8, anchor="center")

# Initialize and Run
load_data()
switch_frame(welcome_frame)
root.mainloop()