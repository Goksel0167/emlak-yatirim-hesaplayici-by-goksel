import streamlit as st
import requests
import pandas as pd

# --- KONFİGÜRASYON ---
st.set_page_config(page_title="Emlak Vizyoner: Pro Analiz", layout="wide")

# --- TÜRKİYE VERİSİ YÜKLEME (İl ve İlçeler) ---
@st.cache_data
def turkiye_verisi_yukle():
    try:
        # 81 il ve 900+ ilçeyi içeren dinamik JSON kaynağı
        url = "https://raw.githubusercontent.com/fatih/turkiye-iller-ilceler/master/data/data.json"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        st.error(f"Veri yükleme hatası: {e}")
    return []

data = turkiye_verisi_yukle()

# --- ARAYÜZ ---
st.title("🏙️ Emlak Vizyoner: Profesyonel Yatırım Analizi")
st.markdown("---")

# --- YAN PANEL: GİRDİLER ---
with st.sidebar:
    st.header("📍 Konum & Finans")
    
    # Şehir Seçimi
    if data:
        il_isimleri = [item['name'] for item in data]
        secilen_il = st.selectbox("İl Seçiniz:", il_isimleri)
        
        # Hata korumalı ilçe seçimi (Senin aldığın hatanın çözümü burada)
        secilen_il_obj = next((i for i in data if i["name"] == secilen_il), None)
        if secilen_il_obj:
            ilce_isimleri = [ilce['name'] for ilce in secilen_il_obj['towns']]
            secilen_ilce = st.selectbox("İlçe Seçiniz:", ilce_isimleri)
        else:
            secilen_ilce = "Bilinmiyor"
    else:
        st.error("Şehir verileri şu an yüklenemedi.")
        secilen_il = "Bilinmiyor"
        secilen_ilce = "Bilinmiyor"

    st.text_input("Mahalle (Opsiyonel):", placeholder="Örn: Yenişehir / Gazi")
    
    st.divider()
    fiyat = st.number_input("Gayrimenkul Fiyatı (TL):", min_value=100000, value=6000000, step=50000)
    kira = st.number_input("Başlangıç Kirası (TL):", min_value=1000, value=30000, step=1000)
    
    st.divider()
    st.header("📉 Ekonomik Beklentiler")
    senaryo = st.radio("Enflasyon Senaryosu:", ["Dezenflasyon (%33.88)", "Yüksek Enflasyon (%55)"])
    artis_orani = 33.88 if "33.88" in senaryo else 55.00

    st.divider()
    kredi_taksit = st.number_input("Aylık Kredi Taksiti (0 ise nakit):", value=0)
    alternatif_getiri = st.slider("Alternatif Yıllık Faiz (%)", 10, 80, 45)

# --- ANA EKRAN ANALİZ MOTORU ---
if st.button("KAPSAMLI FİZİBİLİTE RAPORUNU OLUŞTUR"):
    # Matematiksel Hesaplamalar
    brut_carpan = fiyat / kira
    yil_amortisman = brut_carpan / 12
    net_aylik_gelir = kira * 0.85 # Vergi ve bakım düşülmüş
    nakit_akisi = net_aylik_gelir - kredi_taksit
    
    # 1. TEMEL METRİKLER
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Kira Çarpanı", f"{brut_carpan:.0f} Ay")
    col2.metric("Amortisman", f"{yil_amortisman:.1f} Yıl")
    col3.metric("Net Nakit Akışı", f"{nakit_akisi:,.0f} TL/Ay")
    col4.metric("Yıllık Net Verim", f"%{(net_aylik_gelir*12/fiyat)*100:.2f}")

    # 2. PROFESYONEL KIYASLAMA
    st.divider()
    c_left, c_right = st.columns(2)
    with c_left:
        st.subheader("⚖️ Alternatif Kıyaslama")
        mulk_verimi = (net_aylik_gelir * 12 / fiyat) * 100
        if mulk_verimi < (alternatif_getiri / 2):
            st.error(f"Kira verimi (%{mulk_verimi:.1f}), alternatif getirinin (%{alternatif_getiri}) çok altında.")
        else:
            st.success(f"Kira verimi (%{mulk_verimi:.1f}) piyasa ile dengeli.")

    with c_right:
        st.subheader("🏦 Finansman Durumu")
        if kredi_taksit > 0:
            if nakit_akisi > 0: st.success(f"Kredi kendi kendine ödeniyor. Kalan: {nakit_akisi:,.0f} TL")
            else: st.error(f"Negatif Akış! Aylık cebinizden çıkacak: {abs(nakit_akisi):,.0f} TL")
        else: st.info("Nakit alım yapıldı, kredi yükü yok.")

    # 3. GELECEK PROJEKSİYONU
    st.divider()
    st.subheader(f"🚀 10 Yıllık {senaryo} Projeksiyonu")
    yillar = list(range(1, 11))
    kira_list = [kira * ((1 + artis_orani/100) ** (y-1)) for y in yillar]
    
    chart_df = pd.DataFrame({
        "Yıl": yillar, 
        "Yıllık Kira (TL)": [k*12 for k in kira_list]
    }).set_index("Yıl")
    st.area_chart(chart_df)

    # 4. STRATEJİK NOTLAR
    st.divider()
    ideal_fiyat = kira * 144
    if fiyat > ideal_fiyat:
        st.warning(f"🎯 **Pazarlık Hedefi:** Görseldeki 'Mükemmel Yatırım' için hedef fiyat **{ideal_fiyat:,.0f} TL** olmalıdır.")
    else:
        st.success("✅ Fiyat, kira getirisine göre oldukça avantajlı seviyede!")
