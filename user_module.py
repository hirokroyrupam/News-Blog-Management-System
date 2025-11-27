import tkinter as tk
from tkinter import ttk, messagebox
from db import get_connection
from news_module import UserNewsModal

class UserModule:
    def __init__(self, parent):
        self.win = tk.Toplevel(parent)
        self.win.title("Manage Users")
        self.win.geometry("800x500")
        self.win.configure(bg="#e6f0ff")
        self.entries = {}
        self.setup_ui()
        self.load_users()

    def setup_ui(self):
        header = tk.Frame(self.win, bg="#003366", height=50); header.pack(fill="x")
        tk.Label(header, text="Manage Users", bg="#003366", fg="white", font=("Arial",14,"bold")).pack(pady=8)

        frm = tk.Frame(self.win, bg="#cce0ff", pady=10); frm.pack(pady=8)
        labels = ["Username","Email","Age","Contact Number"]
        for i,l in enumerate(labels):
            tk.Label(frm, text=l, bg="#cce0ff").grid(row=0, column=i, padx=6)
            e = tk.Entry(frm, width=18)
            e.grid(row=1, column=i, padx=6)
            self.entries[l.lower().replace(" ","_")] = e

        btns = [
            ("Add User", self.add_user), ("View All", self.load_users),
            ("Search", self.search_user), ("Update", self.update_user),
            ("Delete", self.delete_user), ("Open News", self.open_user_news),
            ("Clear", self.clear_form)
        ]
        bfrm = tk.Frame(self.win, bg="#e6f0ff"); bfrm.pack(pady=6)
        for i,(txt, cmd) in enumerate(btns):
            color = "#cc3333" if "Delete" in txt else "#0059b3"
            tk.Button(bfrm, text=txt, width=12, bg=color, fg="white", command=cmd)\
              .grid(row=i//4, column=i%4, padx=6, pady=6)

        # Treeview
        cols = ("user_id","username","email","age","contact_number")
        tf = tk.Frame(self.win, bg="#e6f0ff"); tf.pack(fill="both", expand=True, padx=10, pady=10)
        self.tree = ttk.Treeview(tf, columns=cols, show="headings", selectmode="browse")
        for c in cols:
            self.tree.heading(c, text=c.upper() if c=="user_id" else c.capitalize())
            self.tree.column(c, width=120, anchor="center")
        self.tree.pack(side="left", fill="both", expand=True)
        scr = ttk.Scrollbar(tf, orient="vertical", command=self.tree.yview); scr.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scr.set)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

    def run_query(self,q,params=(),fetch=False):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(q, params)
        if fetch:
            rows = cur.fetchall()
            conn.close()
            return rows
        conn.commit()
        conn.close()

    def load_users(self):
        rows = self.run_query("SELECT user_id, username, email, age, contact_number FROM users", fetch=True)
        self.tree.delete(*self.tree.get_children())
        for i,r in enumerate(rows):
            self.tree.insert("", "end", values=r)
        self.clear_form()

    def add_user(self):
        d = {k:self.entries[k].get().strip() for k in self.entries}
        if not d["username"]:
            messagebox.showwarning("Warning","Username required.")
            return
        self.run_query("INSERT INTO users (username,email,age,contact_number) VALUES (%s,%s,%s,%s)",
                       (d["username"],d["email"],d["age"] or None,d["contact_number"]))
        self.load_users()

    def search_user(self):
        username = self.entries["username"].get().strip()
        if not username:
            messagebox.showwarning("Warning","Enter Username to search."); return
        rows = self.run_query("SELECT user_id, username,email,age,contact_number FROM users WHERE username LIKE %s",
                              (f"%{username}%",), fetch=True)
        self.tree.delete(*self.tree.get_children())
        for i,r in enumerate(rows): self.tree.insert("", "end", values=r)

    def on_select(self,e):
        sel = self.tree.selection()
        if sel:
            vals = self.tree.item(sel[0])["values"]
            if vals:
                self.entries["username"].delete(0, tk.END); self.entries["username"].insert(0, vals[1])
                self.entries["email"].delete(0, tk.END); self.entries["email"].insert(0, vals[2])
                self.entries["age"].delete(0, tk.END); self.entries["age"].insert(0, vals[3])
                self.entries["contact_number"].delete(0, tk.END); self.entries["contact_number"].insert(0, vals[4])

    def update_user(self):
        sel = self.tree.selection()
        if not sel: messagebox.showwarning("Warning","Select user to update."); return
        user_id = self.tree.item(sel[0])["values"][0]
        d = {k:self.entries[k].get().strip() for k in self.entries}
        self.run_query("UPDATE users SET username=%s,email=%s,age=%s,contact_number=%s WHERE user_id=%s",
                       (d["username"],d["email"],d["age"] or None,d["contact_number"],user_id))
        self.load_users()

    def delete_user(self):
        sel = self.tree.selection()
        if not sel: messagebox.showwarning("Warning","Select user to delete."); return
        user_id = self.tree.item(sel[0])["values"][0]
        if messagebox.askyesno("Confirm", f"Delete user id {user_id}? This will delete their news as well."):
            self.run_query("DELETE FROM users WHERE user_id=%s", (user_id,))
            self.load_users()

    def open_user_news(self):
        sel = self.tree.selection()
        if not sel: messagebox.showwarning("Warning","Select a user."); return
        user_id = self.tree.item(sel[0])["values"][0]
        UserNewsModal(self.win, user_id)

    def clear_form(self):
        for e in self.entries.values(): e.delete(0, tk.END)
