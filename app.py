import streamlit as st
import pandas as pd
import re

# --- 1. AYARLAR VE VERİ YÜKLEME ---
st.set_page_config(page_title="Şarkı Yazarı Stüdyosu v4", layout="wide")

@st.cache_data # Performans artırıcı: Dosyayı her seferinde tekrar okumasın, hafızada tutsun.
@st.cache_data 
def veri_yukle():
    try:
        # DEĞİŞEN KISIM BURASI: Artık CSV değil Parquet okuyoruz
        df_csv = pd.read_parquet("kelimeler.parquet")
        
        # Olası boşlukları dolduralım (Güvenlik önlemi)
        df_csv = df_csv.fillna("-")
        return df_csv
    except Exception as e:
        # Eğer dosya yoksa veya hata varsa boş dön
        return pd.DataFrame()

# Veriyi yükle
ham_veri = veri_yukle()

if ham_veri.empty:
    st.error("⚠️ 'kelimeler.parquet' dosyası bulunamadı! Lütfen GitHub'a dosyayı yüklediğinden emin ol.")
    st.stop()

# --- 2. GELİŞMİŞ ANALİZ MOTORU ---
def detayli_analiz(kayit):
    kelime = str(kayit["kelime"]).lower() # Garanti olsun diye string'e çevir
    unluler = "aeıioöuü"
    
    kelime_unluler = [h for h in kelime if h in unluler]
    ses_haritasi = "-".join(kelime_unluler)
    
    return {
        "Kelime": kayit["kelime"],
        "Anlam": kayit["anlam"],
        "Tür": kayit["tur"],
        "Duygu": kayit["duygu"],
        "Eş Anlam": kayit["es_anlam"],
        "Vurgu": kayit["vurgu"],
        "Hece": len(kelime_unluler), # Hece sayısını otomatik hesapla
        "Ses Haritası": ses_haritasi,
        "Son Harf": kelime[-1] if len(kelime) > 0 else "",
        "Baş Harf": kelime[0] if len(kelime) > 0 else ""
    }

# CSV'deki her satırı analiz motorundan geçir
df = pd.DataFrame([detayli_analiz(row) for index, row in ham_veri.iterrows()])

# --- 3. ARAYÜZ ---
st.title("🎹 Şarkı Yazarı Stüdyosu v4")
st.markdown("---")

# Yan Panel
st.sidebar.header("🎛️ Mikser")

# 1. TEMEL FİLTRELER
with st.sidebar.expander("Temel Ayarlar", expanded=True):
    # Türleri CSV'den otomatik öğren
    secilen_turler = st.multiselect("Kelime Türü", df["Tür"].unique())
    
    # Hece sayısını dinamik yap (En az ve en çok heceyi veriden bul)
    min_hece = int(df["Hece"].min())
    max_hece = int(df["Hece"].max())
    hece_araligi = st.slider("Hece Sayısı", min_hece, max_hece, (min_hece, max_hece))
    
    duygu_modu = st.multiselect("Duygu Modu", df["Duygu"].unique())

# 2. SES ve FONETİK
with st.sidebar.expander("Ses ve Fonetik (Gelişmiş)", expanded=True):
    col_a, col_b = st.columns(2)
    with col_a:
        bas_harf = st.text_input("Baş Harf", placeholder="Örn: s").lower()
    with col_b:
        son_harf = st.text_input("Son Harf", placeholder="Örn: a").lower()
    
    st.markdown("**Ters Köşe Kafiye (Assonance)**")
    ses_yapisi = st.text_input("Sesli Harita", placeholder="Örn: a-e", help="İçindeki seslileri sırasıyla yazın.")
    
    st.markdown("**Prozodi (Vurgu Yeri)**")
    vurgu_secimi = st.radio("Vurgu Nerede Olsun?", ["Farketmez", "Son", "İlk"], horizontal=True)

# 3. JOKER ARAMA
st.sidebar.subheader("🧩 Joker Arama")
joker = st.sidebar.text_input("Desen", placeholder="Örn: k**a")

def joker_kontrol(kelime, desen):
    if len(kelime) != len(desen): return False
    regex = desen.replace("*", ".")
    return bool(re.match(f"^{regex}$", str(kelime).lower()))

# --- 4. FİLTRELEME MANTIĞI ---
sonuc = df.copy()

if secilen_turler: sonuc = sonuc[sonuc["Tür"].isin(secilen_turler)]
sonuc = sonuc[(sonuc["Hece"] >= hece_araligi[0]) & (sonuc["Hece"] <= hece_araligi[1])]
if duygu_modu: sonuc = sonuc[sonuc["Duygu"].isin(duygu_modu)]
if bas_harf: sonuc = sonuc[sonuc["Kelime"].str.startswith(bas_harf)]
if son_harf: sonuc = sonuc[sonuc["Kelime"].str.endswith(son_harf)]
if ses_yapisi: sonuc = sonuc[sonuc["Ses Haritası"] == ses_yapisi]
if vurgu_secimi != "Farketmez": sonuc = sonuc[sonuc["Vurgu"] == vurgu_secimi]
if joker: sonuc = sonuc[sonuc["Kelime"].apply(lambda x: joker_kontrol(x, joker))]

# --- 5. EKRAN GÖRÜNTÜSÜ ---
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader(f"Bulunan Kelimeler ({len(sonuc)})")
    st.dataframe(
        sonuc[["Kelime", "Hece", "Tür", "Duygu", "Vurgu"]], 
        use_container_width=True, 
        height=450
    )

with col2:
    st.subheader("🔍 Hızlı İncele")
    if not sonuc.empty:
        secilen_kelime = st.selectbox("Detay Kartı:", sonuc["Kelime"].tolist(), index=0)
        bilgi = sonuc[sonuc["Kelime"] == secilen_kelime].iloc[0]
        
        st.info(f"**{str(bilgi['Kelime']).upper()}**")
        st.write(f"📖 **Anlam:** {bilgi['Anlam']}")
        st.write(f"🔄 **Eş Anlam:** {bilgi['Eş Anlam']}")
        st.write(f"🏷️ **Tür:** {bilgi['Tür']}")
        st.markdown("---")
        st.write(f"🎼 **Vurgu:** {bilgi['Vurgu']} hecede")
        st.write(f"🎹 **Tını:** {bilgi['Ses Haritası']}")
    else:
        st.warning("Kriterlere uygun kelime yok.")
