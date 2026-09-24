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
    initial_sidebar_state="collapsed"
)

# --- MOBILBARÁT CSS STÍLUSOK INJEKTÁLÁSA ---
st.markdown("""
<style>
    /* Margók csökkentése mobilon */
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 2rem !important;
        padding-left: 0.8rem !important;
        padding-right: 0.8rem !important;
    }
    
    /* Érintésbarát, nagy gombok mobilon */
    .stButton button {
        width: 100% !important;
        border-radius: 10px !important;
        padding: 0.6rem 1rem !important;
        font-weight: 600 !important;
        font-size: 15px !important;
    }
    
    /* Megakadályozza a kellemetlen iOS/Android ráközelítést gépeléskor */
    input, select, textarea {
        font-size: 16px !important;
    }

    /* Kártya stílus */
    [data-testid="stExpander"] {
        border-radius: 10px !important;
        border: 1px solid #e2e8f0 !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05) !important;
    }
</style>
""", unsafe_allow_html=True)

# --- JELSZÓ ÉS JOGOSULTSÁG KEZELÉS ---
PASSWORD = "zSof123"

if "is_admin" not in st.session_state:
    st.session_state.is_admin = False

# --- ADATKEZELÉS ÉS NORMALIZÁLÁS ---
DATA_FILE = "library_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = [
            {"id": 1, "inventory_number": "LELT-0001", "title": "A Gyűrűk Ura", "author": "J.R.R. Tolkien", "category": "Fantasy", "year": 1954, "status": "Elérhető", "borrower": "", "borrow_date": "", "due_date": "", "cover_url": "", "description": "Frodó és a Gyűrű Szövetségének epikus útja Mordor felé.", "reserved_by": "", "reservation_contact": "", "reservation_date": ""},
            {"id": 2, "inventory_number": "LELT-0002", "title": "1984", "author": "George Orwell", "category": "Disztópia", "year": 1949, "status": "Kölcsönözve", "borrower": "Kovács Péter", "borrow_date": "2026-03-01", "due_date": "2026-03-15", "cover_url": "", "description": "A Nagy Testvér mindent lát.", "reserved_by": "", "reservation_contact": "", "reservation_date": ""},
            {"id": 3, "inventory_number": "LELT-0003", "title": "A Kis Herceg", "author": "Antoine de Saint-Exupéry", "category": "Mese / Filozófia", "year": 1943, "status": "Elérhető", "borrower": "", "borrow_date": "", "due_date": "", "cover_url": "", "description": "Jól csak a szívével lát az ember.", "reserved_by": "", "reservation_contact": "", "reservation_date": ""}
        ]
    
    for book in data:
        book.setdefault("inventory_number", f"LELT-{book.get('id', 1):04d}")
        book.setdefault("due_date", "")
        book.setdefault("cover_url", "")
        book.setdefault("description", "")
        book.setdefault("reserved_by", "")
        book.setdefault("reservation_contact", "")
        book.setdefault("reservation_date", "")
    return data

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

if "books" not in st.session_state:
    st.session_state.books = load_data()

def is_overdue(due_date_str):
    if not due_date_str: return False
    try:
        due = datetime.strptime(due_date_str, "%Y-%m-%d").date()
        return due < date.today()
    except:
        return False

# --- NYOMTATHATÓ HTML GENERÁLÓ FÜGGVÉNY ---
def generate_html_report(books):
    html_content = f"""
    <!DOCTYPE html>
    <html lang="hu">
    <head>
        <meta charset="UTF-8">
        <title>Könyvtári Katalógus Export</title>
        <style>
            body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 30px; color: #333; }}
            h1 {{ text-align: center; color: #2E86C1; margin-bottom: 5px; }}
            p.subtitle {{ text-align: center; color: #666; font-size: 14px; margin-top: 0; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 25px; }}
            th, td {{ border: 1px solid #ddd; padding: 10px; text-align: left; font-size: 13px; }}
            th {{ background-color: #2E86C1; color: white; font-weight: bold; }}
            tr:nth-child(even) {{ background-color: #f9f9f9; }}
            .status-available {{ color: green; font-weight: bold; }}
            .status-borrowed {{ color: orange; font-weight: bold; }}
            .status-reserved {{ color: #2980b9; font-weight: bold; }}
        </style>
    </head>
    <body>
        <h1>📚 Könyvtári Adatbázis Katalógus</h1>
        <p class="subtitle">Készült: {date.today().strftime('%Y.%m.%d')} | Összes elem: {len(books)} db</p>
        <table>
            <thead>
                <tr>
                    <th>Leltári szám</th>
                    <th>Cím</th>
                    <th>Szerző</th>
                    <th>Kategória</th>
                    <th>Kiadás</th>
                    <th>Státusz</th>
                </tr>
            </thead>
            <tbody>
    """
    for b in books:
        st_val = b.get('status', '')
        status_class = "status-available" if st_val == "Elérhető" else ("status-borrowed" if st_val == "Kölcsönözve" else "status-reserved")
        html_content += f"""
                <tr>
                    <td><b>{b.get('inventory_number', '')}</b></td>
                    <td>{b.get('title', '')}</td>
                    <td>{b.get('author', '')}</td>
                    <td>{b.get('category', '')}</td>
                    <td>{b.get('year', '')}</td>
                    <td class="{status_class}">{st_val}</td>
                </tr>
        """
    html_content += """
            </tbody>
        </table>
    </body>
    </html>
    """
    return html_content

# --- NAVIGÁCIÓS OLDALSÁV ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3389/3389081.png", width=70)
    st.title("Könyvtári Rendszer")
    
    if st.session_state.is_admin:
        st.success("🔑 Adminisztrátor Mód")
        menu_options = [
            "📊 Vezérlőpult", 
            "📚 Katalógus & Kereső", 
            "🔄 Kölcsönzési Pult", 
            "⚙️ Állomány Kezelése", 
            "📜 Adatbázis Listázása"
        ]
    else:
        st.info("👤 Olvasói Nézet")
        menu_options = [
            "📚 Katalógus & Kereső", 
            "🔑 Admin Bejelentkezés"
        ]
        
    menu = st.radio("📌 Menü kiválasztása", menu_options)
    
    st.divider()
    if st.session_state.is_admin:
        if st.button("🚪 Kijelentkezés (Admin)", type="secondary", use_container_width=True):
            st.session_state.is_admin = False
            st.rerun()

# ---------------------------------------------------------
# 1. VEZÉRLŐPULT (Csak Admin)
# ---------------------------------------------------------
if menu == "📊 Vezérlőpult" and st.session_state.is_admin:
    st.header("📊 Rendszer Áttekintés")
    
    total_books = len(st.session_state.books)
    available_books = sum(1 for b in st.session_state.books if b["status"] == "Elérhető")
    reserved_books = sum(1 for b in st.session_state.books if b["status"] == "Félretéve")
    borrowed_books = sum(1 for b in st.session_state.books if b["status"] == "Kölcsönözve")
    overdue_books = sum(1 for b in st.session_state.books if b["status"] == "Kölcsönözve" and is_overdue(b["due_date"]))

    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Összes Könyv", total_books)
    m2.metric("🟢 Elérhető", available_books)
    m3.metric("🔵 Félretéve", reserved_books)
    m4.metric("🟡 Kölcsönözve", borrowed_books)
    m5.metric("🔴 Késésben", overdue_books, delta="- Intézkedés!" if overdue_books > 0 else "Rendben", delta_color="inverse")

    st.divider()

    if reserved_books > 0:
        st.subheader("📌 Félretételi Kérések")
        st.caption("A félretett könyvek azonnal kikölcsönözhetők vagy törölhetők:")
        
        for b in st.session_state.books:
            if b["status"] == "Félretéve":
                with st.expander(f"📖 [{b['inventory_number']}] {b['title']} — Olvasó: {b.get('reserved_by', 'Ismeretlen')}", expanded=True):
                    col_info, col_act = st.columns([2, 1])
                    with col_info:
                        st.markdown(f"**✍️ Szerző:** {b['author']}")
                        st.markdown(f"**👤 Olvasó neve:** {b.get('reserved_by', '-')}")
                        st.markdown(f"**📞 Elérhetőség:** {b.get('reservation_contact', '-')}")
                        st.markdown(f"**📅 Kérés dátuma:** {b.get('reservation_date', '-')}")
                    
                    with col_act:
                        if st.button("✅ Kölcsönzés Rögzítése", key=f"dash_borrow_{b['id']}", type="primary", use_container_width=True):
                            b["status"] = "Kölcsönözve"
                            b["borrower"] = b.get("reserved_by", "")
                            b["borrow_date"] = str(date.today())
                            b["due_date"] = str(date.today() + timedelta(days=14))
                            b["reserved_by"] = ""
                            b["reservation_contact"] = ""
                            b["reservation_date"] = ""
                            save_data(st.session_state.books)
                            st.success(f"A(z) '{b['title']}' kiadva {b['borrower']} részére!")
                            st.rerun()
                        
                        if st.button("❌ Félretétel Törlése", key=f"dash_cancel_{b['id']}", type="secondary", use_container_width=True):
                            b["status"] = "Elérhető"
                            b["reserved_by"] = ""
                            b["reservation_contact"] = ""
                            b["reservation_date"] = ""
                            save_data(st.session_state.books)
                            st.warning("Félretétel törölve.")
                            st.rerun()

    st.subheader("⚠️ Figyelmeztetések")
    if overdue_books > 0:
        st.error(f"**{overdue_books} db könyv lejárt határidejű!**")
        for b in st.session_state.books:
            if b["status"] == "Kölcsönözve" and is_overdue(b["due_date"]):
                st.warning(f"📖 **[{b['inventory_number']}] {b['title']}**\n\n👤 Kölcsönző: {b['borrower']}\n\n⏳ Lejárt: {b['due_date']}")
    else:
        st.success("🎉 Nincs lejárt határidejű kölcsönzés!")

# ---------------------------------------------------------
# 2. KATALÓGUS & KERESŐ
# ---------------------------------------------------------
elif menu == "📚 Katalógus & Kereső":
    st.title("📚 Könyvtári Katalógus")
    
    search_term = st.text_input("🔍 Kereső", placeholder="Írd be a könyv címét, szerzőjét vagy kategóriáját...", key="catalog_search")

    col_f1, col_f2 = st.columns(2)
    categories = ["Összes kategória"] + sorted(list(set(b["category"] for b in st.session_state.books if b.get("category"))))
    selected_cat = col_f1.selectbox("🏷️ Kategória", categories)
    status_filter = col_f2.selectbox("📌 Státusz szűrő", ["Mindegyik", "🟢 Csak az Elérhetők", "🔵 Félretettek", "🟡 Kölcsönözöttek"])

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

    if selected_cat != "Összes kategória":
        filtered_books = [b for b in filtered_books if b.get("category") == selected_cat]

    if status_filter == "🟢 Csak az Elérhetők":
        filtered_books = [b for b in filtered_books if b["status"] == "Elérhető"]
    elif status_filter == "🔵 Félretettek":
        filtered_books = [b for b in filtered_books if b["status"] == "Félretéve"]
    elif status_filter == "🟡 Kölcsönözöttek":
        filtered_books = [b for b in filtered_books if b["status"] == "Kölcsönözve"]

    st.divider()

    # NÉZET VÁLTÓ - Az ALAPÉRTELMEZETT Nézet a TÁBLÁZAT
    view_mode = st.radio("📱 Megjelenítés módja:", ["📊 Táblázat Nézet", "🎴 Mobil Kártya Nézet"], index=0, horizontal=True)

    if not filtered_books:
        st.info("🔍 Nincs a keresési feltételeknek megfelelő könyv.")
    else:
        # --- A) TÁBLÁZAT NÉZET (ALAPÉRTELMEZETT) ---
        if view_mode == "📊 Táblázat Nézet":
            cols = ["inventory_number", "title", "author", "category", "year", "status"]
            col_names = ["Leltári szám", "Cím", "Szerző", "Kategória", "Kiadás", "Státusz"]

            df_show = pd.DataFrame(filtered_books)[cols]
            df_show.columns = col_names
            
            event = st.dataframe(
                df_show, 
                use_container_width=True, 
                hide_index=True,
                on_select="rerun",
                selection_mode="single-row"
            )

            # Kiválasztott könyv részletei a táblázat alatt
            selected_rows = event.selection.rows
            if selected_rows:
                selected_idx = selected_rows[0]
                selected_book = filtered_books[selected_idx]

                st.divider()
                st.subheader(f"📖 {selected_book['title']}")
                st.write(f"✍️ **Szerző:** {selected_book['author']}")
                st.write(f"🏷️ **Kategória:** {selected_book['category']} ({selected_book['year']})")
                st.write(f"📌 **Státusz:** {selected_book['status']}")

                if selected_book['status'] == "Elérhető":
                    with st.expander("📌 Könyv Félretétele / Előjegyzése", expanded=True):
                        with st.form(key=f"reserve_form_tbl_{selected_book['id']}"):
                            res_name = st.text_input("Olvasó Neve*")
                            res_contact = st.text_input("Elérhetőség (Telefonszám / E-mail)*")
                            if st.form_submit_button("📌 Félretétel Kérése", type="primary", use_container_width=True):
                                if res_name.strip() and res_contact.strip():
                                    selected_book["status"] = "Félretéve"
                                    selected_book["reserved_by"] = res_name.strip()
                                    selected_book["reservation_contact"] = res_contact.strip()
                                    selected_book["reservation_date"] = str(date.today())
                                    save_data(st.session_state.books)
                                    st.success(f"Köszönjük, {res_name.strip()}! A könyvet félretettük számodra.")
                                    st.rerun()
                                else:
                                    st.error("A név és az elérhetőség megadása is kötelező!")

        # --- B) MOBIL KÁRTYA NÉZET (CSAK CÍM ÉS ÍRÓ) ---
        else:
            st.caption(f"Találatok száma: {len(filtered_books)} db")
            
            for b in filtered_books:
                with st.container(border=True):
                    # KIZÁRÓLAG CÍM ÉS ÍRÓ (SZERZŐ) JELENIK MEG
                    st.markdown(f"### {b['title']}")
                    st.markdown(f"✍️ **{b['author']}**")

                    # Félretételi gomb és űrlap, ha a könyv elérhető
                    if b['status'] == "Elérhető":
                        with st.expander("📌 **Könyv Félretétele**", expanded=False):
                            with st.form(key=f"card_reserve_form_{b['id']}"):
                                r_name = st.text_input("Neved*", key=f"rn_{b['id']}")
                                r_contact = st.text_input("Telefonszámod vagy E-mail címed*", key=f"rc_{b['id']}")
                                
                                if st.form_submit_button("✅ Félretétel Beküldése", type="primary", use_container_width=True):
                                    if r_name.strip() and r_contact.strip():
                                        b["status"] = "Félretéve"
                                        b["reserved_by"] = r_name.strip()
                                        b["reservation_contact"] = r_contact.strip()
                                        b["reservation_date"] = str(date.today())
                                        save_data(st.session_state.books)
                                        st.success(f"Köszönjük {r_name.strip()}! A könyvet félretettük neked.")
                                        st.rerun()
                                    else:
                                        st.error("Kérjük, adja meg a nevét és elérhetőségét!")
                    elif b['status'] == "Félretéve":
                        st.caption("🔵 _Jelenleg félretéve_")
                    elif b['status'] == "Kölcsönözve":
                        st.caption("🟡 _Jelenleg kikölcsönözve_")

# ---------------------------------------------------------
# 3. ADMIN BEJELENTKEZÉS
# ---------------------------------------------------------
elif menu == "🔑 Admin Bejelentkezés":
    st.header("🔑 Adminisztrátori Bejelentkezés")
    st.write("A könyvtár kezeléséhez jelentkezzen be!")

    with st.form("admin_login_form"):
        input_password = st.text_input("Jelszó", type="password", placeholder="Adja meg a jelszót...")
        submit_button = st.form_submit_button("Bejelentkezés Adminként", type="primary", use_container_width=True)

        if submit_button:
            if input_password == PASSWORD:
                st.session_state.is_admin = True
                st.success("Sikeres belépés adminként!")
                st.rerun()
            else:
                st.error("Hibás jelszó! Próbálja újra.")

# ---------------------------------------------------------
# 4. KÖLCSÖNZÉSI PULT (Csak Admin)
# ---------------------------------------------------------
elif menu == "🔄 Kölcsönzési Pult" and st.session_state.is_admin:
    st.header("🔄 Kölcsönzés és Visszavétel")
    st.write("Gyors adminisztrációs felület a napi könyvforgalomhoz.")

    if not st.session_state.books:
        st.warning("A könyvtár üres!")
    else:
        book_options = {f"[{b['inventory_number']}] {b['title']} ({b['status']})": b["id"] for b in st.session_state.books}
        selected_label = st.selectbox("📖 Válassz egy könyvet:", ["-- Válassz --"] + list(book_options.keys()))
        
        if selected_label != "-- Válassz --":
            selected_id = book_options[selected_label]
            current_book = next(b for b in st.session_state.books if b["id"] == selected_id)
            
            st.divider()
            
            if current_book["status"] == "Elérhető":
                st.subheader("📤 Új Kölcsönzés Rögzítése")
                with st.form("borrow_form"):
                    borrower = st.text_input("👤 Kölcsönző Neve*")
                    col1, col2 = st.columns(2)
                    borrow_d = col1.date_input("📅 Kölcsönzés Dátuma", value=date.today())
                    due_d = col2.date_input("⏳ Várható Visszahozatal", value=date.today() + timedelta(days=14))
                    
                    if st.form_submit_button("✅ Kölcsönzés Jóváhagyása", type="primary", use_container_width=True):
                        if borrower.strip():
                            current_book["status"] = "Kölcsönözve"
                            current_book["borrower"] = borrower.strip()
                            current_book["borrow_date"] = str(borrow_d)
                            current_book["due_date"] = str(due_d)
                            save_data(st.session_state.books)
                            st.success(f"Könyv kiadva {borrower.strip()} számára!")
                            st.rerun()
                        else:
                            st.error("A kölcsönző nevét kötelező megadni!")

            elif current_book["status"] == "Félretéve":
                st.subheader("📌 Félretett Könyv Kezelése")
                st.info(f"**Olvasó:** {current_book.get('reserved_by', '-')}\n\n**Elérhetőség:** {current_book.get('reservation_contact', '-')}\n\n**Kérés dátuma:** {current_book.get('reservation_date', '-')}")
                
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("✅ Kiadás Kölcsönzésbe", type="primary", use_container_width=True):
                        current_book["status"] = "Kölcsönözve"
                        current_book["borrower"] = current_book.get("reserved_by", "")
                        current_book["borrow_date"] = str(date.today())
                        current_book["due_date"] = str(date.today() + timedelta(days=14))
                        current_book["reserved_by"] = ""
                        current_book["reservation_contact"] = ""
                        current_book["reservation_date"] = ""
                        save_data(st.session_state.books)
                        st.success("Sikeresen átfordítva kölcsönzésbe!")
                        st.rerun()
                with c2:
                    if st.button("❌ Félretétel Mégsem", use_container_width=True):
                        current_book["status"] = "Elérhető"
                        current_book["reserved_by"] = ""
                        current_book["reservation_contact"] = ""
                        current_book["reservation_date"] = ""
                        save_data(st.session_state.books)
                        st.warning("Félretétel törölve.")
                        st.rerun()

            else:
                st.subheader("📥 Könyv Visszavétele")
                is_late = is_overdue(current_book["due_date"])
                
                st.info(f"**Leltári szám:** {current_book['inventory_number']}\n\n**Kölcsönző:** {current_book['borrower']}\n\n**Elvitte:** {current_book['borrow_date']}\n\n**Határidő:** {current_book['due_date']}")
                if is_late:
                    st.error("⚠️ Figyelem! A könyvet késve hozták vissza!")
                
                if st.button("🔄 Visszavétel Rögzítése (Újra Elérhető)", type="primary", use_container_width=True):
                    current_book["status"] = "Elérhető"
                    current_book["borrower"] = ""
                    current_book["borrow_date"] = ""
                    current_book["due_date"] = ""
                    save_data(st.session_state.books)
                    st.success("Visszavétel rögzítve!")
                    st.rerun()

# ---------------------------------------------------------
# 5. ÁLLOMÁNY KEZELÉSE (Csak Admin)
# ---------------------------------------------------------
elif menu == "⚙️ Állomány Kezelése" and st.session_state.is_admin:
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
            
            st.subheader("Extra adatok")
            description = st.text_area("Rövid leírás / Szinopszis")
            
            if st.form_submit_button("💾 Könyv Hozzáadása a Katalógushoz", type="primary", use_container_width=True):
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
                        "description": description,
                        "reserved_by": "",
                        "reservation_contact": "",
                        "reservation_date": ""
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
                    
                    if st.form_submit_button("💾 Módosítások Mentése", use_container_width=True):
                        cb["inventory_number"] = e_inv.strip()
                        cb["title"], cb["author"], cb["category"], cb["year"] = e_title, e_author, e_cat, int(e_year)
                        cb["description"] = e_desc
                        save_data(st.session_state.books)
                        st.success("Frissítve!")
                        st.rerun()
                
                st.divider()
                if st.button("❌ Könyv Végleges Törlése", type="primary", use_container_width=True):
                    st.session_state.books = [b for b in st.session_state.books if b["id"] != selected_id]
                    save_data(st.session_state.books)
                    st.warning("Könyv törölve!")
                    st.rerun()

# ---------------------------------------------------------
# 6. ADATBÁZIS LISTÁZÁSA (A Mentés menüpont helyett)
# ---------------------------------------------------------
elif menu == "📜 Adatbázis Listázása" and st.session_state.is_admin:
    st.header("📜 Katalógus Listázása és Exportálása")
    st.write("Tekintsd meg a teljes könyvtári állományt, vagy töltsd le nyomtatható formátumban.")
    
    if st.session_state.books:
        # Teljes állomány táblázatos kilistázása
        df_list = pd.DataFrame(st.session_state.books)[["inventory_number", "title", "author", "category", "year", "status"]]
        df_list.columns = ["Leltári szám", "Cím", "Szerző", "Kategória", "Kiadás", "Státusz"]
        
        st.dataframe(df_list, use_container_width=True, hide_index=True)
        
        st.divider()
        html_data = generate_html_report(st.session_state.books)
        
        st.download_button(
            label="📄 Katalógus Lista Letöltése (Nyomtatható PDF / HTML)",
            data=html_data,
            file_name=f"konyvtar_katalogus_{date.today()}.html",
            mime="text/html",
            type="primary",
            use_container_width=True
        )
    else:
        st.warning("Az adatbázis üres, nincs mit listázni.")