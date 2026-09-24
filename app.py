import streamlit as st
import pandas as pd
import json
import os
from datetime import date

# Oldal beállításai (Modern, széles elrendezés)
st.set_page_config(
    page_title="Könyvtár Kezelő Rendszer",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- JELSZÓVÉDELEM ---
PASSWORD = "zSof123"

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown("<h1 style='text-align: center;'>🔒 Bejelentkezés</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray;'>A könyvtárkezelő rendszer használatához adja meg a jelszót.</p>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            input_password = st.text_input("Jelszó", type="password", placeholder="Adja meg a jelszót...")
            submit_button = st.form_submit_button("Belépés", use_container_width=True)

            if submit_button:
                if input_password == PASSWORD:
                    st.session_state.authenticated = True
                    st.success("Sikeres belépés!")
                    st.rerun()
                else:
                    st.error("Hibás jelszó! Próbálja újra.")
    st.stop()

# --- ADATKEZELÉS ---
DATA_FILE = "library_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return [
        {"id": 1, "title": "A Gyűrűk Ura", "author": "J.R.R. Tolkien", "category": "Fantasy", "year": 1954, "status": "Elérhető", "borrower": "", "borrow_date": ""},
        {"id": 2, "title": "1984", "author": "George Orwell", "category": "Disztópia", "year": 1949, "status": "Kölcsönözve", "borrower": "Kovács Péter", "borrow_date": "2026-03-15"},
        {"id": 3, "title": "Dűne", "author": "Frank Herbert", "category": "Sci-Fi", "year": 1965, "status": "Elérhető", "borrower": "", "borrow_date": ""}
    ]

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

if "books" not in st.session_state:
    st.session_state.books = load_data()

# --- OLDALSÁV (Kijelentkezés és szűrők) ---
with st.sidebar:
    st.title("📚 Könyvtár App")
    st.caption("Verzió: 2.0 (Modern UI)")
    
    if st.button("🚪 Kijelentkezés", use_container_width=True):
        st.session_state.authenticated = False
        st.rerun()

    st.divider()
    st.header("🔍 Szűrés és Keresés")
    search_term = st.text_input("Keresés...", placeholder="Cím, szerző, kölcsönző...")

    categories = ["Mind"] + sorted(list(set(b["category"] for b in st.session_state.books)))
    selected_category = st.selectbox("Kategória szűrő", categories)

    status_filter = st.radio("Státusz szűrő", ["Mind", "Elérhető", "Kölcsönözve"])

# --- FEJLÉC & STATISZTIKÁK ---
st.title("📖 Könyvtár Kezelő Rendszer")
st.write("Nyilvántartó és kölcsönzési felület")

total_books = len(st.session_state.books)
available_books = sum(1 for b in st.session_state.books if b["status"] == "Elérhető")
borrowed_books = total_books - available_books

m1, m2, m3 = st.columns(3)
m1.metric("Összes könyv", f"{total_books} db")
m2.metric("Elérhető", f"{available_books} db", delta=f"{available_books} szabad", delta_color="normal")
m3.metric("Kölcsönözve", f"{borrowed_books} db", delta=f"{borrowed_books} kiadva", delta_color="inverse")

st.divider()

# --- FŐ TARTALOM: TABOK ---
tab_list, tab_add, tab_manage = st.tabs([
    "📖 Könyvtár böngésző", 
    "➕ Új könyv felvétele", 
    "✏️ Szerkesztés & Kölcsönzés"
])

# ---------------------------------------------------------
# 1. TAB: Könyvtár böngésző
# ---------------------------------------------------------
with tab_list:
    filtered_books = st.session_state.books

    if search_term:
        term = search_term.lower()
        filtered_books = [
            b for b in filtered_books 
            if term in b["title"].lower() 
            or term in b["author"].lower() 
            or term in b.get("borrower", "").lower()
        ]

    if selected_category != "Mind":
        filtered_books = [b for b in filtered_books if b["category"] == selected_category]

    if status_filter != "Mind":
        filtered_books = [b for b in filtered_books if b["status"] == status_filter]

    if filtered_books:
        data_to_show = []
        for b in filtered_books:
            data_to_show.append({
                "ID": b["id"],
                "Cím": b["title"],
                "Szerző": b["author"],
                "Kategória": b["category"],
                "Kiadási Év": b["year"],
                "Státusz": "🟢 Elérhető" if b["status"] == "Elérhető" else "🔴 Kölcsönözve",
                "Kölcsönző": b.get("borrower", "-") if b["status"] == "Kölcsönözve" else "-",
                "Dátum": b.get("borrow_date", "-") if b["status"] == "Kölcsönözve" else "-"
            })
        
        df = pd.DataFrame(data_to_show)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("Nincs a keresési feltételeknek megfelelő könyv.")

# ---------------------------------------------------------
# 2. TAB: Új könyv hozzáadása
# ---------------------------------------------------------
with tab_add:
    st.subheader("➕ Új könyv regisztrálása")
    with st.form("add_book_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        title = col1.text_input("Könyv címe*")
        author = col2.text_input("Szerző*")
        category = col1.text_input("Kategória* (pl. Sci-Fi, Történelem)")
        year = col2.number_input("Kiadási év*", min_value=1000, max_value=2030, value=2024)

        submitted = st.form_submit_button("💾 Könyv Mentése", use_container_width=True)
        if submitted:
            if title.strip() and author.strip() and category.strip():
                new_id = max([b["id"] for b in st.session_state.books], default=0) + 1
                new_book = {
                    "id": new_id,
                    "title": title.strip(),
                    "author": author.strip(),
                    "category": category.strip(),
                    "year": int(year),
                    "status": "Elérhető",
                    "borrower": "",
                    "borrow_date": ""
                }
                st.session_state.books.append(new_book)
                save_data(st.session_state.books)
                st.success(f"A(z) **{title}** sikeresen hozzáadva a könyvtárhoz!")
                st.rerun()
            else:
                st.error("Kérjük, töltsön ki minden kötelező (*) mezőt!")

# ---------------------------------------------------------
# 3. TAB: Szerkesztés & Kölcsönzés
# ---------------------------------------------------------
with tab_manage:
    if not st.session_state.books:
        st.info("Nincs egyetlen könyv sem a nyilvántartásban.")
    else:
        st.subheader("⚙️ Könyv kezelése és adatok módosítása")
        
        # Könyv kiválasztása
        book_options = {f"#{b['id']} | {b['title']} — {b['author']} ({b['status']})": b["id"] for b in st.session_state.books}
        selected_label = st.selectbox("Válassza ki a kezelendő könyvet:", list(book_options.keys()))
        selected_id = book_options[selected_label]
        
        # A kiválasztott könyv lekérése
        current_book = next(b for b in st.session_state.books if b["id"] == selected_id)

        col_edit, col_borrow = st.columns(2, gap="large")

        # --- BAL OSZLOP: ADATOK SZERKESZTÉSE UTÓLAG ---
        with col_edit:
            st.markdown("### 📝 Adatok szerkesztése")
            with st.form(f"edit_form_{current_book['id']}"):
                edit_title = st.text_input("Cím", value=current_book["title"])
                edit_author = st.text_input("Szerző", value=current_book["author"])
                edit_category = st.text_input("Kategória", value=current_book["category"])
                edit_year = st.number_input("Kiadási év", min_value=1000, max_value=2030, value=int(current_book["year"]))
                
                save_changes = st.form_submit_button("💾 Módosítások mentése", use_container_width=True)
                if save_changes:
                    if edit_title.strip() and edit_author.strip() and edit_category.strip():
                        current_book["title"] = edit_title.strip()
                        current_book["author"] = edit_author.strip()
                        current_book["category"] = edit_category.strip()
                        current_book["year"] = int(edit_year)
                        
                        save_data(st.session_state.books)
                        st.success("A könyv adatai sikeresen frissültek!")
                        st.rerun()
                    else:
                        st.error("A mezők nem lehetnek üresek!")

        # --- JOBB OSZLOP: KÖLCSÖNZÉS ÉS TÖRLÉS ---
        with col_borrow:
            st.markdown("### 🔄 Kölcsönzési állapot")
            
            if current_book["status"] == "Elérhető":
                st.success("Ez a könyv jelenleg **Elérhető**.")
                
                with st.form(f"borrow_form_{current_book['id']}"):
                    st.write("**Kölcsönzés rögzítése:**")
                    borrower_name = st.text_input("Kölcsönző neve")
                    borrow_d = st.date_input("Dátum", value=date.today())
                    
                    submit_borrow = st.form_submit_button("📤 Kölcsönzés rögzítése", use_container_width=True)
                    if submit_borrow:
                        if borrower_name.strip():
                            current_book["status"] = "Kölcsönözve"
                            current_book["borrower"] = borrower_name.strip()
                            current_book["borrow_date"] = str(borrow_d)
                            save_data(st.session_state.books)
                            st.success(f"Sikeresen kikölcsönözve: **{borrower_name}**")
                            st.rerun()
                        else:
                            st.error("Kérjük, adja meg a kölcsönző nevét!")
            else:
                st.warning(f"Ez a könyv **Kölcsönözve** van.\n\n"
                           f"👤 **Kölcsönző:** {current_book.get('borrower', 'N/A')}\n\n"
                           f"📅 **Kivétel dátuma:** {current_book.get('borrow_date', 'N/A')}")
                
                if st.button("📥 Visszahozatal rögzítése", use_container_width=True):
                    current_book["status"] = "Elérhető"
                    current_book["borrower"] = ""
                    current_book["borrow_date"] = ""
                    save_data(st.session_state.books)
                    st.success("A könyv visszahozva, státusza újra elérhető!")
                    st.rerun()

            st.divider()
            st.markdown("### ⚠️ Törlés")
            if st.button("❌ Könyv végleges törlése", type="primary", use_container_width=True):
                st.session_state.books = [b for b in st.session_state.books if b["id"] != selected_id]
                save_data(st.session_state.books)
                st.warning("A könyv törölve lett a nyilvántartásból!")
                st.rerun()