import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime, date
import uuid

# --- OLDAL BEÁLLÍTÁSA ---
st.set_page_config(
    page_title="Könyvtári Rendszer",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- LETISZTULT MODERN STÍLUS (CSS) ---
st.markdown("""
<style>
    html, body, [class*="css"] {
        font-family: 'Segoe UI', -apple-system, Roboto, sans-serif !important;
    }
    
    .stApp {
        background-color: #F8F9FA;
    }

    /* Kártya stílus */
    .book-card {
        background-color: #FFFFFF;
        border: 1px solid #E0E0E0;
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 16px;
        box-shadow: 0px 2px 5px rgba(0,0,0,0.04);
    }

    /* Gombok finomhangolása */
    .stButton > button {
        border-radius: 6px !important;
        font-weight: 600 !important;
        width: 100% !important;
    }

    /* Státusz jelvények */
    .badge-ok {
        background-color: #D1E7DD; color: #0F5132; padding: 4px 10px; border-radius: 8px; font-weight: 600; font-size: 0.85em;
    }
    .badge-out {
        background-color: #FFF3CD; color: #664D03; padding: 4px 10px; border-radius: 8px; font-weight: 600; font-size: 0.85em;
    }
    .badge-res {
        background-color: #CFF4FC; color: #055160; padding: 4px 10px; border-radius: 8px; font-weight: 600; font-size: 0.85em;
    }
</style>
""", unsafe_allow_html=True)

# --- OSZLOPDEFINÍCIÓK ---
COLUMNS = [
    "id", "inventory_number", "title", "author", "category",
    "year", "status", "borrower", "borrow_date", "due_date",
    "cover_url", "description", "reserved_by", "reservation_contact", "reservation_date"
]

# Google Sheets Kapcsolat
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    """Adatok betöltése Google Táblázatból."""
    try:
        df = conn.read(ttl="0d")
        if df is None or df.empty:
            return pd.DataFrame(columns=COLUMNS)
        for col in COLUMNS:
            if col not in df.columns:
                df[col] = ""
        df = df.fillna("")
        return df.astype(str)
    except Exception as e:
        st.error(f"Hiba az adatok betöltésekor: {e}")
        return pd.DataFrame(columns=COLUMNS)

def save_data(df):
    """Adatok elmentése Google Táblázatba."""
    try:
        df_to_save = df.fillna("").astype(str)
        conn.update(data=df_to_save)
        st.cache_data.clear()
        return True
    except Exception as e:
        st.error(f"Hiba a mentéskor: {e}")
        return False

# Adatok betöltése
df = load_data()

# --- OLDALSÁV (SZEREPKÖR VÁLASZTÓ) ---
st.sidebar.title("📚 Könyvtári Rendszer")
role = st.sidebar.radio("Válassz felületet:", ["👁️ Olvasói felület", "⚙️ Adminisztrátori felület"])

# Admin jelszó ellenőrzés
admin_authenticated = False
if role == "⚙️ Adminisztrátori felület":
    admin_password = st.sidebar.text_input("Admin jelszó", type="password")
    if admin_password == "admin123":  # Alapértelmezett jelszó
        admin_authenticated = True
        st.sidebar.success("Sikeres bejelentkezés!")
    else:
        st.sidebar.info("Próbáld a jelszót: `admin123`")

st.sidebar.write("---")
if st.sidebar.button("🔄 Adatok frissítése"):
    st.cache_data.clear()
    st.rerun()

# ==========================================
# 1. OLVASÓI FELÜLET
# ==========================================
if role == "👁️ Olvasói felület":
    st.title("📖 Könyvtári Katalógus")
    st.caption("Böngéssz a könyvek között, és foglald le a neked tetszőt!")

    # Gyors kereső
    col_s1, col_s2 = st.columns([3, 1])
    search = col_s1.text_input("🔍 Keresés (Cím, Szerző, Leltári szám)", placeholder="Írj be egy kifejezést...")
    
    categories = ["Összes"] + sorted(list(set(df['category'].dropna().unique()))) if not df.empty else ["Összes"]
    cat_filter = col_s2.selectbox("Kategória", categories)

    # Szűrés
    filtered = df.copy()
    if search:
        s = search.lower()
        filtered = filtered[
            filtered['title'].str.lower().str.contains(s, na=False) |
            filtered['author'].str.lower().str.contains(s, na=False) |
            filtered['inventory_number'].str.lower().str.contains(s, na=False)
        ]
    if cat_filter != "Összes":
        filtered = filtered[filtered['category'] == cat_filter]

    st.write(f"**Találatok száma:** {len(filtered)} db")
    st.write("---")

    # Kártyák megjelenítése
    if filtered.empty:
        st.info("Nem található a keresésnek megfelelő könyv.")
    else:
        for _, row in filtered.iterrows():
            st.markdown('<div class="book-card">', unsafe_allow_html=True)
            col_img, col_info, col_act = st.columns([1, 3, 1.5])
            
            with col_img:
                if row['cover_url'] and row['cover_url'].startswith("http"):
                    st.image(row['cover_url'], use_container_width=True)
                else:
                    st.markdown("📖 *Nincs kép*")

            with col_info:
                st.markdown(f"### {row['title']}")
                st.markdown(f"**Szerző:** {row['author']} | **Év:** {row['year']} | **Kategória:** {row['category']}")
                
                status = row['status'] if row['status'] else "Kölcsönözhető"
                if status == "Kölcsönözhető":
                    st.markdown('<span class="badge-ok">Kölcsönözhető</span>', unsafe_allow_html=True)
                elif status == "Kölcsönözve":
                    st.markdown('<span class="badge-out">Kölcsönözve</span>', unsafe_allow_html=True)
                elif status == "Foglalva":
                    st.markdown('<span class="badge-res">Foglalva</span>', unsafe_allow_html=True)

                if row['description']:
                    st.caption(row['description'])

            with col_act:
                book_id = row['id']
                real_idx = df[df['id'] == book_id].index[0]

                # Foglalás opció olvasóknak
                if status == "Kölcsönözhető":
                    with st.popover("📌 Foglalás"):
                        st.markdown(f"**Foglalás:** {row['title']}")
                        res_name = st.text_input("Neved *", key=f"rname_{book_id}")
                        res_contact = st.text_input("E-mail / Telefon *", key=f"rcont_{book_id}")
                        
                        if st.button("Foglalás Véglegesítése", key=f"rbtn_{book_id}"):
                            if not res_name or not res_contact:
                                st.warning("Kérjük add meg az adataidat!")
                            else:
                                df.loc[real_idx, 'status'] = "Foglalva"
                                df.loc[real_idx, 'reserved_by'] = res_name
                                df.loc[real_idx, 'reservation_contact'] = res_contact
                                df.loc[real_idx, 'reservation_date'] = str(date.today())
                                
                                if save_data(df):
                                    st.success("Sikeres foglalás!")
                                    st.rerun()
                elif status == "Foglalva":
                    st.caption(f"Foglalta: {row['reserved_by']}")
                else:
                    st.caption(f"Várható visszahozatal: {row['due_date']}")

            st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 2. ADMINISZTRÁTORI FELÜLET
# ==========================================
else:
    if not admin_authenticated:
        st.warning("🔒 Az Adminisztrátori felület használatához jelentkezz be a bal oldali sávban!")
        st.stop()

    st.title("⚙️ Adminisztrációs Központ")
    
    # Statisztikai mutatók
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Összes könyv", len(df))
    c2.metric("Kölcsönözhető", len(df[df['status'] == 'Kölcsönözhető']))
    c3.metric("Kölcsönözve", len(df[df['status'] == 'Kölcsönözve']))
    c4.metric("Foglalva", len(df[df['status'] == 'Foglalva']))

    admin_tab1, admin_tab2, admin_tab3 = st.tabs([
        "⚡ Kölcsönzés & Visszahozatal", 
        "➕ Új Könyv Felvétele", 
        "📊 Adatbázis & Export"
    ])

    # TAB 1: Kölcsönzés és Visszahozatal
    with admin_tab1:
        st.subheader("Könyvek kezelése")
        admin_search = st.text_input("Keresés adminisztrációhoz", placeholder="Cím vagy Leltári szám...")
        
        adm_filtered = df.copy()
        if admin_search:
            s = admin_search.lower()
            adm_filtered = adm_filtered[
                adm_filtered['title'].str.lower().str.contains(s, na=False) |
                adm_filtered['inventory_number'].str.lower().str.contains(s, na=False)
            ]

        for _, row in adm_filtered.iterrows():
            st.markdown('<div class="book-card">', unsafe_allow_html=True)
            col_a, col_b, col_c = st.columns([1, 3, 2])
            
            with col_a:
                st.write(f"**ID:** `{row['inventory_number']}`")
            
            with col_b:
                st.markdown(f"**{row['title']}** - *{row['author']}*")
                status = row['status'] if row['status'] else "Kölcsönözhető"
                
                if status == "Kölcsönözve":
                    st.caption(f"❌ Kölcsönözve: **{row['borrower']}** | Határidő: **{row['due_date']}**")
                elif status == "Foglalva":
                    st.caption(f"📌 Foglaló: **{row['reserved_by']}** ({row['reservation_contact']})")
                else:
                    st.caption("✅ Elérhető a könyvtárban")

            with col_c:
                book_id = row['id']
                real_idx = df[df['id'] == book_id].index[0]

                if status == "Kölcsönözve":
                    if st.button("📥 Visszahozatal", key=f"adm_ret_{book_id}"):
                        df.loc[real_idx, 'status'] = "Kölcsönözhető"
                        df.loc[real_idx, 'borrower'] = ""
                        df.loc[real_idx, 'borrow_date'] = ""
                        df.loc[real_idx, 'due_date'] = ""
                        if save_data(df):
                            st.success("Könyv visszavéve!")
                            st.rerun()
                else:
                    with st.popover("📤 Kölcsönzés"):
                        st.markdown(f"**Kölcsönzés:** {row['title']}")
                        borrower_input = st.text_input("Kölcsönző neve", value=row['reserved_by'], key=f"abname_{book_id}")
                        due_date_input = st.date_input("Visszahozatali határidő", key=f"addate_{book_id}")
                        
                        if st.button("Rögzítés", key=f"abtn_{book_id}"):
                            if borrower_input:
                                df.loc[real_idx, 'status'] = "Kölcsönözve"
                                df.loc[real_idx, 'borrower'] = borrower_input
                                df.loc[real_idx, 'borrow_date'] = str(date.today())
                                df.loc[real_idx, 'due_date'] = str(due_date_input)
                                df.loc[real_idx, 'reserved_by'] = ""
                                df.loc[real_idx, 'reservation_contact'] = ""
                                if save_data(df):
                                    st.success("Kölcsönzés rögzítve!")
                                    st.rerun()

            st.markdown('</div>', unsafe_allow_html=True)

    # TAB 2: Új könyv hozzáadása
    with admin_tab2:
        st.subheader("Új könyv felvétele")
        with st.form("add_form", clear_on_submit=True):
            f1, f2 = st.columns(2)
            inv_num = f1.text_input("Leltári szám *")
            title = f1.text_input("Könyv címe *")
            author = f1.text_input("Szerző *")
            category = f1.text_input("Kategória")
            
            year = f2.text_input("Kiadási év")
            cover_url = f2.text_input("Borítókép URL")
            description = f2.text_area("Leírás")

            if st.form_submit_button("💾 Mentés Google Táblázatba"):
                if inv_num and title and author:
                    new_id = str(uuid.uuid4())[:8]
                    new_row = {
                        "id": new_id, "inventory_number": inv_num, "title": title,
                        "author": author, "category": category if category else "Egyéb",
                        "year": year, "status": "Kölcsönözhető", "borrower": "",
                        "borrow_date": "", "due_date": "", "cover_url": cover_url,
                        "description": description, "reserved_by": "",
                        "reservation_contact": "", "reservation_date": ""
                    }
                    updated_df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                    if save_data(updated_df):
                        st.success("Könyv sikeresen hozzáadva!")
                        st.rerun()
                else:
                    st.warning("Töltsd ki a kötelező mezőket (*)")

    # TAB 3: Teljes adatbázis & Export
    with admin_tab3:
        st.subheader("Teljes Adatbázis")
        st.dataframe(df, use_container_width=True)
        
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Adatok letöltése CSV-ként", csv, f"konyvtar_{date.today()}.csv", "text/csv")