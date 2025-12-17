import pandas as pd
from tkinter import filedialog, messagebox
from database import execute_query

# === Export to CSV ===
def export_to_csv():
    try:
        # Fetch data from database
        products = execute_query("SELECT * FROM products")
        customers = execute_query("SELECT * FROM customers")
        sales = execute_query("SELECT * FROM sales")

        # Convert to DataFrames
        df_products = pd.DataFrame(products)
        df_customers = pd.DataFrame(customers)
        df_sales = pd.DataFrame(sales)

        # Ask user for save location
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv")],
            title="Save data as CSV"
        )

        if not file_path:
            return

        # Write all to single CSV with separators
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("=== PRODUCTS ===\n")
            df_products.to_csv(f, index=False)
            f.write("\n\n=== CUSTOMERS ===\n")
            df_customers.to_csv(f, index=False)
            f.write("\n\n=== SALES ===\n")
            df_sales.to_csv(f, index=False)

        messagebox.showinfo("Success", f"Data exported successfully to:\n{file_path}")
    except Exception as e:
        messagebox.showerror("Export Error", f"Failed to export CSV: {e}")

# === Export to TXT ===
def export_to_txt():
    try:
        products = execute_query("SELECT * FROM products")
        customers = execute_query("SELECT * FROM customers")
        sales = execute_query("SELECT * FROM sales")

        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt")],
            title="Save data as TXT"
        )

        if not file_path:
            return

        with open(file_path, "w", encoding="utf-8") as f:
            f.write("PRODUCTS:\n")
            for p in products:
                f.write(f"{p}\n")
            f.write("\nCUSTOMERS:\n")
            for c in customers:
                f.write(f"{c}\n")
            f.write("\nSALES:\n")
            for s in sales:
                f.write(f"{s}\n")

        messagebox.showinfo("Success", f"Data exported successfully to:\n{file_path}")
    except Exception as e:
        messagebox.showerror("Export Error", f"Failed to export TXT: {e}")
