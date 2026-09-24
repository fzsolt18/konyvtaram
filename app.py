import streamlit as st
import pandas as pd
import json
import os

# Oldal beállításai (Modern, wide elrendezés)
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
        {"id": 1, "title": "A Gyűrűk Ura", "author": "J.R.R. Tolkien", "category": "Fantasy", "year": 1954, "status": "Elérhető"},
        {"id": 2, "title": "1984", "author": "George Orwell", "category": "Disztópia", "year": 1949, "status": "Kölcsönözve"},
        {"id": 3, "title": "Dűne", "author": "Frank Herbert", "category": "Sci-Fi", "year": 1965, "status": "Elérhető"}
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
search_term = st.sidebar.text_input("Keresés címre vagy szerzőre...")

categories = ["Mind"] + list(set(b["category"] for b in st.session_state.books))
selected_category = st.sidebar.selectbox("Kategória", categories)

# --- FŐ TARTALOM: TABOK ---
tab1, tab2, tab3 = st.tabs(["📖 Könyvek Listája", "➕ Új Könyv Hozzáadása", "⚙️ Kezelés & Status"])

# 1. TAB: Könyvek listája
with tab1:
    filtered_books = st.session_state.books
    
    if search_term:
        filtered_books = [b for b in filtered_books if search_term.lower() in b["title"].lower() or search_term.lower() in b["author"].lower()]
    
    if selected_category != "Mind":
        filtered_books = [b for b in filtered_books if b["category"] == selected_category]

    if filtered_books:
        df = pd.DataFrame(filtered_books)
        df.columns = ["ID", "Cím", "Szerző", "Kategória", "Kiadási Év", "Státusz"]
        st.dataframe(df.drop(columns=["ID"]), use_container_width=True)
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
        year = c2.number_input("Kiadási év", min_value=1000, max_value=2026, value=2024)
        
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
                    "status": "Elérhető"
                }
                st.session_state.books.append(new_book)
                save_data(st.session_state.books)
                st.success(f"A(z) **{title}** sikeresen hozzáadva!")
                st.rerun()
            else:
                st.error("Kérjük, töltsd ki az összes mezőt!")

# 3. TAB: Status módosítás & Törlés
with tab3:
    st.subheader("Kölcsönzés és Törlés")
    if st.session_state.books:
        book_options = {f"{b['title']} ({b['author']})": b["id"] for b in st.session_state.books}
        selected_book_name = st.selectbox("Válassz egy könyvet", list(book_options.keys()))
        selected_book_id = book_options[selected_book_name]
        
        # Kiválasztott könyv megkeresése
        current_book = next(b for b in st.session_state.books if b["id"] == selected_book_id)
        
        col_act1, col_act2 = st.columns(2)
        
        with col_act1:
            new_status = "Kölcsönözve" if current_book["status"] == "Elérhető" else "Elérhető"
            button_label = "Megjelölés Kölcsönzöttként" if current_book["status"] == "Elérhető" else "Visszahozva (Megjelölés Elérhetőként)"
            
            if st.button(button_label):
                current_book["status"] = new_status
                save_data(st.session_state.books)
                st.success(f"A könyv státusza frissítve: **{new_status}**")
                st.rerun()

        with col_act2:
            if st.button("❌ Könyv törlése", type="primary"):
                st.session_state.books = [b for b in st.session_state.books if b["id"] != selected_book_id]
                save_data(st.session_state.books)
                st.warning("Könyv törölve!")
                st.rerun()