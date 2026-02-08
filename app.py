import streamlit as st
import pandas as pd

# --- KONFİGÜRASYON ---
st.set_page_config(page_title="Emlak Yatırım Hesap Uygulaması", page_icon="🏠", layout="wide")

# --- STİL ---
st.markdown("""
    <style>
    .stMetric { background-color: #f0f2f6; padding: 15px; border-radius: 10px; }
    .stButton>button { width: 100%; background-color: #007BFF; color: white; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- VERİ SETİ ---
sehir_verileri = {
    "Adana (Çukurova)": 15, "Mersin (Yenişehir)": 16, "İstanbul": 21, 
    "Ankara": 18, "İzmir": 20, "Antalya": 17, "Bursa": 19, "Diğer": 18
}

# --- BAŞLIK ---
st.title("🏛️ Emlak Yatırım Hesap Uygulaması")
st.markdown("### *Yatırımın Duygusu Olmaz, Matematiği Olur.*")

# --- GİRDİ PANELİ ---
with st.sidebar:
    st.header("📍 İlan Detayları")
    sehir = st.selectbox("Şehir/Bölge Seçiniz:", list(sehir_verileri.keys()))
    fiyat = st.number_input("Satış Fiyatı (TL)", min_value=0, value=6000000, step=50000)
    kira = st.number_input("Aylık Kira Getirisi (TL)", min_value=1, value=30000, step=1000)
    
    st.divider()
    st.header("📉 Giderler & Vergi")
    aidat = st.number_input("Aylık Aidat/Bakım (TL)", value=1000)
    vergi_orani = st.slider("Gelir Vergisi Tahmini (%)", 0, 35, 15)

# --- ANALİZ MOTORU ---
brut_carpan_ay = fiyat / kira
brut_carpan_yil = brut_carpan_ay / 12
net_aylik_gelir = kira - aidat - (kira * vergi_orani / 100)
net_carpan_yil = fiyat / (net_aylik_gelir * 12)

# --- ANA EKRAN: METRİKLER ---
c1, c2, c3, c4 = st.columns(4)
c1.metric("Brüt Amortisman", f"{brut_carpan_yil:.1f} Yıl")
c2.metric("Net Amortisman", f"{net_carpan_yil:.1f} Yıl")
c3.metric("Yıllık Verim (Brüt)", f"%{(12/brut_carpan_ay)*100:.1f}")
c4.metric("Net Aylık Akış", f"{net_aylik_gelir:,.0f} TL")

st.divider()

# --- 🚦 5 DAKİKA KURALI & PAZARLIK ROBOTU ---
l_col, r_col = st.columns(2)

with l_col:
    st.subheader("🚦 Yatırım Kararı (5 Dakika Kuralı)")
    if brut_carpan_ay < 144:
        st.success("🟢 MÜKEMMEL YATIRIM: Görseldeki kriterlere göre en üst segment.")
    elif 144 <= brut_carpan_ay < 168:
        st.warning("🟡 İYİ YATIRIM: Makul ve güvenli bir liman.")
    elif 168 <= brut_carpan_ay < 220:
        st.info("🟠 ORTA YATIRIM: Sınırda. Pazarlık şart.")
    else:
        st.error("🔴 RİSKLİ YATIRIM: Amortisman süresi çok uzun, nakit akışı zayıf.")

with r_col:
    st.subheader("🎯 Pazarlık Optimizasyonu")
    hedef_yil = 14 # 'İyi' kategorisi için hedef
    ideal_fiyat = kira * 12 * hedef_yil
    if fiyat > ideal_fiyat:
        fark = fiyat - ideal_fiyat
        st.error(f"Pazarlık Hedefi: -{fark:,.0f} TL")
        st.write(f"Mülkü **{ideal_fiyat:,.0f} TL** seviyesine çekmelisiniz.")
    else:
        st.success("Fiyat zaten ideal yatırım seviyesinde!")

# --- UYARI VE PROJEKSİYON ---
st.divider()
st.subheader("⚠️ Kritik Yatırımcı Notları")
st.info(f"""
- **Bölge Kıyaslaması:** {sehir} ortalaması {sehir_verileri[sehir]} yıl. Sizin yatırımınız {brut_carpan_yil:.1f} yıl. 
- **Boş Kalma Riski:** Analiz 12 ay doluluk varsayar. Risk yönetimi için 11 ay üzerinden hesap yapmayı unutmayın.
- **Enflasyon Etkisi:** Türkiye şartlarında kira artışları amortisman süresini kağıt üzerinde kısaltabilir ancak bakım maliyetlerini de artırır.
""")

