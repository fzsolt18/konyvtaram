import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime, date
import uuid

# --- OLDAL BEÁLLÍTÁSA ---
st.set_page_config(
    page_title="Könyvtári Nyilvántartó",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- WINDOWS 11 FLUENT DESIGN STÍLUS (CSS) ---
st.markdown("""
<style>
    /* Segoe UI betűtípus */
    html, body, [class*="css"] {
        font-family: 'Segoe UI Variable Display', 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif !important;
    }
    
    /* Alkalmazás háttér (Mica stílusú lágy szürke) */
    .stApp {
        background-color: #F3F4F6;
    }

    /* Win11 Kártya konténer */
    .win-card {
        background-color: #FFFFFF;
        border: 1px solid #E5E5E5;
        border-radius: 12px;
        padding: 20px 24px;
        box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.03);
        margin-bottom: 20px;
    }

    /* Elsődleges Gombok (Win11 Kék) */
    .stButton > button {
        border-radius: 6px !important;
        background-color: #005FB8 !important;
        color: #FFFFFF !important;
        border: 1px solid #004E98 !important;
        padding: 8px 16px !important;
        font-weight: 600 !important;
        box-shadow: 0px 2px 4px rgba(0, 0, 0, 0.08) !important;
        transition: all 0.15s ease-in-out !important;
        width: 100% !important;
    }

    .stButton > button:hover {
        background-color: #186EBD !important;
        box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.12) !important;
        transform: translateY(-1px);
    }

    /* Szövegbeviteli mezők és lenyíló menük */
    div[data-baseweb="input"], div[data-baseweb="select"] {
        border-radius: 6px !important;
        border: 1px solid #D1D1D1 !important;
        background-color: #FFFFFF !important;
    }
    
    div[data-baseweb="input"]:focus-within {
        border-color: #005FB8 !important;
        box-shadow: 0 0 0 2px rgba(0, 95, 184, 0.2) !important;
    }

    /* Metrika kártyák finomhangolása */
    div[data-testid="stMetric"] {
        background-color: #FFFFFF;
        border: 1px solid #E5E5E5;
        border-radius: 10px;
        padding: 12px 16px;
        box-shadow: 0px 2px 6px rgba(0, 0, 0, 0.02);
    }

    /* Tab fül stílusok */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: transparent;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        padding: 10px 20px;
        background-color: #EAEAEA;
        color: #333333;
        font-weight: 500;
    }

    .stTabs [aria-selected="true"] {
        background-color: #FFFFFF !important;
        color: #005FB8 !important;
        border-top: 3px solid #005FB8 !important;
        font-weight: 600;
    }

    /* Jelvények (Badges) a státuszokhoz */
    .badge-available {
        background-color: #D1E7DD; color: #0F5132; padding: 4px 10px; border-radius: 12px; font-weight: 600; font-size: 0.85em; display: inline-block;
    }
    .badge-borrowed {
        background-color: #FFF3CD; color: #664D03; padding: 4px 10px; border-radius: 12px; font-weight: 600; font-size: 0.85em; display: inline-block;
    }
    .badge-reserved {
        background-color: #CFF4FC; color: #055160; padding: 4px 10px; border-radius: 12px; font-weight: 600; font-size: 0.85em; display: inline-block;
    }
</style>
""", unsafe_allow_html=True)

# --- OSZLOPOK ÉS ADATBÁZIS OSZLOPDEFINÍCIÓK ---
COLUMNS = [
    "id", "inventory_number", "title", "author", "category",
    "year", "status", "borrower", "borrow_date", "due_date",
    "cover_url", "description", "reserved_by", "reservation_contact", "reservation_date"
]

# Google Sheets Kapcsolat
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    """Adatok betöltése a Google Táblázatból."""
    try:
        df = conn.read(ttl="0d")
        if df is None or df.empty:
            return pd.DataFrame(columns=COLUMNS)
        
        # Hiányzó oszlopok pótlása
        for col in COLUMNS:
            if col not in df.columns:
                df[col] = ""
                
        df = df.fillna("")
        return df.astype(str)
    except Exception as e:
        st.error(f"Hiba az adatok betöltésekor: {e}")
        return pd.DataFrame(columns=COLUMNS)

def save_data(df):
    """Adatok elmentése és felülírása a Google Táblázatban."""
    try:
        df_to_save = df.fillna("").astype(str)
        conn.update(data=df_to_save)
        st.cache_data.clear()
        return True
    except Exception as e:
        st.error(f"Hiba a Google Táblázat mentésekor: {e}")
        return False

# Adatok betöltése a munkamenetbe
df = load_data()

# --- FEJLÉC ÉS ÖSSZESÍTŐ METRIKÁK ---
st.title("📚 Könyvtári Nyilvántartó Rendszer")
st.caption("Windows 11 Fluent Design felület & Google Sheets felhőalapú adatbázis")

col_m1, col_m2, col_m3, col_m4 = st.columns(4)
total_books = len(df)
available_books = len(df[df['status'] == 'Kölcsönözhető']) if not df.empty else 0
borrowed_books = len(df[df['status'] == 'Kölcsönözve']) if not df.empty else 0
reserved_books = len(df[df['status'] == 'Foglalva']) if not df.empty else 0

col_m1.metric("Összes könyv", total_books)
col_m2.metric("Kölcsönözhető", available_books)
col_m3.metric("Kölcsönözve", borrowed_books)
col_m4.metric("Foglalva", reserved_books)

st.write("")

# --- FŐ NAVIGÁCIÓS FÜLEK ---
tab_catalog, tab_add, tab_stats = st.tabs([
    "📚 Katalógus & Kereső", 
    "➕ Új könyv hozzáadása", 
    "📊 Statisztika & Beállítások"
])

# ==========================================
# 1. TAB: KATALÓGUS, KERESŐ ÉS GYORS MŰVELETEK
# ==========================================
with tab_catalog:
    st.markdown('<div class="win-card">', unsafe_allow_html=True)
    st.subheader("🔍 Keresés és szűrés")
    
    col_s1, col_s2, col_s3 = st.columns([2, 1, 1])
    search_term = col_s1.text_input("Keresés (Cím, Szerző vagy Leltári szám alapján)", placeholder="Írj be egy keresőszót...")
    
    categories = ["Összes"] + sorted(list(set(df['category'].dropna().unique()))) if not df.empty else ["Összes"]
    selected_category = col_s2.selectbox("Kategória szűrő", categories)
    
    statuses = ["Összes", "Kölcsönözhető", "Kölcsönözve", "Foglalva"]
    selected_status = col_s3.selectbox("Státusz szűrő", statuses)
    st.markdown('</div>', unsafe_allow_html=True)

    # Szűrés lefutása
    filtered_df = df.copy()
    if search_term:
        term = search_term.lower()
        filtered_df = filtered_df[
            filtered_df['title'].str.lower().str.contains(term, na=False) |
            filtered_df['author'].str.lower().str.contains(term, na=False) |
            filtered_df['inventory_number'].str.lower().str.contains(term, na=False)
        ]
    if selected_category != "Összes":
        filtered_df = filtered_df[filtered_df['category'] == selected_category]
    if selected_status != "Összes":
        filtered_df = filtered_df[filtered_df['status'] == selected_status]

    # Könyvek megjelenítése kártyák formájában
    st.subheader(f"Találatok ({len(filtered_df)} db)")
    
    if filtered_df.empty:
        st.info("Nem található a szűrésnek megfelelő könyv.")
    else:
        for idx, row in filtered_df.iterrows():
            st.markdown('<div class="win-card">', unsafe_allow_html=True)
            col_img, col_info, col_actions = st.columns([1, 3, 2])
            
            # 1. Borítókép
            with col_img:
                if row['cover_url'] and row['cover_url'].startswith("http"):
                    st.image(row['cover_url'], use_container_width=True)
                else:
                    st.markdown("📖 *Nincs borító*")
            
            # 2. Könyv adatai
            with col_info:
                st.markdown(f"### {row['title']}")
                st.markdown(f"**Szerző:** {row['author']} | **Év:** {row['year']} | **Kategória:** {row['category']}")
                st.markdown(f"**Leltári szám:** `{row['inventory_number']}`")
                
                # Státusz jelvény
                status = row['status'] if row['status'] else "Kölcsönözhető"
                if status == "Kölcsönözhető":
                    st.markdown('<span class="badge-available">Kölcsönözhető</span>', unsafe_allow_html=True)
                elif status == "Kölcsönözve":
                    st.markdown(f'<span class="badge-borrowed">Kölcsönözve: {row["borrower"]} | Határidő: {row["due_date"]}</span>', unsafe_allow_html=True)
                elif status == "Foglalva":
                    st.markdown(f'<span class="badge-reserved">Foglalva: {row["reserved_by"]}</span>', unsafe_allow_html=True)

                if row['description']:
                    st.caption(f"Leírás: {row['description']}")

            # 3. MŰVELETEK (Kölcsönzés / Visszahozatal közvetlenül a kártyáról)
            with col_actions:
                st.markdown("**⚡ Gyors Művelet:**")
                
                book_id = row['id']
                real_idx = df[df['id'] == book_id].index[0]
                
                # Ha a könyv jelenleg KÖLCSÖNÖZVE van -> Visszahozatal gomb
                if status == "Kölcsönözve":
                    if st.button("📥 Visszahozatal", key=f"ret_{book_id}"):
                        df.loc[real_idx, 'status'] = "Kölcsönözhető"
                        df.loc[real_idx, 'borrower'] = ""
                        df.loc[real_idx, 'borrow_date'] = ""
                        df.loc[real_idx, 'due_date'] = ""
                        
                        if save_data(df):
                            st.success("Könyv sikeresen visszavéve!")
                            st.rerun()

                # Ha a könyv KÖLCSÖNÖZHETŐ vagy FOGLALVA van -> Kölcsönzés ablak
                else:
                    with st.popover("📤 Kölcsönzés"):
                        st.markdown(f"**Kölcsönzés:** *{row['title']}*")
                        borrower_input = st.text_input("Kölcsönző neve *", key=f"bname_{book_id}")
                        due_date_input = st.date_input("Visszahozatali határidő", key=f"ddate_{book_id}")
                        
                        if st.button("Kölcsönzés Rögzítése", key=f"btn_borrow_{book_id}"):
                            if not borrower_input:
                                st.warning("Add meg a kölcsönző nevét!")
                            else:
                                df.loc[real_idx, 'status'] = "Kölcsönözve"
                                df.loc[real_idx, 'borrower'] = borrower_input
                                df.loc[real_idx, 'borrow_date'] = str(date.today())
                                df.loc[real_idx, 'due_date'] = str(due_date_input)
                                
                                if save_data(df):
                                    st.success("Kölcsönzés sikeresen rögzítve!")
                                    st.rerun()

            st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 2. TAB: ÚJ KÖNYV HOZZÁADÁSA
# ==========================================
with tab_add:
    st.markdown('<div class="win-card">', unsafe_allow_html=True)
    st.subheader("➕ Új könyv rögzítése a katalógusba")
    
    with st.form("add_book_form", clear_on_submit=True):
        f_col1, f_col2 = st.columns(2)
        
        inv_num = f_col1.text_input("Leltári szám *", placeholder="pl. L-2024/001")
        title = f_col1.text_input("Könyv címe *", placeholder="pl. A Gyűrűk Ura")
        author = f_col1.text_input("Szerző *", placeholder="pl. J.R.R. Tolkien")
        category = f_col1.text_input("Kategória", placeholder="pl. Regény / Sci-Fi / Történelem")
        
        year = f_col2.text_input("Kiadási év", placeholder="pl. 1954")
        cover_url = f_col2.text_input("Borítókép URL link", placeholder="https://... image.jpg")
        description = f_col2.text_area("Rövid leírás / megjegyzés", placeholder="A könyv rövid tartalma...")
        
        submit_button = st.form_submit_button("💾 Könyv Hozzáadása a Táblázathoz")

        if submit_button:
            if not inv_num or not title or not author:
                st.warning("⚠️ Kérjük, töltsd ki a kötelező mezőket (Leltári szám, Cím, Szerző)!")
            else:
                new_id = str(uuid.uuid4())[:8]
                new_row = {
                    "id": new_id,
                    "inventory_number": inv_num,
                    "title": title,
                    "author": author,
                    "category": category if category else "Egyéb",
                    "year": year,
                    "status": "Kölcsönözhető",
                    "borrower": "",
                    "borrow_date": "",
                    "due_date": "",
                    "cover_url": cover_url,
                    "description": description,
                    "reserved_by": "",
                    "reservation_contact": "",
                    "reservation_date": ""
                }
                
                updated_df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                
                if save_data(updated_df):
                    st.success(f"✅ A(z) **'{title}'** című könyv sikeresen elmentve a Google Táblázatba!")
                    st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 3. TAB: STATISZTIKA ÉS NYERS ADATOK
# ==========================================
with tab_stats:
    st.markdown('<div class="win-card">', unsafe_allow_html=True)
    st.subheader("📊 Könyvtári Adatok és Szinkronizálás")
    
    if st.button("🔄 Adatok Frissítése a Google Táblázatból"):
        st.cache_data.clear()
        st.rerun()

    st.write("---")
    st.markdown("### Nyers Adattáblázat")
    st.dataframe(df, use_container_width=True)
    
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Adatok letöltése CSV fájlként",
        data=csv,
        file_name=f"konyvtar_adatok_{date.today()}.csv",
        mime="text/csv",
    )
    st.markdown('</div>', unsafe_allow_html=True)