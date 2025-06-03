import sqlite3
import gradio as gr
import matplotlib.pyplot as plt
import io
import base64

# Database setup with check_same_thread=False for Gradio’s multithreading
conn = sqlite3.connect('customer_data.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        phone TEXT,
        email TEXT,
        status TEXT
    )
''')
conn.commit()

# CRUD functions with basic input checks
def add_customer(name, phone, email, status):
    if not name or not phone or not email or not status:
        return "⚠️ Please fill in all fields."
    cursor.execute('INSERT INTO customers (name, phone, email, status) VALUES (?, ?, ?, ?)',
                   (name, phone, email, status))
    conn.commit()
    return f"✅ Customer '{name}' added successfully."

def update_customer(id, name, phone, email, status):
    if not id or not name or not phone or not email or not status:
        return "⚠️ Please fill in all fields."
    cursor.execute('UPDATE customers SET name=?, phone=?, email=?, status=? WHERE id=?',
                   (name, phone, email, status, id))
    conn.commit()
    return f"✅ Customer with ID {id} updated successfully."

def delete_customer(id):
    if not id:
        return "⚠️ Please provide the customer ID."
    cursor.execute('DELETE FROM customers WHERE id=?', (id,))
    conn.commit()
    return f"🗑️ Customer with ID {id} deleted successfully."

def search_customer(query):
    if not query:
        return "⚠️ Please enter a search query."
    cursor.execute('SELECT * FROM customers WHERE name LIKE ? OR phone LIKE ? OR email LIKE ? OR status LIKE ?',
                   (f'%{query}%', f'%{query}%', f'%{query}%', f'%{query}%'))
    data = cursor.fetchall()
    if data:
        result = "🔍 Search Results:\n\n"
        for row in data:
            result += f"ID: {row[0]} | Name: {row[1]} | Phone: {row[2]} | Email: {row[3]} | Status: {row[4]}\n"
        return result
    else:
        return "❌ No matching records found."

# Data visualization
def plot_status_pie():
    cursor.execute("SELECT status, COUNT(*) FROM customers GROUP BY status")
    data = cursor.fetchall()

    if not data:
        return "❌ No data available to visualize."

    statuses = [row[0] for row in data]
    counts = [row[1] for row in data]

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie(counts, labels=statuses, autopct='%1.1f%%', startangle=90, colors=['#00cc66', '#ffcc00', '#ff3300'])
    ax.set_title("Customer Status Distribution")

    # Save plot to a buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()
    plt.close(fig)

    return f'<img src="data:image/png;base64,{img_base64}"/>'

# Gradio UI
with gr.Blocks() as demo:
    gr.Markdown("## 📇 Customer Management System with Visualization")

    with gr.Tab("➕ Add Customer"):
        with gr.Row():
            name = gr.Textbox(label="Name")
            phone = gr.Textbox(label="Phone")
            email = gr.Textbox(label="Email")
            status = gr.Dropdown(choices=["Active", "Inactive", "Banned"], label="Status")
        add_btn = gr.Button("Add Customer")
        add_output = gr.Textbox(label="Status")
        add_btn.click(fn=add_customer, inputs=[name, phone, email, status], outputs=add_output)

    with gr.Tab("✏️ Update Customer"):
        with gr.Row():
            update_id = gr.Number(label="Customer ID", precision=0)
            update_name = gr.Textbox(label="Name")
            update_phone = gr.Textbox(label="Phone")
            update_email = gr.Textbox(label="Email")
            update_status = gr.Dropdown(choices=["Active", "Inactive", "Banned"], label="Status")
        update_btn = gr.Button("Update Customer")
        update_output = gr.Textbox(label="Status")
        update_btn.click(fn=update_customer, inputs=[update_id, update_name, update_phone, update_email, update_status], outputs=update_output)

    with gr.Tab("🗑️ Delete Customer"):
        delete_id = gr.Number(label="Customer ID", precision=0)
        delete_btn = gr.Button("Delete Customer")
        delete_output = gr.Textbox(label="Status")
        delete_btn.click(fn=delete_customer, inputs=delete_id, outputs=delete_output)

    with gr.Tab("🔎 Search Customer"):
        search_query = gr.Textbox(label="Search Query")
        search_btn = gr.Button("Search")
        search_output = gr.Textbox(label="Results", lines=10)
        search_btn.click(fn=search_customer, inputs=search_query, outputs=search_output)

    with gr.Tab("📊 Data Visualization"):
        plot_btn = gr.Button("📈 Show Customer Status Pie Chart")
        plot_output = gr.HTML(label="📊 Pie Chart Visualization")
        plot_btn.click(fn=plot_status_pie, inputs=None, outputs=plot_output)

demo.launch()
