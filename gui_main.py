import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import filedialog
from tkcalendar import DateEntry
from datetime import date
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Project modules
from database import execute_query, init_db
from export_data import export_to_csv, export_to_txt
from sample_data import insert_sample_data
from ai_module import analyze_sales_data, chat_with_ai


class PSMMSApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PSMMS-AI | Product Sales Management System")
        self.geometry("1180x720")
        self.configure(bg="#1e1e2f")
        self.resizable(False, False)

        # Sidebar + Main area
        self.sidebar = tk.Frame(self, bg="#25253a", width=230)
        self.sidebar.pack(side="left", fill="y")
        self.main = tk.Frame(self, bg="#f5f5f5")
        self.main.pack(side="right", fill="both", expand=True)

        # Brand
        tk.Label(self.sidebar, text="📦  PSMMS-AI", fg="#00e0ff", bg="#25253a",
                 font=("Segoe UI", 16, "bold"), anchor="w", padx=16).pack(fill="x", pady=(14, 8))

        # Sidebar buttons
        self._side_button("🏠  Dashboard", self.show_home)
        self._side_button("🏷️  Products", self.show_products)
        self._side_button("👥  Customers", self.show_customers)
        self._side_button("💰  Sales", self.show_sales)
        self._side_button("📦  Import / Export", self.show_export_import)
        self._side_button("📊  Charts / Reports", self.show_reports)
        self._side_button("🤖  AI Insights", self.show_ai_insights)
        self._side_button("💬  Chat with AI", self.show_ai_chat)
        self._side_button("🧩  Load Sample Data", self.load_samples)
        self._side_button("🚪  Exit", self.quit)

        # Title + content area
        self.title_label = tk.Label(self.main, text="Welcome to PSMMS-AI Dashboard",
                                    fg="#1e1e2f", bg="#f5f5f5", font=("Segoe UI", 20, "bold"))
        self.title_label.pack(pady=16, anchor="w", padx=18)
        self.content = tk.Frame(self.main, bg="#f5f5f5")
        self.content.pack(fill="both", expand=True)

        self.show_home()

    # ---------- helpers ----------
    def _side_button(self, text, cmd):
        btn = tk.Button(self.sidebar, text=text, command=cmd,
                        bg="#25253a", fg="white", bd=0, anchor="w", padx=16, pady=10,
                        activebackground="#323253", activeforeground="cyan",
                        font=("Segoe UI", 11, "bold"))
        btn.pack(fill="x", pady=3)

    def clear_content(self):
        for w in self.content.winfo_children():
            w.destroy()

    def set_title(self, text):
        self.title_label.config(text=text)

    # ---------- Home ----------
    def show_home(self):
        self.clear_content()
        self.set_title("📊 Dashboard")

        # Quick stats
        try:
            prod_count = len(execute_query("SELECT id FROM products"))
            cust_count = len(execute_query("SELECT id FROM customers"))
            sales_count = len(execute_query("SELECT id FROM sales"))
            total_rev_row = execute_query("SELECT SUM(amount) AS total FROM sales")
            total_rev = float(total_rev_row[0].get("total") or 0.0)
        except Exception:
            prod_count = cust_count = sales_count = 0
            total_rev = 0.0

        wrap = tk.Frame(self.content, bg="#f5f5f5")
        wrap.pack(padx=18, pady=10, anchor="w")

        def card(parent, title, value):
            c = tk.Frame(parent, bg="white")
            c.pack(side="left", padx=10)
            tk.Label(c, text=title, bg="white", fg="#444", font=("Segoe UI", 10)).pack(padx=14, pady=(10, 0), anchor="w")
            tk.Label(c, text=value, bg="white", fg="#111", font=("Segoe UI", 18, "bold")).pack(padx=14, pady=(0, 12), anchor="w")

        card(wrap, "Products", prod_count)
        card(wrap, "Customers", cust_count)
        card(wrap, "Sales", sales_count)
        card(wrap, "Total Revenue", f"₹{total_rev:,.2f}")

        tk.Label(self.content, text="Use the sidebar to manage data, export, view charts, or chat with AI.",
                 bg="#f5f5f5", fg="#333", font=("Segoe UI", 11)).pack(padx=18, pady=6, anchor="w")

    # ---------- Products ----------
    def show_products(self):
        self.clear_content()
        self.set_title("🏷️ Manage Products")

        form = tk.Frame(self.content, bg="#f5f5f5"); form.pack(padx=18, pady=(10, 6), anchor="w")
        tk.Label(form, text="Name:", bg="#f5f5f5").grid(row=0, column=0, padx=6, pady=4, sticky="e")
        tk.Label(form, text="Category:", bg="#f5f5f5").grid(row=0, column=2, padx=6, pady=4, sticky="e")
        tk.Label(form, text="Price:", bg="#f5f5f5").grid(row=0, column=4, padx=6, pady=4, sticky="e")

        name = tk.Entry(form, width=22); name.grid(row=0, column=1, padx=6)
        cat = tk.Entry(form, width=18); cat.grid(row=0, column=3, padx=6)
        price = tk.Entry(form, width=12); price.grid(row=0, column=5, padx=6)

        btns = tk.Frame(self.content, bg="#f5f5f5"); btns.pack(padx=18, pady=6, anchor="w")

        cols = ("ID", "Name", "Category", "Price")
        tree = ttk.Treeview(self.content, columns=cols, show="headings", height=16)
        for c in cols:
            tree.heading(c, text=c); tree.column(c, width=150, anchor="w")
        tree.pack(fill="both", expand=True, padx=18, pady=10)

        def refresh():
            tree.delete(*tree.get_children())
            rows = execute_query("SELECT id, name, category, price FROM products")
            for r in rows:
                tree.insert("", "end", values=(r["id"], r["name"], r.get("category", ""), r["price"]))

        def add():
            if not name.get() or not price.get():
                return messagebox.showerror("Validation", "Name and Price are required.")
            execute_query("INSERT INTO products (name, category, price) VALUES (%s,%s,%s)",
                          (name.get(), cat.get(), price.get()), commit=True)
            name.delete(0,"end"); cat.delete(0,"end"); price.delete(0,"end")
            refresh()

        def update():
            sel = tree.selection()
            if not sel: return
            pid = tree.item(sel[0])["values"][0]
            execute_query("UPDATE products SET name=%s, category=%s, price=%s WHERE id=%s",
                          (name.get(), cat.get(), price.get(), pid), commit=True)
            refresh()

        def delete():
            sel = tree.selection()
            if not sel: return
            pid = tree.item(sel[0])["values"][0]
            if messagebox.askyesno("Confirm", f"Delete product ID {pid}?"):
                execute_query("DELETE FROM products WHERE id=%s", (pid,), commit=True)
                refresh()

        tk.Button(btns, text="Add", command=add, bg="#3b3b5c", fg="white").pack(side="left", padx=6)
        tk.Button(btns, text="Update", command=update, bg="#3b3b5c", fg="white").pack(side="left", padx=6)
        tk.Button(btns, text="Delete", command=delete, bg="#ff6b6b", fg="white").pack(side="left", padx=6)
        tk.Button(btns, text="Refresh", command=refresh, bg="#2e8b57", fg="white").pack(side="left", padx=6)

        refresh()

    # ---------- Customers ----------
    def show_customers(self):
        self.clear_content()
        self.set_title("👥 Manage Customers")

        form = tk.Frame(self.content, bg="#f5f5f5"); form.pack(padx=18, pady=(10, 6), anchor="w")
        tk.Label(form, text="Name:", bg="#f5f5f5").grid(row=0, column=0, padx=6, pady=4, sticky="e")
        tk.Label(form, text="Email:", bg="#f5f5f5").grid(row=0, column=2, padx=6, pady=4, sticky="e")
        tk.Label(form, text="Phone:", bg="#f5f5f5").grid(row=0, column=4, padx=6, pady=4, sticky="e")

        name = tk.Entry(form, width=22); name.grid(row=0, column=1, padx=6)
        email = tk.Entry(form, width=22); email.grid(row=0, column=3, padx=6)
        phone = tk.Entry(form, width=16); phone.grid(row=0, column=5, padx=6)

        btns = tk.Frame(self.content, bg="#f5f5f5"); btns.pack(padx=18, pady=6, anchor="w")

        cols = ("ID", "Name", "Email", "Phone")
        tree = ttk.Treeview(self.content, columns=cols, show="headings", height=16)
        for c in cols:
            tree.heading(c, text=c); tree.column(c, width=170, anchor="w")
        tree.pack(fill="both", expand=True, padx=18, pady=10)

        def refresh():
            tree.delete(*tree.get_children())
            rows = execute_query("SELECT id, name, email, phone FROM customers")
            for r in rows:
                tree.insert("", "end", values=(r["id"], r["name"], r.get("email",""), r.get("phone","")))

        def add():
            if not name.get():
                return messagebox.showerror("Validation", "Name is required.")
            execute_query("INSERT INTO customers (name, email, phone) VALUES (%s,%s,%s)",
                          (name.get(), email.get(), phone.get()), commit=True)
            name.delete(0,"end"); email.delete(0,"end"); phone.delete(0,"end")
            refresh()

        def update():
            sel = tree.selection()
            if not sel: return
            cid = tree.item(sel[0])["values"][0]
            execute_query("UPDATE customers SET name=%s, email=%s, phone=%s WHERE id=%s",
                          (name.get(), email.get(), phone.get(), cid), commit=True)
            refresh()

        def delete():
            sel = tree.selection()
            if not sel: return
            cid = tree.item(sel[0])["values"][0]
            if messagebox.askyesno("Confirm", f"Delete customer ID {cid}?"):
                execute_query("DELETE FROM customers WHERE id=%s", (cid,), commit=True)
                refresh()

        tk.Button(btns, text="Add", command=add, bg="#3b3b5c", fg="white").pack(side="left", padx=6)
        tk.Button(btns, text="Update", command=update, bg="#3b3b5c", fg="white").pack(side="left", padx=6)
        tk.Button(btns, text="Delete", command=delete, bg="#ff6b6b", fg="white").pack(side="left", padx=6)
        tk.Button(btns, text="Refresh", command=refresh, bg="#2e8b57", fg="white").pack(side="left", padx=6)

        refresh()

    # ---------- Sales (with Date) ----------
    def show_sales(self):
        self.clear_content()
        self.set_title("💰 Manage Sales")

        form = tk.Frame(self.content, bg="#f5f5f5"); form.pack(padx=18, pady=(10, 6), anchor="w")
        tk.Label(form, text="Product ID:", bg="#f5f5f5").grid(row=0, column=0, padx=6, pady=4, sticky="e")
        tk.Label(form, text="Customer ID:", bg="#f5f5f5").grid(row=0, column=2, padx=6, pady=4, sticky="e")
        tk.Label(form, text="Amount:", bg="#f5f5f5").grid(row=0, column=4, padx=6, pady=4, sticky="e")
        tk.Label(form, text="Sale Date:", bg="#f5f5f5").grid(row=0, column=6, padx=6, pady=4, sticky="e")

        pid = tk.Entry(form, width=10); pid.grid(row=0, column=1, padx=6)
        cid = tk.Entry(form, width=10); cid.grid(row=0, column=3, padx=6)
        amt = tk.Entry(form, width=12); amt.grid(row=0, column=5, padx=6)
        sdate = DateEntry(form, width=12, background="darkblue", foreground="white",
                          borderwidth=2, year=date.today().year, month=date.today().month,
                          day=date.today().day, date_pattern='yyyy-mm-dd')
        sdate.grid(row=0, column=7, padx=6)

        btns = tk.Frame(self.content, bg="#f5f5f5"); btns.pack(padx=18, pady=6, anchor="w")

        cols = ("ID", "Product", "Customer", "Date", "Amount")
        tree = ttk.Treeview(self.content, columns=cols, show="headings", height=16)
        for c in cols:
            tree.heading(c, text=c); tree.column(c, width=160 if c!="Amount" else 120, anchor="w")
        tree.pack(fill="both", expand=True, padx=18, pady=10)

        def refresh():
            tree.delete(*tree.get_children())
            rows = execute_query("""
                SELECT s.id, p.name AS product, c.name AS customer, s.sale_date, s.amount
                FROM sales s
                JOIN products p ON s.product_id = p.id
                JOIN customers c ON s.customer_id = c.id
                ORDER BY s.sale_date DESC, s.id DESC
            """)
            for r in rows:
                tree.insert("", "end", values=(r["id"], r["product"], r["customer"], str(r["sale_date"]), r["amount"]))

        def add():
            if not (pid.get() and cid.get() and amt.get()):
                return messagebox.showerror("Validation", "Product ID, Customer ID, and Amount are required.")
            execute_query("INSERT INTO sales (product_id, customer_id, sale_date, amount) VALUES (%s,%s,%s,%s)",
                          (pid.get(), cid.get(), sdate.get(), amt.get()), commit=True)
            pid.delete(0,"end"); cid.delete(0,"end"); amt.delete(0,"end")
            refresh()

        def delete():
            sel = tree.selection()
            if not sel: return
            sid = tree.item(sel[0])["values"][0]
            if messagebox.askyesno("Confirm", f"Delete sale ID {sid}?"):
                execute_query("DELETE FROM sales WHERE id=%s", (sid,), commit=True)
                refresh()

        tk.Button(btns, text="Add", command=add, bg="#3b3b5c", fg="white").pack(side="left", padx=6)
        tk.Button(btns, text="Delete", command=delete, bg="#ff6b6b", fg="white").pack(side="left", padx=6)
        tk.Button(btns, text="Refresh", command=refresh, bg="#2e8b57", fg="white").pack(side="left", padx=6)

        refresh()

    # ---------- Import / Export ----------
    def show_export_import(self):
        self.clear_content()
        self.set_title("📦 Import / Export")

        tk.Label(self.content, text="Export your database tables to CSV or TXT.",
                 bg="#f5f5f5", fg="#333", font=("Segoe UI", 11)).pack(padx=18, pady=(10, 2), anchor="w")

        tk.Button(self.content, text="Export to CSV", command=export_to_csv,
                  bg="#3b3b5c", fg="white", padx=12).pack(padx=18, pady=8, anchor="w")
        tk.Button(self.content, text="Export to TXT", command=export_to_txt,
                  bg="#3b3b5c", fg="white", padx=12).pack(padx=18, pady=8, anchor="w")

           # ---------- Reports / Charts ----------
    def show_reports(self):
        self.clear_content()
        self.set_title("📊 Sales Charts & Reports")

        import matplotlib.pyplot as plt
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        import pandas as pd

        # --- Fetch data from DB ---
        try:
            sales = execute_query("SELECT * FROM sales")
            products = execute_query("SELECT * FROM products")
        except Exception as e:
            tk.Label(
                self.content,
                text=f"[Database Error]: {e}",
                bg="#f5f5f5",
                fg="red",
                font=("Segoe UI", 12)
            ).pack(pady=20)
            return

        if not sales or not products:
            tk.Label(
                self.content,
                text="No sales or products found.\nPlease add some data or use 'Load Sample Data'.",
                bg="#f5f5f5",
                fg="#555",
                font=("Segoe UI", 12)
            ).pack(pady=20)
            return

        # --- Prepare data ---
        df_sales = pd.DataFrame(sales)
        df_products = pd.DataFrame(products)

        # Merge for product/category names
        df = df_sales.merge(df_products, left_on="product_id", right_on="id", how="left")

        # Convert types
        df["amount"] = pd.to_numeric(df.get("amount", 0), errors="coerce").fillna(0)
        df["sale_date"] = pd.to_datetime(df.get("sale_date"), errors="coerce")

        # Scrollable wrapper
        wrapper = tk.Frame(self.content, bg="#f5f5f5")
        wrapper.pack(fill="both", expand=True, padx=20, pady=10)

        # 1️⃣ --- Sales by Product ---
        prod_summary = df.groupby("name")["amount"].sum().sort_values(ascending=False)
        if not prod_summary.empty:
            fig1, ax1 = plt.subplots(figsize=(6, 4))
            prod_summary.plot(kind="bar", ax=ax1, color="#0078D4")
            ax1.set_title("Sales by Product", fontsize=12)
            ax1.set_ylabel("Amount")
            ax1.set_xlabel("Product")
            ax1.tick_params(axis="x", rotation=45)
            plt.tight_layout()

            canvas1 = FigureCanvasTkAgg(fig1, master=wrapper)
            canvas1.draw()
            canvas1.get_tk_widget().pack(pady=10)

        # 2️⃣ --- Sales by Category ---
        if "category" in df.columns:
            cat_summary = df.groupby("category")["amount"].sum().sort_values(ascending=False)
            if not cat_summary.empty:
                fig2, ax2 = plt.subplots(figsize=(6, 4))
                cat_summary.plot(kind="bar", color="#4CAF50", ax=ax2)
                ax2.set_title("Sales by Category", fontsize=12)
                ax2.set_ylabel("Amount")
                ax2.set_xlabel("Category")
                ax2.tick_params(axis="x", rotation=45)
                plt.tight_layout()

                canvas2 = FigureCanvasTkAgg(fig2, master=wrapper)
                canvas2.draw()
                canvas2.get_tk_widget().pack(pady=10)

        # 3️⃣ --- Sales Trend (by Date) ---
        if "sale_date" in df.columns:
            daily_sales = df.groupby("sale_date")["amount"].sum().sort_index()
            if not daily_sales.empty:
                fig3, ax3 = plt.subplots(figsize=(6, 4))
                daily_sales.plot(kind="line", marker="o", color="#FF9800", ax=ax3)
                ax3.set_title("Sales Trend Over Time", fontsize=12)
                ax3.set_ylabel("Amount")
                ax3.set_xlabel("Date")
                fig3.autofmt_xdate()
                plt.tight_layout()

                canvas3 = FigureCanvasTkAgg(fig3, master=wrapper)
                canvas3.draw()
                canvas3.get_tk_widget().pack(pady=10)

        # --- Summary Label ---
        total_sales = df["amount"].sum()
        total_label = tk.Label(
            wrapper,
            text=f"💰 Total Revenue: ₹{total_sales:,.2f}",
            font=("Segoe UI", 13, "bold"),
            bg="#f5f5f5",
            fg="#1e1e2f"
        )
        total_label.pack(pady=20)



    # ---------- AI Insights ----------
    def show_ai_insights(self):
        self.clear_content()
        self.set_title("🤖 AI Insights")

        txt = tk.Text(self.content, wrap="word", font=("Consolas", 11), bg="white", fg="#111")
        txt.pack(fill="both", expand=True, padx=18, pady=10)
        txt.insert("end", "Analyzing with AI (Ollama)…\n\n"); txt.see("end"); self.update()

        try:
            result = analyze_sales_data()
            txt.insert("end", result)
        except Exception as e:
            txt.insert("end", f"[ERROR] {e}")
     # ---------- Chat with AI ----------
    def show_ai_chat(self):
        self.clear_content()
        self.set_title("💬 Chat with AI (qwen2:1.5b)")

        # Wrapper frame (everything inside)
        wrapper = tk.Frame(self.content, bg="#f5f5f5")
        wrapper.pack(fill="both", expand=True, padx=15, pady=10)

        # --- Scrollable Chat Box ---
        chat_frame = tk.Frame(wrapper, bg="#f5f5f5")
        chat_frame.pack(fill="both", expand=True)

        self.chat_scroll = tk.Scrollbar(chat_frame)
        self.chat_scroll.pack(side="right", fill="y")

        self.chat_box = tk.Text(
            chat_frame,
            wrap="word",
            font=("Segoe UI", 11),
            bg="#ffffff",
            fg="#000000",
            yscrollcommand=self.chat_scroll.set,
            height=20,  # slightly smaller height to fit on screen
            state="normal",
        )
        self.chat_box.pack(fill="both", expand=True)
        self.chat_scroll.config(command=self.chat_box.yview)

        # Initial greeting
        self.chat_box.insert(
            "end",
            "AI: 👋 Hi! I’m your business assistant. Ask me anything about your sales, products, or customers.\n\n",
        )
        self.chat_box.config(state="disabled")

        # --- Fixed Input Bar at Bottom ---
        input_bar = tk.Frame(wrapper, bg="#f5f5f5")
        input_bar.pack(fill="x", pady=(10, 5))

        self.user_input = tk.Entry(
            input_bar,
            font=("Segoe UI", 12),
            bg="#ffffff",
            fg="#000000",
        )
        self.user_input.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.user_input.focus_set()

        send_btn = tk.Button(
            input_bar,
            text="Send",
            bg="#0078D4",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            width=10,
            height=1,
            command=self._send_message,
        )
        send_btn.pack(side="right")

        # Press Enter to send
        self.user_input.bind("<Return>", lambda e: self._send_message())

    # --- helper function for sending message ---
    def _send_message(self):
        msg = self.user_input.get().strip()
        if not msg:
            return

        # Display user message
        self.chat_box.config(state="normal")
        self.chat_box.insert("end", f"You: {msg}\n")
        self.chat_box.insert("end", "AI: Thinking...\n")
        self.chat_box.config(state="disabled")
        self.chat_box.see("end")

        self.user_input.delete(0, "end")
        self.user_input.focus_set()
        self.update()

        # --- AI reply logic ---
        try:
            from ai_module import chat_with_ai
            reply = chat_with_ai(msg)
        except Exception as e:
            reply = f"[AI ERROR]: {e}"

        # Display AI reply
        self.chat_box.config(state="normal")
        self.chat_box.delete("end-2l linestart", "end-1l lineend")
        self.chat_box.insert("end", f"AI: {reply}\n\n")
        self.chat_box.config(state="disabled")
        self.chat_box.see("end")


    # ---------- Load sample data ----------
    def load_samples(self):
        insert_sample_data()
        messagebox.showinfo("Sample Data", "Sample data loaded. You can now use Products/Sales/Reports.")

# -------- helpers for charts --------
import os
def os_path_exists(p): 
    try: return os.path.exists(p)
    except: return False

def draw_charts(csv_path):
    try:
        df = pd.read_csv(csv_path)
        df.columns = [c.lower().strip() for c in df.columns]
        if "sale_date" not in df.columns or "amount" not in df.columns:
            messagebox.showwarning("Charts", "CSV must include 'sale_date' and 'amount' columns.")
            return
        df["sale_date"] = pd.to_datetime(df["sale_date"], errors="coerce")
        df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0)

        # Daily totals
        daily = df.groupby(df["sale_date"].dt.date)["amount"].sum()

        # Top 5 products (if product/name exists)
        if "product" in df.columns:
            by_prod = df.groupby("product")["amount"].sum().sort_values(ascending=False).head(5)
        elif "name" in df.columns:
            by_prod = df.groupby("name")["amount"].sum().sort_values(ascending=False).head(5)
        else:
            by_prod = None

        # Plot daily bar
        fig1, ax1 = plt.subplots(figsize=(8, 3.6))
        daily.plot(kind="bar", ax=ax1, title="Daily Sales")
        plt.tight_layout()
        app._plot_embed(fig1)

        # Plot top products
        if by_prod is not None:
            fig2, ax2 = plt.subplots(figsize=(8, 3.6))
            by_prod.plot(kind="bar", ax=ax2, title="Top 5 Products by Revenue")
            plt.tight_layout()
            app._plot_embed(fig2)

    except Exception as e:
        messagebox.showerror("Charts", f"Failed to draw charts: {e}")


if __name__ == "__main__":
    init_db()
    app = PSMMSApp()
    app.mainloop()

