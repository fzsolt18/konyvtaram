import streamlit as st
import pandas as pd
import json
import os
from datetime import date, datetime, timedelta

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
        # Alapértelmezett adatok, ha nincs fájl
        data = [
            {"id": 1, "title": "A Gyűrűk Ura", "author": "J.R.R. Tolkien", "category": "Fantasy", "year": 1954, "status": "Elérhető", "borrower": "", "borrow_date": "", "due_date": "", "cover_url": "", "description": "Frodó és a Gyűrű Szövetségének epikus útja."},
            {"id": 2, "title": "1984", "author": "George Orwell", "category": "Disztópia", "year": 1949, "status": "Kölcsönözve", "borrower": "Kovács Péter", "borrow_date": "2026-03-01", "due_date": "2026-03-15", "cover_url": "", "description": "A Nagy Testvér mindent lát."}
        ]
    
    # Adatok "normalizálása" (ha régi adatbázisból jön, kiegészítjük az új mezőkkel)
    for book in data:
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

# --- NAVIGÁCIÓS OLDALSÁV ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3389/3389081.png", width=80)
    st.title("Könyvtár Admin")
    st.caption("Verzió: 3.0 Pro")
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
                st.warning(f"📖 **{b['title']}**\n\n👤 {b['borrower']}\n\n⏳ Lejárt: {b['due_date']}")
    else:
        st.success("🎉 Nincs lejárt határidejű kölcsönzés!")

# ---------------------------------------------------------
# 2. KATALÓGUS & KERESŐ
# ---------------------------------------------------------
elif menu == "📚 Katalógus & Kereső":
    st.header("📚 Könyvtári Katalógus")
    
    # Kereső sáv (széles)
    search_term = st.text_input("🔍 Keresés (Cím, Szerző, Kategória, Leírás alapján...)", placeholder="Írd be a keresőszót...")
    
    # Szűrési adatok
    filtered_books = st.session_state.books
    if search_term:
        term = search_term.lower()
        filtered_books = [
            b for b in filtered_books 
            if term in b["title"].lower() 
            or term in b["author"].lower() 
            or term in b["category"].lower()
            or term in b.get("description", "").lower()
        ]

    view_mode = st.radio("Nézet:", ["Kártyás (Vizuális)", "Táblázatos (Részletes)"], horizontal=True)
    st.divider()

    if not filtered_books:
        st.info("Nincs találat a megadott feltételekkel.")
    else:
        if view_mode == "Kártyás (Vizuális)":
            cols = st.columns(4)
            for i, b in enumerate(filtered_books):
                with cols[i % 4]:
                    st.container(border=True)
                    if b.get("cover_url"):
                        st.image(b["cover_url"], use_container_width=True)
                    else:
                        st.image("https://via.placeholder.com/150x200.png?text=Nincs+Bor%C3%ADt%C3%B3", use_container_width=True)
                    
                    st.markdown(f"**{b['title']}**")
                    st.caption(f"✍️ {b['author']} | 📅 {b['year']}")
                    
                    if b["status"] == "Elérhető":
                        st.success("🟢 Elérhető")
                    else:
                        if is_overdue(b["due_date"]):
                            st.error("🔴 Késésben")
                        else:
                            st.warning("🟡 Kölcsönözve")
                    
                    with st.expander("Részletek"):
                        st.write(f"**Kategória:** {b['category']}")
                        st.write(f"**Sztori:** {b.get('description', 'Nincs leírás.')}")
                        if b["status"] == "Kölcsönözve":
                            st.write(f"**Kölcsönző:** {b['borrower']}")
                            st.write(f"**Vissza kell hozni:** {b['due_date']}")
        
        else:
            # Táblázatos nézet
            df_show = pd.DataFrame(filtered_books)[["title", "author", "category", "year", "status", "borrower", "due_date"]]
            df_show.columns = ["Cím", "Szerző", "Kategória", "Kiadás", "Státusz", "Kölcsönző", "Határidő"]
            st.dataframe(df_show, use_container_width=True, hide_index=True)

# ---------------------------------------------------------
# 3. KÖLCSÖNZÉSI PULT
# ---------------------------------------------------------
elif menu == "🔄 Kölcsönzési Pult":
    st.header("🔄 Kölcsönzés és Visszavétel")
    st.write("Gyors adminisztrációs felület a napi könyvforgalomhoz.")

    if not st.session_state.books:
        st.warning("A könyvtár üres!")
    else:
        book_options = {f"#{b['id']} | {b['title']} ({b['status']})": b["id"] for b in st.session_state.books}
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
                    
                    # Alapértelmezett 14 napos kölcsönzés
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
                    st.info(f"**Kölcsönző:** {current_book['borrower']}\n\n**Elvitte:** {current_book['borrow_date']}\n\n**Határidő:** {current_book['due_date']}")
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
        with st.form("new_book_form", clear_on_submit=True):
            st.subheader("Könyv alapadatok")
            c1, c2 = st.columns(2)
            title = c1.text_input("Cím*")
            author = c2.text_input("Szerző*")
            category = c1.text_input("Kategória*")
            year = c2.number_input("Kiadási év*", min_value=1000, max_value=2030, value=2024)
            
            st.subheader("Extra adatok (Opcionális)")
            description = st.text_area("Rövid leírás / Szinopszis")
            
            if st.form_submit_button("💾 Könyv Hozzáadása a Katalógushoz", type="primary"):
                if title and author and category:
                    new_id = max([b["id"] for b in st.session_state.books], default=0) + 1
                    new_book = {
                        "id": new_id, "title": title, "author": author, "category": category, 
                        "year": int(year), "status": "Elérhető", "borrower": "", "borrow_date": "", 
                        "due_date": "", "cover_url": "", "description": description
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
            book_options = {f"#{b['id']} | {b['title']} - {b['author']}": b["id"] for b in st.session_state.books}
            selected_label = st.selectbox("Válassz könyvet módosításhoz:", ["-- Válassz --"] + list(book_options.keys()))
            
            if selected_label != "-- Válassz --":
                selected_id = book_options[selected_label]
                cb = next(b for b in st.session_state.books if b["id"] == selected_id)
                
                with st.form(f"edit_{cb['id']}"):
                    st.write("Adatok módosítása:")
                    e_title = st.text_input("Cím", value=cb["title"])
                    e_author = st.text_input("Szerző", value=cb["author"])
                    e_cat = st.text_input("Kategória", value=cb["category"])
                    e_year = st.number_input("Kiadási év", value=int(cb["year"]))
                    e_desc = st.text_area("Leírás", value=cb.get("description", ""))
                    
                    if st.form_submit_button("💾 Módosítások Mentése"):
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
# 5. ADATBÁZIS (Exportálás)
# ---------------------------------------------------------
elif menu == "💾 Adatbázis Mentése":
    st.header("💾 Adatbázis Exportálása")
    st.write("Itt letöltheted a teljes könyvtári adatbázist Excel-kompatibilis CSV formátumban.")
    
    if st.session_state.books:
        df_export = pd.DataFrame(st.session_state.books)
        csv_data = df_export.to_csv(index=False).encode('utf-8')
        
        st.download_button(
            label="⬇️ Adatbázis letöltése (.csv)",
            data=csv_data,
            file_name=f"konyvtar_adatbazis_{date.today()}.csv",
            mime="text/csv",
            type="primary"
        )
        st.info("A letöltött fájlt megnyithatod Microsoft Excelben vagy Google Táblázatokban.")
    else:
        st.warning("Az adatbázis üres, nincs mit exportálni.")