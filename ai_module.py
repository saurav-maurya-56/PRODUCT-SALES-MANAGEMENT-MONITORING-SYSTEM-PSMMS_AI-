import requests
import pandas as pd
from database import execute_query

# --- Ollama Configuration ---
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "qwen2:1.5b"  # ✅ lightweight, stable, recommended for laptops


# === Utility: Send prompt to Ollama ===
def _ollama_request(prompt: str) -> str:
    """
    Sends a text prompt to Ollama model and returns its response.
    Handles connection, model, and memory errors gracefully.
    """
    try:
        response = requests.post(
            OLLAMA_URL,
            json={"model": MODEL, "prompt": prompt, "stream": False},
            timeout=90
        )
        if response.status_code == 200:
            data = response.json()
            return data.get("response", "").strip() or "(no response from AI)"
        elif response.status_code == 404:
            return "[AI ERROR]: Model not found. Run 'ollama pull qwen2:1.5b'"
        elif response.status_code == 500:
            return "[AI ERROR]: Model failed to load. Not enough memory."
        else:
            return f"[AI ERROR {response.status_code}]: {response.text}"
    except requests.exceptions.ConnectionError:
        return "[AI ERROR]: Ollama is not running. Please start it with 'ollama serve'."
    except Exception as e:
        return f"[AI ERROR]: {e}"


# === AI Sales Analysis ===
def analyze_sales_data():
    """
    Uses Ollama to analyze sales performance and generate insights.
    Works with qwen2:1.5b (lightweight model).
    """
    try:
        sales = execute_query("SELECT * FROM sales")
        products = execute_query("SELECT * FROM products")
        customers = execute_query("SELECT * FROM customers")

        if not sales:
            return "No sales data found to analyze."

        df = pd.DataFrame(sales)
        dfp = pd.DataFrame(products)

        # Merge product info
        if "product_id" in df.columns and "id" in dfp.columns:
            df = df.merge(dfp, left_on="product_id", right_on="id", how="left")

        df["amount"] = pd.to_numeric(df.get("amount", 0), errors="coerce").fillna(0)
        total_sales = df["amount"].sum()
        avg_sale = df["amount"].mean()
        top_product = df["name"].value_counts().idxmax() if "name" in df.columns else "N/A"

        # Build prompt for AI summary
        prompt = (
            f"You are a business analytics assistant.\n"
            f"Here is the sales summary data:\n"
            f"- Total Sales: {total_sales}\n"
            f"- Average Sale: {avg_sale}\n"
            f"- Top Product: {top_product}\n\n"
            f"Write a short report summarizing sales performance and key opportunities."
        )

        ai_response = _ollama_request(prompt)
        return ai_response

    except Exception as e:
        return f"[AI ERROR]: {e}"


# === AI Chat ===
def chat_with_ai(user_message: str) -> str:
    """
    Handles free-form chat with the Ollama model.
    This lets users ask questions about sales, customers, or general business.
    """
    if not user_message.strip():
        return "Please type a message first."

    # Build prompt
    prompt = (
        "You are a helpful AI business assistant for a Product Sales Management System.\n"
        "Answer in a friendly, clear, and professional tone.\n"
        "If the question is about sales, products, or customers, reason it generally.\n"
        f"User: {user_message}\n"
        "AI:"
    )

    return _ollama_request(prompt)
