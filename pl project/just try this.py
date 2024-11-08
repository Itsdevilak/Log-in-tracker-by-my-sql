import mysql.connector
import bcrypt
import tkinter as tk
from tkinter import messagebox
from mysql.connector import Error

# Connect to MySQL database
def connect_to_db():
    try:
        return mysql.connector.connect(
            host="localhost",
            user="root",  # Change this to your MySQL username
            password="12345678",  # Change this to your MySQL password
            database="Ak"
        )
    except Error as err:
        messagebox.showerror("Database Error", f"Error connecting to MySQL: {err}")
        return None

# Register a user with hashed password
def register_user(username, password):
    db = connect_to_db()
    if db is None:
        return
    
    try:
        # Hash the password using bcrypt
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        cursor = db.cursor()
        cursor.execute("INSERT INTO Users (username, password) VALUES (%s, %s)", (username, hashed_password))
        db.commit()
        messagebox.showinfo("Registration Successful", f"User '{username}' registered successfully!")
    except Error as err:
        db.rollback()
        messagebox.showerror("Registration Error", f"Error registering user: {err}")
    finally:
        db.close()

# Login a user and track the attempt
def login_user(username, password):
    db = connect_to_db()
    if db is None:
        return
    
    cursor = db.cursor()
    cursor.execute("SELECT user_id, password FROM Users WHERE username = %s", (username,))
    user = cursor.fetchone()

    if user is None:
        log_attempt(username, 'failure')  # Log the failed attempt
        db.close()
        messagebox.showerror("Login Failed", "Invalid username or password.")
        return
    
    user_id, stored_hash = user

    # Ensure stored_hash is in bytes
    if isinstance(stored_hash, str):
        stored_hash = stored_hash.encode('utf-8')  # Convert to bytes

    if bcrypt.checkpw(password.encode('utf-8'), stored_hash):
        log_attempt(username, 'success', user_id)  # Log the successful attempt
        db.close()
        messagebox.showinfo("Login Successful", f"Welcome, {username}!")
    else:
        log_attempt(username, 'failure', user_id)  # Log the failed attempt
        db.close()
        messagebox.showerror("Login Failed", "Invalid username or password.")

# Log the login attempt
def log_attempt(username, status, user_id=None):
    db = connect_to_db()
    if db is None:
        return
    
    if user_id is None:  # If user_id is not passed, fetch it
        cursor = db.cursor()
        cursor.execute("SELECT user_id FROM Users WHERE username = %s", (username,))
        user_id = cursor.fetchone()
        if user_id is None:
            db.close()
            return  # No user found with this username
        user_id = user_id[0]  # Extract user_id from tuple
    
    cursor = db.cursor()
    cursor.execute("INSERT INTO LoginAttempts (user_id, status) VALUES (%s, %s)", (user_id, status))
    db.commit()
    db.close()

# Get the number of successful and failed login attempts for a user
def get_login_stats(username):
    db = connect_to_db()
    if db is None:
        return
    
    cursor = db.cursor()
    cursor.execute(""" 
        SELECT 
            SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) AS success_count,
            SUM(CASE WHEN status = 'failure' THEN 1 ELSE 0 END) AS failure_count
        FROM LoginAttempts
        WHERE user_id = (SELECT user_id FROM Users WHERE username = %s)
    """, (username,))
    
    result = cursor.fetchone()
    db.close()
    
    if result:
        success_count, failure_count = result
        return success_count, failure_count
    else:
        return 0, 0

# GUI for Login and Registration
class Application(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Login Page")
        self.geometry("400x300")

        self.label_username = tk.Label(self, text="Username:")
        self.label_username.pack(pady=10)

        self.entry_username = tk.Entry(self)
        self.entry_username.pack(pady=5)

        self.label_password = tk.Label(self, text="Password:")
        self.label_password.pack(pady=10)

        self.entry_password = tk.Entry(self, show="*")
        self.entry_password.pack(pady=5)

        self.login_button = tk.Button(self, text="Login", command=self.login)
        self.login_button.pack(pady=10)

        self.register_button = tk.Button(self, text="Register", command=self.register)
        self.register_button.pack(pady=10)

        self.stats_button = tk.Button(self, text="View Stats", command=self.view_stats)
        self.stats_button.pack(pady=10)

    def login(self):
        username = self.entry_username.get()
        password = self.entry_password.get()
        if not username or not password:
            messagebox.showerror("Input Error", "Please enter both username and password.")
            return
        login_user(username, password)

    def register(self):
        username = self.entry_username.get()
        password = self.entry_password.get()
        if not username or not password:
            messagebox.showerror("Input Error", "Please enter both username and password.")
            return
        register_user(username, password)

    def view_stats(self):
        username = self.entry_username.get()
        if not username:
            messagebox.showerror("Input Error", "Please enter a username.")
            return
        success_count, failure_count = get_login_stats(username)
        messagebox.showinfo("Login Stats", f"Successful logins: {success_count}\nFailed logins: {failure_count}")

# Running the application
if __name__ == "__main__":
    app = Application()
    app.mainloop()
