
import streamlit as st
import sqlite3
import pandas as pd
from datetime import date, datetime
from pathlib import Path
from io import BytesIO

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

# =============== PAGE CONFIG ===============

st.set_page_config(
    page_title="Pharmacy Management System",
    page_icon="💊",
    layout="wide"
)

DB = "database/pharmacy_complete.db"
Path("database").mkdir(exist_ok=True)

# =============== DATABASE ===============

def connect():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    return con


def add_missing_columns(con, table, columns):
    existing = {
        row["name"]
        for row in con.execute(
            f"PRAGMA table_info({table})"
        ).fetchall()
    }

    for column, definition in columns.items():
        if column not in existing:
            con.execute(
                f"ALTER TABLE {table} ADD COLUMN {column} {definition}"
            )


def setup_database():
    with connect() as con:

        con.execute("""
            CREATE TABLE IF NOT EXISTS medicines(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                category TEXT,
                batch TEXT,
                quantity INTEGER DEFAULT 0,
                price REAL DEFAULT 0,
                expiry TEXT,
                supplier TEXT
            )
        """)

        con.execute("""
            CREATE TABLE IF NOT EXISTS customers(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                phone TEXT,
                address TEXT
            )
        """)

        con.execute("""
            CREATE TABLE IF NOT EXISTS sales(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice TEXT,
                customer TEXT,
                medicine TEXT,
                quantity INTEGER,
                price REAL,
                total REAL,
                sale_date TEXT
            )
        """)

        add_missing_columns(con, "medicines", {
            "name": "TEXT",
            "category": "TEXT",
            "batch": "TEXT",
            "quantity": "INTEGER DEFAULT 0",
            "price": "REAL DEFAULT 0",
            "expiry": "TEXT",
            "supplier": "TEXT"
        })

        add_missing_columns(con, "customers", {
            "name": "TEXT",
            "phone": "TEXT",
            "address": "TEXT"
        })

        add_missing_columns(con, "sales", {
            "invoice": "TEXT",
            "customer": "TEXT",
            "medicine": "TEXT",
            "quantity": "INTEGER DEFAULT 0",
            "price": "REAL DEFAULT 0",
            "total": "REAL DEFAULT 0",
            "sale_date": "TEXT"
        })

        con.commit()


setup_database()


def read_data(query, params=()):
    with connect() as con:
        return pd.read_sql_query(query, con, params=params)


def rupees(value):
    return f"₹{float(value):,.2f}"


# =============== DESIGN ===============

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', 'Segoe UI', sans-serif;
    font-size: 13px;
}

.stApp {
    background: #f3f6fa;
    color: #18324d;
}

.block-container {
    max-width: 1050px;
    padding-top: 12px;
    padding-bottom: 18px;
}

h1 {
    font-size: 25px !important;
    color: #17324d !important;
    font-weight: 800 !important;
}

h2 {
    font-size: 21px !important;
    color: #17324d !important;
}

h3 {
    font-size: 17px !important;
    color: #17324d !important;
}

.pharmacy-header {
    background: linear-gradient(120deg,#102a43,#176b87,#11998e);
    padding: 17px 12px;
    border-radius: 12px;
    text-align: center;
    margin-bottom: 17px;
}

.pharmacy-header h1 {
    color: white !important;
    font-size: 25px !important;
    margin: 0;
}

.pharmacy-header p {
    color: #e0f2f1;
    font-size: 12px;
    margin: 6px 0 0;
}

section[data-testid="stSidebar"] {
    background: #102a43;
}

section[data-testid="stSidebar"] * {
    color: white !important;
}

.login-heading {
    text-align: center;
    font-size: 25px;
    font-weight: 800;
    color: #17324d;
    margin: 8px 0 15px;
}

div[data-testid="stForm"] {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0 !important;
}

.stTextInput input,
.stNumberInput input,
.stDateInput input,
.stTextArea textarea {
    min-height: 34px !important;
    font-size: 13px !important;
    border: 1px solid #cbd8e5 !important;
    border-radius: 7px !important;
    background: white !important;
    color: #17324d !important;
}

.stButton > button,
.stFormSubmitButton > button,
.stDownloadButton > button {
    min-height: 35px;
    padding: 4px 13px;
    font-size: 13px;
    background: #087e8b;
    color: white !important;
    border: none;
    border-radius: 7px;
    font-weight: 700;
}

div[data-testid="stMetric"] {
    background: white;
    padding: 12px;
    border-radius: 10px;
    border-left: 4px solid #0d9488;
    box-shadow: 0 3px 10px rgba(0,0,0,.05);
}

div[data-testid="stMetricValue"] {
    font-size: 22px !important;
    color: #123b5d !important;
    font-weight: 800 !important;
}

hr {
    margin: 12px 0;
    border-color: #dbe6ef;
}
</style>
""", unsafe_allow_html=True)


# =============== HEADER ===============

def header():
    st.markdown("""
    <div class="pharmacy-header">
        <h1>💊 PHARMACY MANAGEMENT SYSTEM</h1>
        <p>Smart Medicine • Easy Billing • Inventory Management</p>
    </div>
    """, unsafe_allow_html=True)


# =============== LOGIN ===============

def login_page():
    header()

    st.markdown(
        '<div class="login-heading">Admin Login</div>',
        unsafe_allow_html=True
    )

    left, center, right = st.columns([1.5, 1.4, 1.5])

    with center:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            login = st.form_submit_button(
                "Login", use_container_width=True
            )

        if login:
            if username == "admin" and password == "admin123":
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Invalid Username or Password!")

        st.caption("Demo ID: admin | Password: admin123")


# =============== DASHBOARD ===============

def dashboard():
    st.title("📊 Dashboard")

    medicines = read_data("SELECT * FROM medicines")
    customers = read_data("SELECT * FROM customers")
    sales = read_data("SELECT * FROM sales")

    stock = int(medicines["quantity"].fillna(0).sum()) if not medicines.empty else 0
    products = len(medicines)
    customer_count = len(customers)

    today_total = 0
    revenue = 0

    if not sales.empty:
        sales["total"] = pd.to_numeric(sales["total"], errors="coerce").fillna(0)
        revenue = sales["total"].sum()
        today_total = sales[
            sales["sale_date"] == date.today().isoformat()
        ]["total"].sum()

    a, b, c, d = st.columns(4)
    a.metric("Total Stock", stock)
    b.metric("Products", products)
    c.metric("Customers", customer_count)
    d.metric("Today's Sales", rupees(today_total))

    e, f = st.columns(2)
    low = len(medicines[medicines["quantity"].fillna(0) <= 10]) if not medicines.empty else 0
    e.metric("Low Stock", low)
    f.metric("Total Revenue", rupees(revenue))

    st.subheader("⚠️ Low Stock Medicines")

    if not medicines.empty:
        low_df = medicines[medicines["quantity"].fillna(0) <= 10]
        if low_df.empty:
            st.success("All medicines have sufficient stock.")
        else:
            st.dataframe(
                low_df[["name", "category", "quantity", "expiry"]],
                use_container_width=True,
                hide_index=True
            )
    else:
        st.info("No medicines added yet.")


# =============== MEDICINES ===============

def medicine_management():
    st.title("💊 Medicine Management")

    tab1, tab2, tab3 = st.tabs([
        "Add Medicine", "View / Update", "Delete"
    ])

    with tab1:
        with st.form("add_medicine", clear_on_submit=True):
            c1, c2 = st.columns(2)
            name = c1.text_input("Medicine Name *")
            category = c2.text_input("Category")
            batch = c1.text_input("Batch Number")
            supplier = c2.text_input("Supplier")
            quantity = c1.number_input("Quantity", min_value=0, step=1)
            price = c2.number_input("Price", min_value=0.0, step=1.0)
            expiry = st.date_input("Expiry Date")
            save = st.form_submit_button("Add Medicine")

        if save:
            if not name.strip():
                st.error("Medicine name is required.")
            else:
                with connect() as con:
                    con.execute("""
                        INSERT INTO medicines
                        (name,category,batch,quantity,price,expiry,supplier)
                        VALUES(?,?,?,?,?,?,?)
                    """, (
                        name.strip(), category, batch, quantity,
                        price, expiry.isoformat(), supplier
                    ))
                    con.commit()
                st.success("Medicine added successfully!")
                st.rerun()

    with tab2:
        df = read_data("SELECT * FROM medicines ORDER BY id DESC")

        if df.empty:
            st.info("No medicines available.")
        else:
            st.dataframe(df, use_container_width=True, hide_index=True)

            selected = st.selectbox("Select Medicine ID", df["id"].tolist())
            item = df[df["id"] == selected].iloc[0]

            with st.form("update_medicine"):
                c1, c2 = st.columns(2)
                name = c1.text_input("Name", value=str(item["name"] or ""))
                category = c2.text_input("Category", value=str(item["category"] or ""))
                batch = c1.text_input("Batch", value=str(item["batch"] or ""))
                supplier = c2.text_input("Supplier", value=str(item["supplier"] or ""))
                quantity = c1.number_input(
                    "Quantity", min_value=0,
                    value=max(0, int(item["quantity"] or 0))
                )
                price = c2.number_input(
                    "Price", min_value=0.0,
                    value=max(0.0, float(item["price"] or 0))
                )

                try:
                    old_expiry = date.fromisoformat(str(item["expiry"]))
                except (ValueError, TypeError):
                    old_expiry = date.today()

                expiry = st.date_input("Expiry", value=old_expiry)
                update = st.form_submit_button("Update Medicine")

            if update:
                if not name.strip():
                    st.error("Medicine name is required.")
                else:
                    with connect() as con:
                        con.execute("""
                            UPDATE medicines
                            SET name=?,category=?,batch=?,quantity=?,
                                price=?,expiry=?,supplier=?
                            WHERE id=?
                        """, (
                            name.strip(), category, batch, quantity,
                            price, expiry.isoformat(), supplier, selected
                        ))
                        con.commit()
                    st.success("Medicine updated!")
                    st.rerun()

    with tab3:
        df = read_data("SELECT id,name FROM medicines")

        if df.empty:
            st.info("No medicines to delete.")
        else:
            selected = st.selectbox(
                "Select Medicine",
                df["id"].tolist(),
                format_func=lambda x:
                    f"{df[df.id == x].iloc[0]['name']} (ID {x})"
            )

            if st.button("Delete Medicine"):
                with connect() as con:
                    con.execute("DELETE FROM medicines WHERE id=?", (selected,))
                    con.commit()
                st.success("Medicine deleted.")
                st.rerun()


# =============== CUSTOMERS ===============

def customer_management():
    st.title("👥 Customer Management")

    with st.form("customer_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        name = c1.text_input("Customer Name *")
        phone = c2.text_input("Phone Number")
        address = st.text_area("Address")
        save = st.form_submit_button("Register Customer")

    if save:
        if not name.strip():
            st.error("Customer name is required.")
        else:
            with connect() as con:
                con.execute("""
                    INSERT INTO customers(name,phone,address)
                    VALUES(?,?,?)
                """, (name.strip(), phone, address))
                con.commit()
            st.success("Customer registered!")
            st.rerun()

    st.subheader("Customer List")
    df = read_data("SELECT * FROM customers ORDER BY id DESC")

    if df.empty:
        st.info("No customers registered.")
    else:
        st.dataframe(df, use_container_width=True, hide_index=True)


# =============== PDF BILL ===============

def make_pdf(data):
    if not PDF_AVAILABLE:
        return None

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    pdf.setFont("Helvetica-Bold", 20)
    pdf.drawString(45, height - 55, "PHARMACY MANAGEMENT")

    pdf.setFont("Helvetica", 12)
    pdf.drawString(45, height - 90, "Sales Invoice")
    pdf.drawString(45, height - 120, "Invoice: " + data["invoice"])
    pdf.drawString(45, height - 145, "Customer: " + (data["customer"] or "Walk-in"))
    pdf.drawString(45, height - 190, "Medicine: " + data["medicine"][:35])
    pdf.drawString(45, height - 215, f"Quantity: {data['qty']}")
    pdf.drawString(45, height - 240, f"Price: INR {data['price']:.2f}")

    pdf.setFont("Helvetica-Bold", 15)
    pdf.drawString(45, height - 280, f"Total: INR {data['total']:.2f}")

    pdf.setFont("Helvetica", 11)
    pdf.drawString(45, height - 330, "Thank you for your purchase!")

    pdf.save()
    buffer.seek(0)
    return buffer.getvalue()


# =============== SALES & BILLING ===============

def sales_billing():
    st.title("🧾 Sales & Billing")

    medicines = read_data(
        "SELECT * FROM medicines WHERE quantity > 0 ORDER BY name"
    )
    customers = read_data("SELECT * FROM customers ORDER BY name")

    if medicines.empty:
        st.warning("No stock available. Add medicines first.")
        return

    customer_options = ["Walk-in Customer"]
    if not customers.empty:
        customer_options += customers["name"].dropna().tolist()

    with st.form("sales_form"):
        customer = st.selectbox("Customer", customer_options)

        medicine_id = st.selectbox(
            "Medicine",
            medicines["id"].tolist(),
            format_func=lambda x:
                f"{medicines[medicines.id == x].iloc[0]['name']} "
                f"(Stock: {int(medicines[medicines.id == x].iloc[0]['quantity'])})"
        )

        item = medicines[medicines["id"] == medicine_id].iloc[0]

        qty = st.number_input(
            "Quantity",
            min_value=1,
            max_value=int(item["quantity"]),
            step=1
        )

        price = st.number_input(
            "Selling Price",
            min_value=0.0,
            value=float(item["price"] or 0),
            step=1.0
        )

        sale = st.form_submit_button("Complete Sale")

    if sale:
        total = int(qty) * float(price)
        invoice = "INV-" + datetime.now().strftime("%Y%m%d%H%M%S")

        customer_name = "" if customer == "Walk-in Customer" else customer

        with connect() as con:
            current = con.execute(
                "SELECT quantity FROM medicines WHERE id=?",
                (medicine_id,)
            ).fetchone()

            if current is None or int(current["quantity"] or 0) < qty:
                st.error("Insufficient stock.")
                return

            con.execute("""
                INSERT INTO sales
                (invoice,customer,medicine,quantity,price,total,sale_date)
                VALUES(?,?,?,?,?,?,?)
            """, (
                invoice, customer_name, item["name"],
                qty, price, total, date.today().isoformat()
            ))

            con.execute(
                "UPDATE medicines SET quantity=quantity-? WHERE id=?",
                (qty, medicine_id)
            )
            con.commit()

        st.session_state.last_invoice = {
            "invoice": invoice,
            "customer": customer_name,
            "medicine": item["name"],
            "qty": int(qty),
            "price": float(price),
            "total": total
        }

        st.success("Sale completed successfully!")
        st.rerun()

    last = st.session_state.get("last_invoice")

    if last:
        st.subheader("Latest Invoice")
        st.write("Invoice:", last["invoice"])
        st.write("Total:", rupees(last["total"]))

        pdf_data = make_pdf(last)

        if pdf_data:
            st.download_button(
                "Download PDF Bill",
                pdf_data,
                file_name=last["invoice"] + ".pdf",
                mime="application/pdf"
            )
        else:
            st.warning(
                "PDF package missing. Install reportlab using pip."
            )

    st.subheader("Sales History")
    sales = read_data("SELECT * FROM sales ORDER BY id DESC")

    if sales.empty:
        st.info("No sales yet.")
    else:
        st.dataframe(sales, use_container_width=True, hide_index=True)


# =============== REPORTS ===============

def reports():
    st.title("📈 Sales Reports")

    df = read_data("SELECT * FROM sales ORDER BY id DESC")

    if df.empty:
        st.info("No sales data available.")
        return

    df["total"] = pd.to_numeric(df["total"], errors="coerce").fillna(0)
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce").fillna(0)

    a, b, c = st.columns(3)
    a.metric("Total Revenue", rupees(df["total"].sum()))
    b.metric("Transactions", len(df))
    c.metric("Units Sold", int(df["quantity"].sum()))

    st.subheader("Sales Records")
    st.dataframe(df, use_container_width=True, hide_index=True)

    csv = df.to_csv(index=False).encode("utf-8-sig")

    st.download_button(
        "Download CSV Report",
        csv,
        file_name="pharmacy_sales_report.csv",
        mime="text/csv"
    )

    st.subheader("Daily Sales")
    daily = df.groupby("sale_date")["total"].sum()
    st.bar_chart(daily)


# =============== MAIN APP ===============

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    login_page()

else:
    with st.sidebar:
        st.markdown("## 💊 Pharmacy Admin")
        st.caption("Management Panel")

        page = st.radio(
            "Navigation",
            [
                "Dashboard",
                "Medicine Management",
                "Customer Management",
                "Sales & Billing",
                "Reports"
            ]
        )

        st.divider()
        st.caption("Logged in as Admin")

        if st.button("Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.pop("last_invoice", None)
            st.rerun()

    header()

    if page == "Dashboard":
        dashboard()
    elif page == "Medicine Management":
        medicine_management()
    elif page == "Customer Management":
        customer_management()
    elif page == "Sales & Billing":
        sales_billing()
    elif page == "Reports":
        reports()

    st.divider()

    st.markdown(
        "<p style='text-align:center;color:#60758a;font-size:12px;'>"
        "Pharmacy Management System | MCA Project"
        "</p>",
        unsafe_allow_html=True
    )
