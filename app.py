import streamlit as st
import pandas as pd

st.set_page_config(page_title="Şarkı Yazarı Stüdyosu v7", layout="wide")

@st.cache_data
def veri_yukle():
    try:
        df_csv = pd.read_parquet("kelimeler.parquet")
        df_csv = df_csv.fillna("-")
        return df_csv
    except Exception:
        return pd.DataFrame()

# Veriyi yükle
ham_veri = veri_yukle()

if ham_veri.empty:
    st.error("⚠️ Veri yüklenemedi! GitHub'a 'kelimeler.parquet' dosyasını yüklediğinden emin ol.")
    st.stop()

# Dinamik Sınırlar (Hatayı önlemek için veriden okuyoruz)
MIN_HECE = int(ham_veri["hece"].min())
MAX_HECE = int(ham_veri["hece"].max())

# Filtreleri Temizleme Fonksiyonu
def filtreleri_temizle():
    # Session state'i güvenli şekilde sıfırla
    if "kelime_turu" in st.session_state: st.session_state.kelime_turu = []
    if "hece_sayisi" in st.session_state: st.session_state.hece_sayisi = (MIN_HECE, MAX_HECE)
    if "duygu_modu" in st.session_state: st.session_state.duygu_modu = []
    if "bas_harf" in st.session_state: st.session_state.bas_harf = ""
    if "son_harf" in st.session_state: st.session_state.son_harf = ""
    if "ters_kose" in st.session_state: st.session_state.ters_kose = ""
    if "sesli_harita" in st.session_state: st.session_state.sesli_harita = ""
    if "vurgu_yeri" in st.session_state: st.session_state.vurgu_yeri = "Farketmez"
    if "joker_desen" in st.session_state: st.session_state.joker_desen = ""
    if "sayfa_no" in st.session_state: st.session_state.sayfa_no = 0

# Ses analizi (Anlık)
if "ses_haritasi" not in ham_veri.columns:
    ham_veri["ses_haritasi"] = ham_veri["kelime"].apply(lambda x: "-".join([h for h in str(x).lower() if h in "aeıioöuü"]))

# --- ARAYÜZ ---
with st.sidebar:
    st.header("🎹 Mikser")
    st.button("🧹 Filtreleri Temizle", on_click=filtreleri_temizle, type="primary")
    st.markdown("---")

    with st.expander("🔻 Temel Ayarlar", expanded=True):
        secilen_turler = st.multiselect("Kelime Türü", options=ham_veri["tur"].unique(), key="kelime_turu")
        secilen_hece = st.slider("Hece Sayısı", MIN_HECE, MAX_HECE, (MIN_HECE, MAX_HECE), key="hece_sayisi")
        secilen_duygu = st.multiselect("Duygu Modu", options=ham_veri["duygu"].unique(), key="duygu_modu")

    with st.expander("🗣️ Ses ve Fonetik", expanded=False):
        c1, c2 = st.columns(2)
        bas_harf = c1.text_input("Baş Harf", key="bas_harf").lower()
        son_harf = c2.text_input("Son Harf", key="son_harf").lower()
        ters_kose = st.text_input("Ters Köşe (Assonance)", placeholder="Örn: ü-ü", key="ters_kose").lower()
        sesli_harita_input = st.text_input("Sesli Harita", placeholder="Örn: a-e", key="sesli_harita").lower()

    with st.expander("🥁 Prozodi", expanded=False):
        vurgu_secimi = st.radio("Vurgu", ["Farketmez", "Son", "İlk"], key="vurgu_yeri")

    st.markdown("---")
    joker_desen = st.text_input("🧩 Joker Arama", placeholder="Örn: k**a", key="joker_desen").lower()

# --- FİLTRELEME ---
df = ham_veri.copy()

if secilen_turler: df = df[df["tur"].isin(secilen_turler)]
df = df[(df["hece"] >= secilen_hece[0]) & (df["hece"] <= secilen_hece[1])]
if secilen_duygu: df = df[df["duygu"].isin(secilen_duygu)]
if bas_harf: df = df[df["kelime"].str.startswith(bas_harf)]
if son_harf: df = df[df["kelime"].str.endswith(son_harf)]
if ters_kose: df = df[df["ses_haritasi"].str.endswith(ters_kose)]
if sesli_harita_input: df = df[df["ses_haritasi"] == sesli_harita_input]
if vurgu_secimi != "Farketmez": df = df[df["vurgu"].str.contains(vurgu_secimi, case=False)]
if joker_desen:
    regex = "^" + joker_desen.replace("*", ".") + "$"
    try: df = df[df["kelime"].str.match(regex, na=False)]
    except: pass

# --- SAYFALAMA SİSTEMİ ---
sonuc_sayisi = len(df)
SAYFA_LIMITE = 100

if "sayfa_no" not in st.session_state: st.session_state.sayfa_no = 0

# Filtre değişince başa dön
if sonuc_sayisi < st.session_state.sayfa_no * SAYFA_LIMITE:
    st.session_state.sayfa_no = 0

toplam_sayfa = max(1, (sonuc_sayisi + SAYFA_LIMITE - 1) // SAYFA_LIMITE)
baslangic = st.session_state.sayfa_no * SAYFA_LIMITE
bitis = min(sonuc_sayisi, baslangic + SAYFA_LIMITE)

gosterilecek_df = df.iloc[baslangic:bitis]

# --- SONUÇ GÖSTERİMİ ---
st.title("🎹 Şarkı Yazarı Stüdyosu v7")
st.caption(f"Toplam {sonuc_sayisi} kelime bulundu. (Sayfa {st.session_state.sayfa_no + 1} / {toplam_sayfa})")

c_tablo, c_detay = st.columns([1.5, 1])

with c_tablo:
    st.dataframe(gosterilecek_df[["kelime", "hece", "tur", "vurgu"]], use_container_width=True, height=500)
    
    # Sayfa Butonları
    col_prev, col_info, col_next = st.columns([1, 2, 1])
    if col_prev.button("⬅️ Önceki Sayfa") and st.session_state.sayfa_no > 0:
        st.session_state.sayfa_no -= 1
        st.rerun()
    
    if col_next.button("Sonraki Sayfa ➡️") and (st.session_state.sayfa_no + 1) < toplam_sayfa:
        st.session_state.sayfa_no += 1
        st.rerun()

with c_detay:
    st.markdown("### 🔍 Hızlı İncele")
    if not gosterilecek_df.empty:
        secilen = st.selectbox("Detay Kartı:", gosterilecek_df["kelime"].tolist())
        detay = ham_veri[ham_veri["kelime"] == secilen].iloc[0]
        st.info(f"### {detay['kelime'].upper()}")
        st.write(f"📖 **Anlam:** {detay['anlam']}")
        st.write(f"🏷️ **Tür:** {detay['tur']}")
        st.markdown("---")
        st.write(f"🎼 **Vurgu:** {detay['vurgu']} hecede")
        st.write(f"🎹 **Tını:** {detay['ses_haritasi']}")
    else:
        st.warning("Sonuç bulunamadı.")
