import streamlit as st
import pandas as pd
import re

# --- 1. AYARLAR VE VERİ YÜKLEME ---
st.set_page_config(page_title="Şarkı Yazarı Stüdyosu v5", layout="wide")

# Filtreleri Temizleme Fonksiyonu (Callback)
def filtreleri_temizle():
    if "kelime_turu" in st.session_state: st.session_state.kelime_turu = []
    if "hece_sayisi" in st.session_state: st.session_state.hece_sayisi = (1, 15)
    if "duygu_modu" in st.session_state: st.session_state.duygu_modu = []
    if "bas_harf" in st.session_state: st.session_state.bas_harf = ""
    if "son_harf" in st.session_state: st.session_state.son_harf = ""
    if "ters_kose" in st.session_state: st.session_state.ters_kose = ""
    if "sesli_harita" in st.session_state: st.session_state.sesli_harita = ""
    if "vurgu_yeri" in st.session_state: st.session_state.vurgu_yeri = "Farketmez"
    if "joker_desen" in st.session_state: st.session_state.joker_desen = ""

@st.cache_data
def veri_yukle():
    try:
        # Parquet formatı ile ultra hızlı okuma
        df_csv = pd.read_parquet("kelimeler.parquet")
        df_csv = df_csv.fillna("-")
        return df_csv
    except Exception as e:
        return pd.DataFrame()

# Veriyi yükle
ham_veri = veri_yukle()

if ham_veri.empty:
    st.error("⚠️ 'kelimeler.parquet' dosyası bulunamadı! Lütfen GitHub'a dosyayı yüklediğinden emin ol.")
    st.stop()

# --- 2. GELİŞMİŞ ANALİZ MOTORU ---
def detayli_analiz(kayit):
    kelime = str(kayit["kelime"]).lower()
    unluler = "aeıioöuü"
    kelime_unluler = [h for h in kelime if h in unluler]
    ses_haritasi = "-".join(kelime_unluler)
    return pd.Series([ses_haritasi], index=['ses_haritasi'])

# Analiz sütununu veri yüklenirken bir kere hesaplayalım (Hız için)
if "ses_haritasi" not in ham_veri.columns:
    analiz_sonuclari = ham_veri.apply(detayli_analiz, axis=1)
    ham_veri = pd.concat([ham_veri, analiz_sonuclari], axis=1)

# --- 3. ARAYÜZ (SOL PANEL) ---
with st.sidebar:
    st.header("🎹 Mikser")
    
    # Temizle Butonu
    st.button("🧹 Filtreleri Temizle", on_click=filtreleri_temizle, type="primary")
    st.markdown("---")

    with st.expander("🔻 Temel Ayarlar", expanded=True):
        secilen_turler = st.multiselect("Kelime Türü", options=ham_veri["tur"].unique(), key="kelime_turu")
        min_h, max_h = int(ham_veri["hece"].min()), int(ham_veri["hece"].max())
        secilen_hece = st.slider("Hece Sayısı", min_h, max_h, (min_h, max_h), key="hece_sayisi")
        secilen_duygu = st.multiselect("Duygu Modu", options=ham_veri["duygu"].unique(), key="duygu_modu")

    with st.expander("🗣️ Ses ve Fonetik", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            bas_harf = st.text_input("Baş Harf", placeholder="Örn: s", key="bas_harf").lower()
        with col2:
            son_harf = st.text_input("Son Harf", placeholder="Örn: a", key="son_harf").lower()
        
        ters_kose = st.text_input("Ters Köşe Kafiye (Assonance)", placeholder="Örn: ü-ü", help="Sadece sesli harfleri eşleştirir (hüzün -> ü-ü)", key="ters_kose").lower()
        sesli_harita_input = st.text_input("Sesli Harita", placeholder="Örn: a-e", help="Tam ünlü sırasını arar (anne -> a-e)", key="sesli_harita").lower()

    with st.expander("🥁 Prozodi (Vurgu Yeri)", expanded=False):
        vurgu_secimi = st.radio("Vurgu Nerede Olsun?", ["Farketmez", "Son", "İlk"], key="vurgu_yeri")

    st.markdown("---")
    st.subheader("🧩 Joker Arama")
    joker_desen = st.text_input("Desen", placeholder="Örn: k**a", help="* işareti herhangi bir harf demektir.", key="joker_desen").lower()

# --- 4. FİLTRELEME MOTORU ---
filtrelenmis_df = ham_veri.copy()

if secilen_turler:
    filtrelenmis_df = filtrelenmis_df[filtrelenmis_df["tur"].isin(secilen_turler)]

filtrelenmis_df = filtrelenmis_df[
    (filtrelenmis_df["hece"] >= secilen_hece[0]) & 
    (filtrelenmis_df["hece"] <= secilen_hece[1])
]

if secilen_duygu:
    filtrelenmis_df = filtrelenmis_df[filtrelenmis_df["duygu"].isin(secilen_duygu)]

if bas_harf:
    filtrelenmis_df = filtrelenmis_df[filtrelenmis_df["kelime"].str.startswith(bas_harf)]

if son_harf:
    filtrelenmis_df = filtrelenmis_df[filtrelenmis_df["kelime"].str.endswith(son_harf)]

if ters_kose:
    filtrelenmis_df = filtrelenmis_df[filtrelenmis_df["ses_haritasi"].str.endswith(ters_kose)]

if sesli_harita_input:
    filtrelenmis_df = filtrelenmis_df[filtrelenmis_df["ses_haritasi"] == sesli_harita_input]

if vurgu_secimi != "Farketmez":
    filtrelenmis_df = filtrelenmis_df[filtrelenmis_df["vurgu"].str.contains(vurgu_secimi, case=False)]

if joker_desen:
    regex_pattern = "^" + joker_desen.replace("*", ".") + "$"
    try:
        filtrelenmis_df = filtrelenmis_df[filtrelenmis_df["kelime"].str.match(regex_pattern, na=False)]
    except:
        st.error("Hatalı desen girişi.")

# --- 5. SONUÇ GÖSTERİMİ ---
st.title("🎹 Şarkı Yazarı Stüdyosu v5")

sonuc_sayisi = len(filtrelenmis_df)

# Hız Ayarı: Çok fazla sonuç varsa sadece ilk 50'yi gösterelim (Tarayıcıyı kitlememek için)
LIMIT = 50 
gosterilecek_df = filtrelenmis_df.head(LIMIT)

st.subheader(f"Bulunan Kelimeler ({sonuc_sayisi})")

if sonuc_sayisi > LIMIT:
    st.caption(f"🚀 Performans için sadece ilk {LIMIT} sonuç gösteriliyor. Daha spesifik filtreleme yapabilirsin.")

col_table, col_detail = st.columns([1.5, 1])

with col_table:
    st.dataframe(
        gosterilecek_df[["kelime", "hece", "tur", "duygu", "vurgu"]], 
        use_container_width=True,
        height=500
    )

with col_detail:
    st.markdown("### 🔍 Hızlı İncele")
    if not gosterilecek_df.empty:
        secilen_kelime_row = st.selectbox("Detay Kartı:", gosterilecek_df["kelime"].tolist())
        detay = ham_veri[ham_veri["kelime"] == secilen_kelime_row].iloc[0]
        
        st.info(f"### {detay['kelime'].upper()}")
        st.write(f"📖 **Anlam:** {detay['anlam']}")
        st.write(f"🔄 **Eş Anlam:** {detay['es_anlam']}")
        st.write(f"🏷️ **Tür:** {detay['tur']}")
        st.markdown("---")
        st.write(f"🎼 **Vurgu:** {detay['vurgu']} hecede")
        st.write(f"🎹 **Tını:** {detay['ses_haritasi'].replace('-', '-')}")
    else:
        st.warning("Kriterlere uygun kelime bulunamadı.")
