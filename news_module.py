import tkinter as tk
from tkinter import ttk, messagebox
from db import get_connection

class NewsModule:
    def __init__(self,parent):
        self.win = tk.Toplevel(parent)
        self.win.title("Manage News")
        self.win.geometry("900x500")
        self.win.configure(bg="#e6f0ff")
        self.entries = {}
        self.setup_ui()
        self.load_news()

    def setup_ui(self):
        header = tk.Frame(self.win,bg="#003366",height=50); header.pack(fill="x")
        tk.Label(header,text="Manage News",bg="#003366",fg="white",font=("Arial",14,"bold")).pack(pady=8)

        frm = tk.Frame(self.win,bg="#cce0ff",pady=8); frm.pack(pady=6,padx=6)
        labels = ["Title","User ID"]
        for i,l in enumerate(labels):
            tk.Label(frm,text=l,bg="#cce0ff").grid(row=0,column=i,padx=6)
            e = tk.Entry(frm,width=25)
            e.grid(row=1,column=i,padx=6)
            self.entries[l.lower().replace(" ","_")] = e

        tk.Label(frm,text="Body",bg="#cce0ff").grid(row=2,column=0,padx=6,pady=6,sticky="w")
        self.txt_body = tk.Text(frm,width=80,height=6)
        self.txt_body.grid(row=3,column=0,columnspan=4,padx=6,pady=6)

        btns = [
            ("Add News", self.add_news),
            ("View All", self.load_news),
            ("Search", self.search_news),
            ("Update", self.update_news),
            ("Delete", self.delete_news),
            ("Clear", self.clear_form)
        ]
        bfrm = tk.Frame(self.win,bg="#e6f0ff"); bfrm.pack(pady=6)
        for i,(txt,cmd) in enumerate(btns):
            color = "#cc3333" if "Delete" in txt else "#0059b3"
            tk.Button(bfrm,text=txt,width=12,bg=color,fg="white",command=cmd).grid(row=i//4,column=i%4,padx=6,pady=6)

        # Treeview
        cols = ("news_id","title","body","username","created_at")
        tf = tk.Frame(self.win,bg="#e6f0ff"); tf.pack(fill="both",expand=True,padx=10,pady=10)
        self.tree = ttk.Treeview(tf,columns=cols,show="headings")
        for c in cols: self.tree.heading(c,text=c.upper() if c=="news_id" else c.capitalize()); self.tree.column(c,width=140,anchor="center")
        self.tree.pack(side="left",fill="both",expand=True)
        scr = ttk.Scrollbar(tf,orient="vertical",command=self.tree.yview); scr.pack(side="right",fill="y")
        self.tree.configure(yscrollcommand=scr.set)
        self.tree.bind("<<TreeviewSelect>>",self.on_select)

    def run_query(self,q,params=(),fetch=False):
        conn = get_connection(); cur = conn.cursor()
        cur.execute(q,params)
        if fetch:
            rows = cur.fetchall(); conn.close(); return rows
        conn.commit(); conn.close()

    def load_news(self):
        q = """SELECT n.news_id, n.title, n.body, u.username, n.created_at
               FROM news n LEFT JOIN users u ON n.user_id = u.user_id
               ORDER BY n.created_at DESC"""
        rows = self.run_query(q,fetch=True)
        self.tree.delete(*self.tree.get_children())
        for i,r in enumerate(rows): self.tree.insert("", "end", values=r)
        self.clear_form()

    def add_news(self):
        title = self.entries["title"].get().strip()
        user_id = self.entries["user_id"].get().strip()
        body = self.txt_body.get("1.0",tk.END).strip()
        if not title or not body or not user_id:
            messagebox.showwarning("Warning","Title, Body, and User ID required."); return
        self.run_query("INSERT INTO news (title,body,user_id) VALUES (%s,%s,%s)", (title,body,int(user_id)))
        self.load_news()

    def search_news(self):
        title = self.entries["title"].get().strip()
        if not title: messagebox.showwarning("Warning","Enter Title to search."); return
        q = """SELECT n.news_id,n.title,n.body,u.username,n.created_at
               FROM news n LEFT JOIN users u ON n.user_id=u.user_id
               WHERE n.title LIKE %s"""
        rows = self.run_query(q,(f"%{title}%",),fetch=True)
        self.tree.delete(*self.tree.get_children())
        for r in rows: self.tree.insert("", "end", values=r)

    def on_select(self,e):
        sel = self.tree.selection()
        if sel:
            vals = self.tree.item(sel[0])["values"]
            if vals:
                nid = vals[0]
                row = self.run_query("SELECT title,body,user_id FROM news WHERE news_id=%s",(nid,),fetch=True)
                t,b,u = row[0]
                self.entries["title"].delete(0,tk.END); self.entries["title"].insert(0,t)
                self.entries["user_id"].delete(0,tk.END); self.entries["user_id"].insert(0,u)
                self.txt_body.delete("1.0",tk.END); self.txt_body.insert("1.0",b)

    def update_news(self):
        sel = self.tree.selection()
        if not sel: messagebox.showwarning("Warning","Select news to update."); return
        nid = self.tree.item(sel[0])["values"][0]
        title = self.entries["title"].get().strip()
        user_id = self.entries["user_id"].get().strip()
        body = self.txt_body.get("1.0",tk.END).strip()
        if not title or not body or not user_id:
            messagebox.showwarning("Warning","Title, Body, and User ID required."); return
        self.run_query("UPDATE news SET title=%s,body=%s,user_id=%s WHERE news_id=%s",
                       (title,body,int(user_id),nid))
        self.load_news()

    def delete_news(self):
        sel = self.tree.selection()
        if not sel: messagebox.showwarning("Warning","Select news to delete."); return
        nid = self.tree.item(sel[0])["values"][0]
        if messagebox.askyesno("Confirm",f"Delete news id {nid}?"):
            self.run_query("DELETE FROM news WHERE news_id=%s",(nid,))
            self.load_news()

    def clear_form(self):
        self.entries["title"].delete(0,tk.END)
        self.entries["user_id"].delete(0,tk.END)
        self.txt_body.delete("1.0",tk.END)

# Modal to show user's news
class UserNewsModal:
    def __init__(self,parent,user_id):
        self.user_id = user_id
        self.win = tk.Toplevel(parent)
        self.win.title(f"News of User ID {user_id}")
        self.win.geometry("800x400")
        self.setup_ui()
        self.load_news()

    def setup_ui(self):
        cols = ("news_id","title","body","created_at")
        self.tree = ttk.Treeview(self.win, columns=cols, show="headings")
        for c in cols: self.tree.heading(c,text=c.upper() if c=="news_id" else c.capitalize()); self.tree.column(c,width=150)
        self.tree.pack(fill="both",expand=True,padx=10,pady=10)

    def run_query(self,q,params=(),fetch=False):
        conn = get_connection(); cur = conn.cursor()
        cur.execute(q,params)
        if fetch:
            rows = cur.fetchall(); conn.close(); return rows
        conn.commit(); conn.close()

    def load_news(self):
        q = """SELECT news_id,title,body,created_at FROM news WHERE user_id=%s"""
        rows = self.run_query(q,(self.user_id,),fetch=True)
        self.tree.delete(*self.tree.get_children())
        for r in rows: self.tree.insert("", "end", values=r)
