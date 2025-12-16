import streamlit as st
import pandas as pd
import re

# --- 1. AYARLAR VE VERİTABANI ---
st.set_page_config(page_title="Şarkı Yazarı Stüdyosu v3", layout="wide")

# Veritabanına "Vurgu" özelliğini ekledik
kelime_veritabani = [
    {"kelime": "seda", "anlam": "Ses, yankı.", "tur": "İsim", "duygu": "Nötr", "es_anlam": "ses, avaz", "vurgu": "Son"},
    {"kelime": "bedbaht", "anlam": "Mutsuz, bahtsız.", "tur": "Sıfat", "duygu": "Melankolik", "es_anlam": "talihsiz", "vurgu": "Son"},
    {"kelime": "hey", "anlam": "Seslenme sözü.", "tur": "Nida", "duygu": "Coşkulu", "es_anlam": "-", "vurgu": "İlk"},
    {"kelime": "yakamoz", "anlam": "Denizdeki parıltı.", "tur": "İsim", "duygu": "Romantik", "es_anlam": "parıltı", "vurgu": "Son"},
    {"kelime": "ah", "anlam": "Acı, özlem sesi.", "tur": "Nida", "duygu": "Melankolik", "es_anlam": "feryat", "vurgu": "İlk"},
    {"kelime": "müphem", "anlam": "Belirsiz.", "tur": "Sıfat", "duygu": "Gizemli", "es_anlam": "belirsiz", "vurgu": "Son"},
    {"kelime": "ghostlamak", "anlam": "İletişimi aniden kesmek.", "tur": "Fiil (Argo)", "duygu": "Modern/Negatif", "es_anlam": "yok olmak", "vurgu": "İlk"},
    {"kelime": "efkar", "anlam": "Üzüntülü düşünceler.", "tur": "İsim", "duygu": "Melankolik", "es_anlam": "tasa", "vurgu": "Son"},
    {"kelime": "karanfil", "anlam": "Kokulu çiçek.", "tur": "İsim", "duygu": "Romantik", "es_anlam": "-", "vurgu": "Son"},
    {"kelime": "baki", "anlam": "Kalıcı, sonsuz.", "tur": "Sıfat", "duygu": "Ciddi", "es_anlam": "ebedi", "vurgu": "Son"},
    {"kelime": "masa", "anlam": "Mobilya.", "tur": "İsim", "duygu": "Nötr", "es_anlam": "-", "vurgu": "İlk"},
    {"kelime": "bence", "anlam": "Bana göre.", "tur": "Zarf", "duygu": "Nötr", "es_anlam": "-", "vurgu": "İlk"}
]

# --- 2. GELİŞMİŞ ANALİZ MOTORU ---
def detayli_analiz(kayit):
    kelime = kayit["kelime"].lower()
    unluler = "aeıioöuü"
    sert_unsuzler = "fstkçşhp"
    
    kelime_unluler = [h for h in kelime if h in unluler]
    ses_haritasi = "-".join(kelime_unluler)
    
    return {
        "Kelime": kayit["kelime"],
        "Anlam": kayit["anlam"],
        "Tür": kayit["tur"],
        "Duygu": kayit["duygu"],
        "Eş Anlam": kayit["es_anlam"],
        "Vurgu": kayit["vurgu"],     # YENİ ÖZELLİK
        "Hece": len(kelime_unluler),
        "Ses Haritası": ses_haritasi,
        "Son Harf": kelime[-1],
        "Baş Harf": kelime[0]        # YENİ ÖZELLİK
    }

df = pd.DataFrame([detayli_analiz(k) for k in kelime_veritabani])

# --- 3. ARAYÜZ ---
st.title("🎹 Şarkı Yazarı Stüdyosu v3")
st.markdown("---")

# Yan Panel
st.sidebar.header("🎛️ Mikser")

# 1. TEMEL FİLTRELER
with st.sidebar.expander("Temel Ayarlar", expanded=True):
    secilen_turler = st.multiselect("Kelime Türü", df["Tür"].unique())
    hece_araligi = st.slider("Hece Sayısı", 1, 10, (1, 5))
    duygu_modu = st.multiselect("Duygu Modu", df["Duygu"].unique())

# 2. SES ve FONETİK (GÜNCELLENDİ)
with st.sidebar.expander("Ses ve Fonetik (Gelişmiş)", expanded=True):
    col_a, col_b = st.columns(2)
    with col_a:
        bas_harf = st.text_input("Baş Harf", placeholder="Örn: s").lower()
    with col_b:
        son_harf = st.text_input("Son Harf", placeholder="Örn: a").lower()
    
    # Ters Köşe Kafiye (Assonance)
    st.markdown("**Ters Köşe Kafiye (Assonance)**")
    ses_yapisi = st.text_input("Sesli Harita", placeholder="Örn: a-e (Kalem -> Madem)", help="İçindeki seslileri sırasıyla yazın.")
    
    # Prozodi / Vurgu (YENİ)
    st.markdown("**Prozodi (Vurgu Yeri)**")
    vurgu_secimi = st.radio("Vurgu Nerede Olsun?", ["Farketmez", "Son", "İlk"], horizontal=True)

# 3. JOKER ARAMA
st.sidebar.subheader("🧩 Joker Arama")
joker = st.sidebar.text_input("Desen", placeholder="Örn: k**a")
def joker_kontrol(kelime, desen):
    if len(kelime) != len(desen): return False
    regex = desen.replace("*", ".")
    return bool(re.match(f"^{regex}$", kelime))

# --- 4. FİLTRELEME MANTIĞI ---
sonuc = df.copy()

if secilen_turler: sonuc = sonuc[sonuc["Tür"].isin(secilen_turler)]
sonuc = sonuc[(sonuc["Hece"] >= hece_araligi[0]) & (sonuc["Hece"] <= hece_araligi[1])]
if duygu_modu: sonuc = sonuc[sonuc["Duygu"].isin(duygu_modu)]
if bas_harf: sonuc = sonuc[sonuc["Kelime"].str.startswith(bas_harf)] # Baş harf filtresi
if son_harf: sonuc = sonuc[sonuc["Kelime"].str.endswith(son_harf)]
if ses_yapisi: sonuc = sonuc[sonuc["Ses Haritası"] == ses_yapisi]
if vurgu_secimi != "Farketmez": sonuc = sonuc[sonuc["Vurgu"] == vurgu_secimi] # Vurgu filtresi
if joker: sonuc = sonuc[sonuc["Kelime"].apply(lambda x: joker_kontrol(x, joker))]

# --- 5. EKRAN GÖRÜNTÜSÜ (YENİ TASARIM) ---
col1, col2 = st.columns([2, 1]) # Ekranı 2'ye 1 oranında böl

with col1:
    st.subheader(f"Bulunan Kelimeler ({len(sonuc)})")
    # Tabloyu göster
    st.dataframe(
        sonuc[["Kelime", "Hece", "Tür", "Duygu", "Vurgu"]], 
        use_container_width=True, 
        height=450
    )

with col2:
    st.subheader("🔍 Hızlı İncele")
    
    if not sonuc.empty:
        # AKILLI SEÇİM: Listede ne kaldıysa, kutuda sadece onlar çıkar.
        # Varsayılan olarak listenin en tepesindeki kelime seçili gelir.
        secilen_kelime = st.selectbox(
            "Detay Kartı:", 
            sonuc["Kelime"].tolist(),
            index=0 # Her zaman ilk kelimeyi seçili getir
        )
        
        # Seçilenin detaylarını getir
        bilgi = sonuc[sonuc["Kelime"] == secilen_kelime].iloc[0]
        
        # Kart Tasarımı
        st.info(f"**{bilgi['Kelime'].upper()}**")
        st.write(f"📖 **Anlam:** {bilgi['Anlam']}")
        st.write(f"🔄 **Eş Anlam:** {bilgi['Eş Anlam']}")
        st.write(f"🏷️ **Tür:** {bilgi['Tür']}")
        st.markdown("---")
        st.write(f"🎼 **Vurgu:** {bilgi['Vurgu']} hecede")
        st.write(f"🎹 **Tını:** {bilgi['Ses Haritası']}")
        
    else:
        st.warning("Kriterlere uygun kelime yok.")
