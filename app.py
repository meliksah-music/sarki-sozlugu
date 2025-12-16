import streamlit as st
import pandas as pd
import re # Joker aramalar için regex kütüphanesi

# --- 1. AYARLAR VE GELİŞMİŞ VERİTABANI ---
st.set_page_config(page_title="Şarkı Yazarı Sözlüğü Pro", layout="wide")

# BURASI ÖNEMLİ: Artık kelimeler sadece isim değil, özellikleri olan nesneler.
# Not: Bu listeyi ileride Excel'den otomatik çekeceğiz, şimdilik örnekler var.
kelime_veritabani = [
    {"kelime": "seda", "anlam": "Ses, yankı.", "tur": "İsim", "duygu": "Nötr", "es_anlam": "ses, avaz"},
    {"kelime": "bedbaht", "anlam": "Mutsuz, bahtsız.", "tur": "Sıfat", "duygu": "Melankolik", "es_anlam": "talihsiz"},
    {"kelime": "hey", "anlam": "Seslenme sözü.", "tur": "Nida", "duygu": "Coşkulu", "es_anlam": "-"},
    {"kelime": "yakamoz", "anlam": "Denizde balıkların veya küreklerin kımıldanışıyla oluşan parıltı.", "tur": "İsim", "duygu": "Romantik", "es_anlam": "parıltı"},
    {"kelime": "ah", "anlam": "Acı, üzüntü veya özlem anlatan ses.", "tur": "Nida", "duygu": "Melankolik", "es_anlam": "feryat"},
    {"kelime": "müphem", "anlam": "Belirsiz.", "tur": "Sıfat", "duygu": "Gizemli", "es_anlam": "belirsiz"},
    {"kelime": "ghostlamak", "anlam": "Bir ilişkiyi aniden, habersizce kesmek.", "tur": "Fiil (Argo)", "duygu": "Modern/Negatif", "es_anlam": "yok olmak"},
    {"kelime": "efkar", "anlam": "Üzüntülü düşünceler.", "tur": "İsim", "duygu": "Melankolik", "es_anlam": "tasa, keder"},
    {"kelime": "karanfil", "anlam": "Kokulu bir çiçek.", "tur": "İsim", "duygu": "Romantik", "es_anlam": "-"},
    {"kelime": "baki", "anlam": "Sürekli, kalıcı.", "tur": "Sıfat", "duygu": "Ciddi", "es_anlam": "ebedi"},
    {"kelime": "şayet", "anlam": "Eğer.", "tur": "Bağlaç", "duygu": "Nötr", "es_anlam": "eğer, ise"},
    {"kelime": "vuslat", "anlam": "Sevgiliye kavuşma.", "tur": "İsim", "duygu": "Romantik", "es_anlam": "kavuşma"}
]

# --- 2. GELİŞMİŞ ANALİZ MOTORU ---
def detayli_analiz(kayit):
    kelime = kayit["kelime"].lower()
    unluler = "aeıioöuü"
    kalin_unluler = "aıou"
    ince_unluler = "eiöü"
    sert_unsuzler = "fstkçşhp"
    
    kelime_unluler = [h for h in kelime if h in unluler]
    
    # Sesli harf haritası (Ters köşe kafiye için: 'kalem' -> 'a-e')
    ses_haritasi = "-".join(kelime_unluler)
    
    return {
        "Kelime": kayit["kelime"], # Orijinal hali
        "Anlam": kayit["anlam"],
        "Tür": kayit["tur"],
        "Duygu": kayit["duygu"],
        "Eş Anlam": kayit["es_anlam"],
        "Hece": len(kelime_unluler),
        "Harf": len(kelime),
        "Son Harf": kelime[-1],
        "Ses Haritası": ses_haritasi, # Örn: a-e, ü-i
        "Yapı": "Sert" if any(h in sert_unsuzler for h in kelime) else "Yumuşak"
    }

# Veriyi işle
df = pd.DataFrame([detayli_analiz(k) for k in kelime_veritabani])

# --- 3. YENİ ARAYÜZ ---
st.title("🎹 Şarkı Yazarı Stüdyosu v2")
st.markdown("---")

# Yan Panel (Gelişmiş Filtreler)
st.sidebar.header("🎛️ Mikser (Filtreler)")

# 1. TEMEL FİLTRELER
with st.sidebar.expander("Temel Ayarlar", expanded=True):
    secilen_turler = st.multiselect("Kelime Türü", df["Tür"].unique())
    hece_araligi = st.slider("Hece Sayısı", 1, 10, (1, 5))
    duygu_modu = st.multiselect("Duygu Modu", df["Duygu"].unique())

# 2. FONETİK FİLTRELER
with st.sidebar.expander("Ses ve Fonetik"):
    ses_yapisi = st.text_input("Sesli Harf Haritası (Örn: a-e)", help="Sadece 'a' ve 'e' seslilerini içerenleri bulmak için a-e yazın.")
    son_harf = st.text_input("Son Harf", "").lower()

# 3. JOKER ARAMA (YENİ!)
st.sidebar.subheader("🧩 Joker Arama")
joker = st.sidebar.text_input("Desen (Örn: k**a)", help="Bilinmeyen harfler için * kullanın. Örn: k**a (4 harfli, k ile başlar a ile biter)")

# --- 4. FİLTRELEME MANTIĞI ---
sonuc = df.copy()

# Tür Filtresi
if secilen_turler:
    sonuc = sonuc[sonuc["Tür"].isin(secilen_turler)]

# Hece Filtresi
sonuc = sonuc[(sonuc["Hece"] >= hece_araligi[0]) & (sonuc["Hece"] <= hece_araligi[1])]

# Duygu Filtresi
if duygu_modu:
    sonuc = sonuc[sonuc["Duygu"].isin(duygu_modu)]

# Ses Haritası (Assonance)
if ses_yapisi:
    sonuc = sonuc[sonuc["Ses Haritası"] == ses_yapisi]

# Son Harf
if son_harf:
    sonuc = sonuc[sonuc["Kelime"].str.endswith(son_harf)]

# Joker Filtreleme Fonksiyonu
def joker_kontrol(kelime, desen):
    if len(kelime) != len(desen): return False
    regex = desen.replace("*", ".") # * karakterini regex nokta (.) ile değiştir
    return bool(re.match(f"^{regex}$", kelime))

if joker:
    sonuc = sonuc[sonuc["Kelime"].apply(lambda x: joker_kontrol(x, joker))]

# --- 5. EKRAN GÖRÜNTÜSÜ VE DETAYLAR ---

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader(f"Bulunan Kelimeler ({len(sonuc)})")
    st.dataframe(
        sonuc[["Kelime", "Hece", "Tür", "Duygu", "Ses Haritası"]], 
        use_container_width=True,
        height=400
    )

with col2:
    st.subheader("🔍 Kelime İncele")
    if not sonuc.empty:
        secilen_kelime = st.selectbox("Detayına bakmak istediğin kelime:", sonuc["Kelime"].tolist())
        
        # Seçilen kelimenin bilgilerini çek
        bilgi = sonuc[sonuc["Kelime"] == secilen_kelime].iloc[0]
        
        st.info(f"**{bilgi['Kelime'].upper()}**")
        st.markdown(f"**Anlam:** {bilgi['Anlam']}")
        st.markdown(f"**Eş Anlam:** {bilgi['Eş Anlam']}")
        st.markdown(f"**Tür:** {bilgi['Tür']}")
        
        st.markdown("---")
        st.caption("Müzikal Analiz:")
        st.text(f"Hece: {bilgi['Hece']}")
        st.text(f"Tını: {bilgi['Ses Haritası']} ({bilgi['Yapı']})")
    else:
        st.warning("Bu kriterlere uygun kelime bulunamadı.")
