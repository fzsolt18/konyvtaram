import streamlit as st
import pandas as pd
import json
import os
from datetime import date, datetime, timedelta
from fpdf import FPDF

# --- OLDAL BEÁLLÍTÁSOK ---
st.set_page_config(
    page_title="Pro Könyvtár Rendszer",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- JELSZÓVÉDELEM ---
PASSWORD = "zSof123"

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown("<br><br><h1 style='text-align: center; color: #2E86C1;'>📚 Pro Könyvtár Rendszer</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray;'>Kérjük, azonosítsa magát a belépéshez!</p>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        with st.form("login_form"):
            input_password = st.text_input("Biztonsági Jelszó", type="password", placeholder="Adja meg a jelszót...")
            submit_button = st.form_submit_button("Bejelentkezés", use_container_width=True)

            if submit_button:
                if input_password == PASSWORD:
                    st.session_state.authenticated = True
                    st.success("Sikeres belépés! Betöltés...")
                    st.rerun()
                else:
                    st.error("Hibás jelszó! Próbálja újra.")
    st.stop()

# --- ADATKEZELÉS ÉS NORMALIZÁLÁS ---
DATA_FILE = "library_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        # Alapértelmezett adatok Leltári számmal
        data = [
            {"id": 1, "inventory_number": "LELT-0001", "title": "A Gyűrűk Ura", "author": "J.R.R. Tolkien", "category": "Fantasy", "year": 1954, "status": "Elérhető", "borrower": "", "borrow_date": "", "due_date": "", "cover_url": "", "description": "Frodó és a Gyűrű Szövetségének epikus útja."},
            {"id": 2, "inventory_number": "LELT-0002", "title": "1984", "author": "George Orwell", "category": "Disztópia", "year": 1949, "status": "Kölcsönözve", "borrower": "Kovács Péter", "borrow_date": "2026-03-01", "due_date": "2026-03-15", "cover_url": "", "description": "A Nagy Testvér mindent lát."}
        ]
    
    # Adatok frissítése/normalizálása ha régi struktúrából jönne
    for book in data:
        book.setdefault("inventory_number", f"LELT-{book.get('id', 1):04d}")
        book.setdefault("due_date", "")
        book.setdefault("cover_url", "")
        book.setdefault("description", "")
    return data

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

if "books" not in st.session_state:
    st.session_state.books = load_data()

# Segédfüggvény a késések ellenőrzéséhez
def is_overdue(due_date_str):
    if not due_date_str: return False
    try:
        due = datetime.strptime(due_date_str, "%Y-%m-%d").date()
        return due < date.today()
    except:
        return False

# --- PDF GENERÁLÓ FÜGGVÉNY ---
def generate_pdf(books):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    
    # Cím / Fejléc
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "Konyvtari Adatbazis Katalogus", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.set_font("Helvetica", "I", 10)
    pdf.cell(0, 6, f"Keszult: {date.today().strftime('%Y-%m-%d')}", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(5)
    
    # Ékezetek átalakítása a PDF kompatibilitáshoz
    def sanitize(text):
        t = str(text)
        t = t.replace('ő', 'ö').replace('Ő', 'Ö').replace('ű', 'ü').replace('Ű', 'Ü')
        return t.encode('latin-1', 'replace').decode('latin-1')

    # Táblázat fejlécek
    headers = ["Leltari szam", "Cim", "Szerzo", "Kategoria", "Kiadas", "Statusz", "Kolcsonzo", "Hatarido"]
    col_widths = [32, 65, 45, 30, 20, 25, 35, 25]
    
    pdf.set_font("Helvetica", "B", 10)
    for i, h in enumerate(headers):
        pdf.cell(col_widths[i], 8, h, border=1, align="C")
    pdf.ln()
    
    # Táblázat adatai
    pdf.set_font("Helvetica", "", 9)
    for b in books:
        row = [
            sanitize(b.get("inventory_number", "")),
            sanitize(b.get("title", "")),
            sanitize(b.get("author", "")),
            sanitize(b.get("category", "")),
            sanitize(b.get("year", "")),
            sanitize(b.get("status", "")),
            sanitize(b.get("borrower", "")),
            sanitize(b.get("due_date", ""))
        ]
        
        for i, val in enumerate(row):
            # Cím és szerző levágása, ha túl hosszú
            if len(val) > 30 and i in [1, 2]:
                val = val[:27] + "..."
            pdf.cell(col_widths[i], 8, val, border=1)
        pdf.ln()
        
    try:
        return bytes(pdf.output())
    except TypeError:
        return pdf.output(dest='S').encode('latin-1')

# --- NAVIGÁCIÓS OLDALSÁV ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3389/3389081.png", width=80)
    st.title("Könyvtár Admin")
    st.caption("Verzió: 3.2 Pro")
    st.divider()
    
    menu = st.radio(
        "📌 Főmenü",
        ["📊 Vezérlőpult", "📚 Katalógus & Kereső", "🔄 Kölcsönzési Pult", "⚙️ Állomány Kezelése", "💾 Adatbázis Mentése"]
    )
    
    st.divider()
    if st.button("🚪 Kijelentkezés", type="primary", use_container_width=True):
        st.session_state.authenticated = False
        st.rerun()

# ---------------------------------------------------------
# 1. VEZÉRLŐPULT (DASHBOARD)
# ---------------------------------------------------------
if menu == "📊 Vezérlőpult":
    st.header("📊 Rendszer Áttekintés")
    
    total_books = len(st.session_state.books)
    available_books = sum(1 for b in st.session_state.books if b["status"] == "Elérhető")
    borrowed_books = total_books - available_books
    overdue_books = sum(1 for b in st.session_state.books if b["status"] == "Kölcsönözve" and is_overdue(b["due_date"]))

    # Felső metrikák
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Összes Könyv", total_books)
    m2.metric("🟢 Elérhető", available_books)
    m3.metric("🟡 Kölcsönözve", borrowed_books)
    m4.metric("🔴 Késésben", overdue_books, delta="- Intézkedés javasolt!" if overdue_books > 0 else "Minden rendben", delta_color="inverse")

    st.divider()
    
    st.subheader("⚠️ Figyelmeztetések")
    if overdue_books > 0:
        st.error(f"**{overdue_books} db könyv lejárt határidejű!**")
        for b in st.session_state.books:
            if b["status"] == "Kölcsönözve" and is_overdue(b["due_date"]):
                st.warning(f"📖 **[{b['inventory_number']}] {b['title']}**\n\n👤 {b['borrower']}\n\n⏳ Lejárt: {b['due_date']}")
    else:
        st.success("🎉 Nincs lejárt határidejű kölcsönzés!")

# ---------------------------------------------------------
# 2. KATALÓGUS & KERESŐ
# ---------------------------------------------------------
elif menu == "📚 Katalógus & Kereső":
    st.header("📚 Könyvtári Katalógus")
    
    # Kereső sáv
    search_term = st.text_input("🔍 Keresés (Leltári szám, Cím, Szerző, Kategória, Leírás alapján...)", placeholder="Írd be a keresőszót...")
    
    # Szűrési adatok
    filtered_books = st.session_state.books
    if search_term:
        term = search_term.lower()
        filtered_books = [
            b for b in filtered_books 
            if term in b["inventory_number"].lower()
            or term in b["title"].lower() 
            or term in b["author"].lower() 
            or term in b["category"].lower()
            or term in b.get("description", "").lower()
        ]

    st.divider()

    if not filtered_books:
        st.info("Nincs találat a megadott feltételekkel.")
    else:
        st.caption("💡 **Tipp:** Kattints a táblázat bármelyik sorára a könyv részletes adatlapjának megtekintéséhez!")
        
        # Táblázat adatai
        df_show = pd.DataFrame(filtered_books)[["inventory_number", "title", "author", "category", "year", "status", "borrower", "due_date"]]
        df_show.columns = ["Leltári szám", "Cím", "Szerző", "Kategória", "Kiadás", "Státusz", "Kölcsönző", "Határidő"]
        
        # Interaktív táblázat sorkijelöléssel
        event = st.dataframe(
            df_show, 
            use_container_width=True, 
            hide_index=True,
            on_select="rerun",
            selection_mode="single-row"
        )

        # Adatlap megjelenítése, ha ki van választva egy sor
        selected_rows = event.selection.rows
        if selected_rows:
            selected_idx = selected_rows[0]
            selected_book = filtered_books[selected_idx]

            st.divider()
            st.subheader(f"📖 Adatlap: {selected_book['title']}")

            col1, col2 = st.columns([1, 2])
            with col1:
                st.markdown(f"**🏷️ Leltári szám:** `{selected_book['inventory_number']}`")
                st.markdown(f"**✍️ Szerző:** {selected_book['author']}")
                st.markdown(f"**🏷️ Kategória:** {selected_book['category']}")
                st.markdown(f"**📅 Kiadási év:** {selected_book['year']}")
                
                status_color = "green" if selected_book['status'] == "Elérhető" else "orange"
                st.markdown(f"**📌 Státusz:** :{status_color}[{selected_book['status']}]")
                
                if selected_book['status'] == "Kölcsönözve":
                    st.markdown(f"**👤 Kölcsönző:** {selected_book['borrower']}")
                    st.markdown(f"**📅 Kölcsönzés dátuma:** {selected_book.get('borrow_date', '-')}")
                    st.markdown(f"**⏳ Határidő:** {selected_book['due_date']}")

            with col2:
                st.markdown("**📝 Leírás / Szinopszis:**")
                if selected_book.get("description"):
                    st.info(selected_book["description"])
                else:
                    st.caption("Nincs leírás megadva ehhez a könyvhöz.")

# ---------------------------------------------------------
# 3. KÖLCSÖNZÉSI PULT
# ---------------------------------------------------------
elif menu == "🔄 Kölcsönzési Pult":
    st.header("🔄 Kölcsönzés és Visszavétel")
    st.write("Gyors adminisztrációs felület a napi könyvforgalomhoz.")

    if not st.session_state.books:
        st.warning("A könyvtár üres!")
    else:
        book_options = {f"[{b['inventory_number']}] {b['title']} ({b['status']})": b["id"] for b in st.session_state.books}
        selected_label = st.selectbox("📖 Válassz egy könyvet a tranzakcióhoz:", ["-- Válassz --"] + list(book_options.keys()))
        
        if selected_label != "-- Válassz --":
            selected_id = book_options[selected_label]
            current_book = next(b for b in st.session_state.books if b["id"] == selected_id)
            
            st.divider()
            
            if current_book["status"] == "Elérhető":
                st.subheader("📤 Új Kölcsönzés Rögzítése")
                with st.form("borrow_form"):
                    col1, col2 = st.columns(2)
                    borrower = col1.text_input("👤 Kölcsönző Neve*")
                    borrow_d = col2.date_input("📅 Kölcsönzés Dátuma", value=date.today())
                    due_d = col2.date_input("⏳ Várható Visszahozatal", value=date.today() + timedelta(days=14))
                    
                    if st.form_submit_button("✅ Kölcsönzés Jóváhagyása", type="primary"):
                        if borrower.strip():
                            current_book["status"] = "Kölcsönözve"
                            current_book["borrower"] = borrower.strip()
                            current_book["borrow_date"] = str(borrow_d)
                            current_book["due_date"] = str(due_d)
                            save_data(st.session_state.books)
                            st.success(f"Könyv sikeresen kiadva {borrower.strip()} számára!")
                            st.rerun()
                        else:
                            st.error("A kölcsönző nevét kötelező megadni!")
                            
            else:
                st.subheader("📥 Könyv Visszavétele")
                is_late = is_overdue(current_book["due_date"])
                
                col1, col2 = st.columns(2)
                with col1:
                    st.info(f"**Leltári szám:** {current_book['inventory_number']}\n\n**Kölcsönző:** {current_book['borrower']}\n\n**Elvitte:** {current_book['borrow_date']}\n\n**Határidő:** {current_book['due_date']}")
                with col2:
                    if is_late:
                        st.error("⚠️ Figyelem! A könyvet késve hozták vissza!")
                    else:
                        st.success("✅ A könyv időben érkezett vissza.")
                
                if st.button("🔄 Visszavétel Rögzítése (Újra Elérhető)", type="primary"):
                    current_book["status"] = "Elérhető"
                    current_book["borrower"] = ""
                    current_book["borrow_date"] = ""
                    current_book["due_date"] = ""
                    save_data(st.session_state.books)
                    st.success("Visszavétel rögzítve!")
                    st.rerun()

# ---------------------------------------------------------
# 4. ÁLLOMÁNY KEZELÉSE (Új könyv, Szerkesztés, Törlés)
# ---------------------------------------------------------
elif menu == "⚙️ Állomány Kezelése":
    st.header("⚙️ Könyvtári Állomány Kezelése")
    
    tab_new, tab_edit = st.tabs(["➕ Új Könyv Felvétele", "✏️ Szerkesztés és Törlés"])
    
    with tab_new:
        next_id = max([b["id"] for b in st.session_state.books], default=0) + 1
        default_inv = f"LELT-{next_id:04d}"
        
        with st.form("new_book_form", clear_on_submit=True):
            st.subheader("Könyv alapadatok")
            c1, c2 = st.columns(2)
            inv_num = c1.text_input("Leltári szám*", value=default_inv)
            title = c2.text_input("Cím*")
            author = c1.text_input("Szerző*")
            category = c2.text_input("Kategória*")
            year = c1.number_input("Kiadási év*", min_value=1000, max_value=2030, value=2024)
            
            st.subheader("Extra adatok (Opcionális)")
            description = st.text_area("Rövid leírás / Szinopszis")
            
            if st.form_submit_button("💾 Könyv Hozzáadása a Katalógushoz", type="primary"):
                if inv_num and title and author and category:
                    new_book = {
                        "id": next_id, 
                        "inventory_number": inv_num.strip(), 
                        "title": title, 
                        "author": author, 
                        "category": category, 
                        "year": int(year), 
                        "status": "Elérhető", 
                        "borrower": "", 
                        "borrow_date": "", 
                        "due_date": "", 
                        "cover_url": "", 
                        "description": description
                    }
                    st.session_state.books.append(new_book)
                    save_data(st.session_state.books)
                    st.success("Sikeres mentés!")
                    st.rerun()
                else:
                    st.error("A *-gal jelölt mezők kitöltése kötelező!")

    with tab_edit:
        if not st.session_state.books:
            st.info("Nincs szerkeszthető könyv.")
        else:
            book_options = {f"[{b['inventory_number']}] {b['title']} - {b['author']}": b["id"] for b in st.session_state.books}
            selected_label = st.selectbox("Válassz könyvet módosításhoz:", ["-- Válassz --"] + list(book_options.keys()))
            
            if selected_label != "-- Válassz --":
                selected_id = book_options[selected_label]
                cb = next(b for b in st.session_state.books if b["id"] == selected_id)
                
                with st.form(f"edit_{cb['id']}"):
                    st.write("Adatok módosítása:")
                    e_inv = st.text_input("Leltári szám", value=cb.get("inventory_number", ""))
                    e_title = st.text_input("Cím", value=cb["title"])
                    e_author = st.text_input("Szerző", value=cb["author"])
                    e_cat = st.text_input("Kategória", value=cb["category"])
                    e_year = st.number_input("Kiadási év", value=int(cb["year"]))
                    e_desc = st.text_area("Leírás", value=cb.get("description", ""))
                    
                    if st.form_submit_button("💾 Módosítások Mentése"):
                        cb["inventory_number"] = e_inv.strip()
                        cb["title"], cb["author"], cb["category"], cb["year"] = e_title, e_author, e_cat, int(e_year)
                        cb["description"] = e_desc
                        save_data(st.session_state.books)
                        st.success("Frissítve!")
                        st.rerun()
                
                st.divider()
                st.write("Veszélyes Zóna")
                if st.button("❌ Könyv Végleges Törlése", type="primary"):
                    st.session_state.books = [b for b in st.session_state.books if b["id"] != selected_id]
                    save_data(st.session_state.books)
                    st.warning("Könyv törölve!")
                    st.rerun()

# ---------------------------------------------------------
# 5. ADATBÁZIS (Exportálás PDF-be)
# ---------------------------------------------------------
elif menu == "💾 Adatbázis Mentése":
    st.header("💾 Adatbázis Exportálása PDF-be")
    st.write("Itt letöltheted a teljes könyvtári adatbázist formázott PDF dokumentumként.")
    
    if st.session_state.books:
        try:
            pdf_data = generate_pdf(st.session_state.books)
            
            st.download_button(
                label="📄 Adatbázis letöltése (.pdf)",
                data=pdf_data,
                file_name=f"konyvtar_adatbazis_{date.today()}.pdf",
                mime="application/pdf",
                type="primary"
            )
            st.info("A letöltött PDF dokumentum megnyitható bármilyen PDF-olvasóban vagy böngészőben.")
        except Exception as e:
            st.error(f"Hiba történt a PDF generálása során: {e}")
            st.caption("Kérjük, győződj meg róla, hogy az `fpdf2` csomag telepítve van (`pip install fpdf2`).")
    else:
        st.warning("Az adatbázis üres, nincs mit exportálni.")