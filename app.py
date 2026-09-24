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
        # Alapértelmezett adatok Leltári számmal
        data = [
            {"id": 1, "inventory_number": "LELT-0001", "title": "A Gyűrűk Ura", "author": "J.R.R. Tolkien", "category": "Fantasy", "year": 1954, "status": "Elérhető", "borrower": "", "borrow_date": "", "due_date": "", "cover_url": "", "description": "Frodó és a Gyűrű Szövetségének epikus útja.", "reserved_by": "", "reservation_contact": "", "reservation_date": ""},
            {"id": 2, "inventory_number": "LELT-0002", "title": "1984", "author": "George Orwell", "category": "Disztópia", "year": 1949, "status": "Kölcsönözve", "borrower": "Kovács Péter", "borrow_date": "2026-03-01", "due_date": "2026-03-15", "cover_url": "", "description": "A Nagy Testvér mindent lát.", "reserved_by": "", "reservation_contact": "", "reservation_date": ""}
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

# --- NYOMTATHATÓ HTML / PDF GENERÁLÓ FÜGGVÉNY ---
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
            @media print {{
                body {{ margin: 0; }}
                @page {{ size: landscape; margin: 1cm; }}
            }}
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
        if st_val == "Elérhető":
            status_class = "status-available"
        elif st_val == "Kölcsönözve":
            status_class = "status-borrowed"
        else:
            status_class = "status-reserved"

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
    st.image("https://cdn-icons-png.flaticon.com/512/3389/3389081.png", width=80)
    st.title("Könyvtári Rendszer")
    
    if st.session_state.is_admin:
        st.success("🔑 Adminisztrátor Mód")
        menu_options = [
            "📊 Vezérlőpult", 
            "📚 Katalógus & Kereső", 
            "🔄 Kölcsönzési Pult", 
            "⚙️ Állomány Kezelése", 
            "💾 Adatbázis Mentése"
        ]
    else:
        st.info("👤 Olvasói / Vendég Nézet")
        menu_options = [
            "📚 Katalógus & Kereső", 
            "🔑 Admin Bejelentkezés"
        ]
        
    menu = st.radio("📌 Menü", menu_options)
    
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
        for b in st.session_state.books:
            if b["status"] == "Félretéve":
                st.info(f"📖 **[{b['inventory_number']}] {b['title']}**\n\n"
                        f"👤 **Olvasó:** {b.get('reserved_by', '-')}\n\n"
                        f"📞 **Elérhetőség:** {b.get('reservation_contact', '-')}\n\n"
                        f"📅 **Kérés dátuma:** {b.get('reservation_date', '-')}")

    st.subheader("⚠️ Figyelmeztetések")
    if overdue_books > 0:
        st.error(f"**{overdue_books} db könyv lejárt határidejű!**")
        for b in st.session_state.books:
            if b["status"] == "Kölcsönözve" and is_overdue(b["due_date"]):
                st.warning(f"📖 **[{b['inventory_number']}] {b['title']}**\n\n👤 {b['borrower']}\n\n⏳ Lejárt: {b['due_date']}")
    else:
        st.success("🎉 Nincs lejárt határidejű kölcsönzés!")

# ---------------------------------------------------------
# 2. KATALÓGUS & KERESŐ (Mindenki számára elérhető)
# ---------------------------------------------------------
elif menu == "📚 Katalógus & Kereső":
    st.header("📚 Könyvtári Katalógus")
    st.caption("Böngéssz a könyvtár állományában! A kereső segítségével könnyen megtalálhatod a kívánt könyvet.")
    
    search_term = st.text_input("🔍 Keresés (Leltári szám, Cím, Szerző, Kategória, Leírás alapján...)", placeholder="Írd be a keresőszót...")
    
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
        st.caption("💡 **Tipp:** Kattints a táblázat bármelyik sorára a könyv részletes adatlapjának megtekintéséhez és a **félretételhez**!")
        
        # Oszlopok összeállítása (Vendég vs Admin)
        if st.session_state.is_admin:
            cols = ["inventory_number", "title", "author", "category", "year", "status", "borrower", "due_date"]
            col_names = ["Leltári szám", "Cím", "Szerző", "Kategória", "Kiadás", "Státusz", "Kölcsönző", "Határidő"]
        else:
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
                
                # Státusz színkódolás
                if selected_book['status'] == "Elérhető":
                    status_color = "green"
                elif selected_book['status'] == "Kölcsönözve":
                    status_color = "orange"
                else:
                    status_color = "blue"
                
                st.markdown(f"**📌 Státusz:** :{status_color}[{selected_book['status']}]")
                st.divider()

                # --- 1. HA KÖLCSÖNÖZVE VAN ---
                if selected_book['status'] == "Kölcsönözve":
                    if st.session_state.is_admin:
                        st.markdown(f"**👤 Kölcsönző:** {selected_book['borrower']}")
                        st.markdown(f"**📅 Dátum:** {selected_book.get('borrow_date', '-')}")
                        st.markdown(f"**⏳ Határidő:** {selected_book['due_date']}")
                        
                        if is_overdue(selected_book['due_date']):
                            st.error("⚠️ Ez a kölcsönzés már lejárt!")

                        if st.button("📥 Kölcsönzés Lezárása (Visszavétel)", type="primary", key=f"return_btn_{selected_book['id']}"):
                            selected_book["status"] = "Elérhető"
                            selected_book["borrower"] = ""
                            selected_book["borrow_date"] = ""
                            selected_book["due_date"] = ""
                            save_data(st.session_state.books)
                            st.success("A kölcsönzés lezárva! A könyv újra elérhető.")
                            st.rerun()

                # --- 2. HA FÉLRETÉVE VAN ---
                elif selected_book['status'] == "Félretéve":
                    if st.session_state.is_admin:
                        st.info(f"📌 **Félretéve az alábbi olvasónak:**\n\n"
                                f"• **Név:** {selected_book.get('reserved_by', '-')}\n\n"
                                f"• **Elérhetőség:** {selected_book.get('reservation_contact', '-')}\n\n"
                                f"• **Foglalás dátuma:** {selected_book.get('reservation_date', '-')}")
                        
                        col_r1, col_r2 = st.columns(2)
                        with col_r1:
                            if st.button("✅ Kölcsönzésbe átfordítás", type="primary", key=f"res_to_borrow_{selected_book['id']}"):
                                selected_book["status"] = "Kölcsönözve"
                                selected_book["borrower"] = selected_book.get("reserved_by", "")
                                selected_book["borrow_date"] = str(date.today())
                                selected_book["due_date"] = str(date.today() + timedelta(days=14))
                                selected_book["reserved_by"] = ""
                                selected_book["reservation_contact"] = ""
                                selected_book["reservation_date"] = ""
                                save_data(st.session_state.books)
                                st.success("Félretett könyv kiadva kölcsönzésbe!")
                                st.rerun()
                        with col_r2:
                            if st.button("❌ Félretétel Törlése", type="secondary", key=f"cancel_res_{selected_book['id']}"):
                                selected_book["status"] = "Elérhető"
                                selected_book["reserved_by"] = ""
                                selected_book["reservation_contact"] = ""
                                selected_book["reservation_date"] = ""
                                save_data(st.session_state.books)
                                st.warning("Félretétel törölve, a könyv újra elérhető.")
                                st.rerun()
                    else:
                        st.warning("📌 Ez a könyv jelenleg fel van téve félre egy olvasó számára.")

                # --- 3. HA ELÉRHE TŐ (FÉLRETÉTEL OLVASÓKNAK / GYORS KIADÁS ADMINNAK) ---
                else:
                    if st.session_state.is_admin:
                        with st.expander("📤 Könyv Kölcsönzése Gyorsan (Admin)"):
                            with st.form(key=f"quick_borrow_{selected_book['id']}"):
                                q_borrower = st.text_input("Kölcsönző Neve*")
                                q_borrow_d = st.date_input("Kölcsönzés Dátuma", value=date.today())
                                q_due_d = st.date_input("Várható Visszahozatal", value=date.today() + timedelta(days=14))
                                
                                if st.form_submit_button("✅ Kiadás Rögzítése"):
                                    if q_borrower.strip():
                                        selected_book["status"] = "Kölcsönözve"
                                        selected_book["borrower"] = q_borrower.strip()
                                        selected_book["borrow_date"] = str(q_borrow_d)
                                        selected_book["due_date"] = str(q_due_d)
                                        save_data(st.session_state.books)
                                        st.success(f"Könyv kiadva {q_borrower.strip()} részére!")
                                        st.rerun()
                                    else:
                                        st.error("A név megadása kötelező!")

                    # OLVASÓI FÉLRETÉTEL ŰRLAP (Vendég és Admin számára is elérhető)
                    with st.expander("📌 Könyv Félretétele / Előjegyzése (Olvasóknak)", expanded=not st.session_state.is_admin):
                        st.write("Tedd félre a könyvet, és a könyvtáros előkészíti neked a személyes átvételhez!")
                        with st.form(key=f"reserve_form_{selected_book['id']}"):
                            res_name = st.text_input("Olvasó Neve*")
                            res_contact = st.text_input("Elérhetőség (Telefonszám / E-mail)*")
                            
                            if st.form_submit_button("📌 Félretétel Kérése", type="primary"):
                                if res_name.strip() and res_contact.strip():
                                    selected_book["status"] = "Félretéve"
                                    selected_book["reserved_by"] = res_name.strip()
                                    selected_book["reservation_contact"] = res_contact.strip()
                                    selected_book["reservation_date"] = str(date.today())
                                    save_data(st.session_state.books)
                                    st.success(f"Köszönjük, {res_name.strip()}! A könyvet félretettük számodra. A könyvtáros felveszi veled a kapcsolatot.")
                                    st.rerun()
                                else:
                                    st.error("A név és az elérhetőség megadása is kötelező!")

            with col2:
                st.markdown("**📝 Leírás / Szinopszis:**")
                if selected_book.get("description"):
                    st.info(selected_book["description"])
                else:
                    st.caption("Nincs leírás megadva ehhez a könyvhöz.")

# ---------------------------------------------------------
# 3. ADMIN BEJELENTKEZÉS (Vendégeknek)
# ---------------------------------------------------------
elif menu == "🔑 Admin Bejelentkezés":
    st.header("🔑 Adminisztrátori Bejelentkezés")
    st.write("A könyvtár kezeléséhez (kölcsönzések rögzítése, új könyvek felvétele, módosítások) kérjük, jelentkezzen be!")

    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        with st.form("admin_login_form"):
            input_password = st.text_input("Jelszó", type="password", placeholder="Adja meg a jelszót...")
            submit_button = st.form_submit_button("Bejelentkezés Adminként", type="primary", use_container_width=True)

            if submit_button:
                if input_password == PASSWORD:
                    st.session_state.is_admin = True
                    st.success("Sikeres belépés adminisztrátorként!")
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

            elif current_book["status"] == "Félretéve":
                st.subheader("📌 Félretett Könyv Kezelése")
                st.info(f"**Olvasó:** {current_book.get('reserved_by', '-')}\n\n**Elérhetőség:** {current_book.get('reservation_contact', '-')}\n\n**Kérés dátuma:** {current_book.get('reservation_date', '-')}")
                
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("✅ Kiadás Kölcsönzésbe", type="primary"):
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
                    if st.button("❌ Félretétel Mégsem"):
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
# 6. ADATBÁZIS MENTÉSE (Csak Admin)
# ---------------------------------------------------------
elif menu == "💾 Adatbázis Mentése" and st.session_state.is_admin:
    st.header("💾 Adatbázis Exportálása PDF-be")
    st.write("Töltsd le a teljes katalógust nyomtatható PDF / HTML formátumban.")
    
    if st.session_state.books:
        html_data = generate_html_report(st.session_state.books)
        
        st.download_button(
            label="📄 Katalógus Letöltése (Nyomtatható PDF)",
            data=html_data,
            file_name=f"konyvtar_katalogus_{date.today()}.html",
            mime="text/html",
            type="primary"
        )
        st.info("💡 **Hogyan mentsd PDF-ként?**\n"
                "1. Kattints a letöltés gombra.\n"
                "2. Nyisd meg a letöltött fájlt a böngésződben (Chrome, Edge, Firefox stb.).\n"
                "3. Nyomd meg a **Ctrl + P** gombot, és válaszd a **'Mentés PDF-ként'** (Save as PDF) opciót.")
    else:
        st.warning("Az adatbázis üres, nincs mit exportálni.")