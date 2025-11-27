import tkinter as tk
from user_module import UserModule
from news_module import NewsModule

class App:
    def __init__(self, root):
        self.root = root
        self.root.withdraw()  # Hide root window
        self.open_dashboard()

    def open_dashboard(self):
        dash = tk.Toplevel(self.root)
        dash.title("News Blog Management System")
        dash.geometry("500x300")
        dash.configure(bg="#e6f0ff")

        header = tk.Frame(dash, bg="#003366", height=50)
        header.pack(fill="x")
        tk.Label(header, text="News Blog Management System", bg="#003366", fg="white",
                 font=("Arial",14,"bold")).pack(pady=8)

        btns = [
            ("Manage Users", lambda: UserModule(dash)),
            ("Manage News", lambda: NewsModule(dash)),
        ]
        frm = tk.Frame(dash, bg="#e6f0ff", pady=20)
        frm.pack(expand=True)
        for i,(txt, cmd) in enumerate(btns):
            tk.Button(frm, text=txt, width=20, bg="#0059b3", fg="white", command=cmd)\
              .grid(row=i, column=0, padx=10, pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
