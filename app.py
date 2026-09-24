import streamlit as st
import pandas as pd
import json
import os
from datetime import date

# Oldal beállításai (Modern elrendezés)
st.set_page_config(
    page_title="Online Könyvtár",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

DATA_FILE = "library_data.json"

# Adatok betöltése JSON fájlból
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return [
        {
            "id": 1, 
            "title": "A Gyűrűk Ura", 
            "author": "J.R.R. Tolkien", 
            "category": "Fantasy", 
            "year": 1954, 
            "status": "Elérhető",
            "borrower": "",
            "borrow_date": ""
        },
        {
            "id": 2, 
            "title": "1984", 
            "author": "George Orwell", 
            "category": "Disztópia", 
            "year": 1949, 
            "status": "Kölcsönözve",
            "borrower": "Kovács Péter",
            "borrow_date": "2026-03-15"
        },
        {
            "id": 3, 
            "title": "Dűne", 
            "author": "Frank Herbert", 
            "category": "Sci-Fi", 
            "year": 1965, 
            "status": "Elérhető",
            "borrower": "",
            "borrow_date": ""
        }
    ]

# Adatok mentése
def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

if "books" not in st.session_state:
    st.session_state.books = load_data()

# --- FEJLÉC & METRIKÁK ---
st.title("📚 Könyvtár Kezelő Rendszer")
st.caption("Modern webes felület könyvek nyilvántartásához és kölcsönzéséhez.")

col1, col2, col3 = st.columns(3)
total_books = len(st.session_state.books)
available_books = sum(1 for b in st.session_state.books if b["status"] == "Elérhető")
borrowed_books = total_books - available_books

col1.metric("Összes könyv", total_books)
col2.metric("Elérhető", available_books)
col3.metric("Kölcsönözve", borrowed_books)

st.divider()

# --- OLDALSÁV (Keresés és szűrés) ---
st.sidebar.header("🔍 Szűrés és Keresés")
search_term = st.sidebar.text_input("Keresés címre, szerzőre vagy kölcsönzőre...")

categories = ["Mind"] + sorted(list(set(b["category"] for b in st.session_state.books)))
selected_category = st.sidebar.selectbox("Kategória", categories)

status_filter = st.sidebar.radio("Státusz szűrés", ["Mind", "Elérhető", "Kölcsönözve"])

# --- FŐ TARTALOM: TABOK ---
tab1, tab2, tab3 = st.tabs(["📖 Könyvek Listája", "➕ Új Könyv Hozzáadása", "🔄 Kölcsönzés & Kezelés"])

# 1. TAB: Könyvek listája
with tab1:
    filtered_books = st.session_state.books

    # Keresési szűrők
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
        # Adattábla elkészítése áttekinthető mezőnevekkel
        data_to_show = []
        for b in filtered_books:
            data_to_show.append({
                "Cím": b["title"],
                "Szerző": b["author"],
                "Kategória": b["category"],
                "Kiadási Év": b["year"],
                "Státusz": "🟢 Elérhető" if b["status"] == "Elérhető" else "🔴 Kölcsönözve",
                "Kölcsönző": b.get("borrower", "-") if b["status"] == "Kölcsönözve" else "-",
                "Kölcsönzés Dátuma": b.get("borrow_date", "-") if b["status"] == "Kölcsönözve" else "-"
            })
        
        df = pd.DataFrame(data_to_show)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Nincs a keresésnek megfelelő könyv.")

# 2. TAB: Új könyv hozzáadása
with tab2:
    st.subheader("Új könyv regisztrálása")
    with st.form("add_book_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        title = c1.text_input("Könyv címe")
        author = c2.text_input("Szerző")
        category = c1.text_input("Kategória (pl. Sci-Fi, Regény)")
        year = c2.number_input("Kiadási év", min_value=1000, max_value=2030, value=2024)

        submitted = st.form_submit_button("Könyv Mentése")
        if submitted:
            if title and author and category:
                new_id = max([b["id"] for b in st.session_state.books], default=0) + 1
                new_book = {
                    "id": new_id,
                    "title": title,
                    "author": author,
                    "category": category,
                    "year": int(year),
                    "status": "Elérhető",
                    "borrower": "",
                    "borrow_date": ""
                }
                st.session_state.books.append(new_book)
                save_data(st.session_state.books)
                st.success(f"A(z) **{title}** sikeresen hozzáadva!")
                st.rerun()
            else:
                st.error("Kérjük, töltsd ki az összes mezőt!")

# 3. TAB: Kölcsönzés, Visszahozatal & Törlés
with tab3:
    st.subheader("Kölcsönzés és Státusz Frissítése")
    if st.session_state.books:
        book_options = {f"{b['title']} — {b['author']} ({b['status']})": b["id"] for b in st.session_state.books}
        selected_book_name = st.selectbox("Válassz egy könyvet", list(book_options.keys()))
        selected_book_id = book_options[selected_book_name]

        # Kiválasztott könyv adatai
        current_book = next(b for b in st.session_state.books if b["id"] == selected_book_id)

        col_left, col_right = st.columns(2)

        with col_left:
            st.write(### "Könyv állapota")
            if current_book["status"] == "Elérhető":
                st.info("Ez a könyv jelenleg **Elérhető**.")
                
                # Kölcsönzés űrlap
                with st.form("borrow_form"):
                    st.write("**Kölcsönzés rögzítése:**")
                    borrower_name = st.text_input("Kölcsönző neve")
                    borrow_d = st.date_input("Kölcsönzés dátuma", value=date.today())
                    
                    submit_borrow = st.form_submit_button("📤 Kölcsönzés rögzítése")
                    if submit_borrow:
                        if borrower_name.strip():
                            current_book["status"] = "Kölcsönözve"
                            current_book["borrower"] = borrower_name.strip()
                            current_book["borrow_date"] = str(borrow_d)
                            save_data(st.session_state.books)
                            st.success(f"A könyvet kikölcsönözte: **{borrower_name}** ({borrow_d})")
                            st.rerun()
                        else:
                            st.error("Adja meg a kölcsönző nevét!")
            else:
                st.warning(f"Ez a könyv **Kölcsönözve** van.\n\n"
                           f"👤 **Kölcsönző:** {current_book.get('borrower', 'Nincs megadva')}\n\n"
                           f"📅 **Dátum:** {current_book.get('borrow_date', 'Nincs megadva')}")
                
                if st.button("📥 Visszahozatal rögzítése (Megjelölés elérhetőként)"):
                    current_book["status"] = "Elérhető"
                    current_book["borrower"] = ""
                    current_book["borrow_date"] = ""
                    save_data(st.session_state.books)
                    st.success("A könyv sikeresen visszahozva!")
                    st.rerun()

        with col_right:
            st.write(### "Egyéb műveletek")
            st.write("A kiválasztott könyv végleges törlése a rendszerből:")
            if st.button("❌ Könyv törlése", type="primary"):
                st.session_state.books = [b for b in st.session_state.books if b["id"] != selected_book_id]
                save_data(st.session_state.books)
                st.warning("A könyv törölve lett az adatbázisból!")
                st.rerun()