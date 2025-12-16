import streamlit as st
import pandas as pd

# --- 1. AYARLAR VE VERİTABANI ---
st.set_page_config(page_title="Şarkı Yazarı Sözlüğü", layout="wide")

# Şimdilik örnek veri havuzumuz (Burası on binlerce kelime ile dolacak)
kelime_listesi = [
    "elma", "armut", "kelime", "melankolik", "anadolu", "aşk", "hüzün", 
    "ghostlamak", "selfie", "anksiyete", "bedbaht", "müphem", "lalettayin",
    "yeknesak", "özgürlük", "gece", "karanlık", "yıldız", "deniz", "martı",
    "gönül", "seda", "baki", "rüzgar", "esinti", "fırtına", "sessizlik",
    "kalem", "kağıt", "nota", "melodi", "ritim", "kafiye"
]

# --- 2. FONKSİYONLAR (UYGULAMANIN BEYNİ) ---
def kelime_analizi(kelime):
    unluler = "aeıioöuü"
    kalin_unluler = "aıou"
    ince_unluler = "eiöü"
    
    kelime = kelime.lower()
    kelime_unluler = [h for h in kelime if h in unluler]
    
    return {
        "Kelime": kelime,
        "Harf Sayısı": len(kelime),
        "Hece Sayısı": len(kelime_unluler), # Türkçede ünlü sayısı = hece sayısı
        "Son Harf": kelime[-1],
        "Baş Harf": kelime[0],
        "Ünlü Yapısı": "Karışık" if (any(h in kalin_unluler for h in kelime_unluler) and any(h in ince_unluler for h in kelime_unluler)) else ("Kalın" if any(h in kalin_unluler for h in kelime_unluler) else "İnce")
    }

# Tüm kelimeleri analiz et ve tabloya dök
veri = [kelime_analizi(k) for k in kelime_listesi]
df = pd.DataFrame(veri)

# --- 3. ARAYÜZ (EKRANDA GÖRECEĞİN KISIM) ---
st.title("🎵 Şarkı Yazarı Asistanı")
st.markdown("*İlham tıkandığında doğru kelimeyi bul.*")

# Yan Panel (Filtreler)
st.sidebar.header("Filtreleme Seçenekleri")

# Şifre Koruması (Basit)
sifre = st.sidebar.text_input("Şifre", type="password")
if sifre != "beste123":
    st.warning("Lütfen sözlüğü kullanmak için şifreyi girin.")
    st.stop()

# Filtreler
hece_secimi = st.sidebar.multiselect("Hece Sayısı", sorted(df["Hece Sayısı"].unique()))
unlu_yapisi = st.sidebar.selectbox("Ünlü Uyumu (Tını)", ["Hepsi", "Kalın", "İnce", "Karışık"])
bas_harf = st.sidebar.text_input("Şu harf(ler)le başlasın (Örn: k, me)", "").lower()
son_harf = st.sidebar.text_input("Şu harf(ler)le bitsin (Örn: a, r)", "").lower()

# --- 4. FİLTRELEME MANTIĞI ---
filtrelenmis_df = df.copy()

if hece_secimi:
    filtrelenmis_df = filtrelenmis_df[filtrelenmis_df["Hece Sayısı"].isin(hece_secimi)]

if unlu_yapisi != "Hepsi":
    filtrelenmis_df = filtrelenmis_df[filtrelenmis_df["Ünlü Yapısı"] == unlu_yapisi]

if bas_harf:
    filtrelenmis_df = filtrelenmis_df[filtrelenmis_df["Kelime"].str.startswith(bas_harf)]

if son_harf:
    filtrelenmis_df = filtrelenmis_df[filtrelenmis_df["Kelime"].str.endswith(son_harf)]

# --- 5. SONUÇLARI GÖSTER ---
st.success(f"Toplam {len(filtrelenmis_df)} kelime bulundu.")
st.dataframe(filtrelenmis_df, use_container_width=True)

# İlham Kutusu
if not filtrelenmis_df.empty:
    rastgele = filtrelenmis_df.sample(1).iloc[0]["Kelime"]
    st.info(f"💡 İlham Önerisi: **{rastgele}** kelimesini denemeye ne dersin?")
