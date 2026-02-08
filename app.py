import streamlit as st
import requests
import pandas as pd

# --- KONFİGÜRASYON ---
st.set_page_config(page_title="Emlak Vizyoner: Profesyonel Yatırım Analizi", layout="wide")

# --- VERİ ÇEKME (İller & İlçeler) ---
@st.cache_data
def turkiye_verisi_yukle():
    url = "https://raw.githubusercontent.com/fatih/turkiye-iller-ilceler/master/data/data.json"
    response = requests.get(url)
    return response.json() if response.status_code == 200 else {}

data = turkiye_verisi_yukle()

# --- ARAYÜZ: YAN PANEL ---
with st.sidebar:
    st.header("📍 Konum & Finans")
    il_isimleri = [item['name'] for item in data]
    secilen_il = st.selectbox("İl Seçiniz:", il_isimleri)
    ilce_isimleri = [ilce['name'] for ilce in next(i for i in data if i["name"] == secilen_il)['towns']]
    secilen_ilce = st.selectbox("İlçe Seçiniz:", ilce_isimleri)
    
    st.divider()
    fiyat = st.number_input("Gayrimenkul Fiyatı (TL):", min_value=100000, value=6000000)
    kira = st.number_input("Başlangıç Kirası (TL):", min_value=1000, value=30000)
    
    st.divider()
    st.header("📈 Ekonomik Beklentiler")
    senaryo = st.radio("Enflasyon Senaryosu:", ["Dezenflasyon (Normalleşme - %33.88)", "Yüksek Enflasyon (%55)"])
    artis_orani = 33.88 if "Dezenflasyon" in senaryo else 55.00

    st.divider()
    st.header("🏦 Kredi & Alternatif")
    kredi_taksit = st.number_input("Aylık Kredi Taksiti (0 ise nakit):", value=0)
    alternatif_getiri = st.slider("Alternatif Yıllık Faiz/Getiri (%)", 10, 80, 45)

# --- ANA EKRAN ---
st.title("🏙️ Emlak Vizyoner: Profesyonel Analiz Paneli")
st.markdown("---")

if st.button("KAPSAMLI FİZİBİLİTE RAPORUNU ÇALIŞTIR"):
    # Matematiksel Modeller
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

    # 2. PROFESYONEL ANALİZ (ROI VE KIYASLAMA)
    st.divider()
    st.subheader("🏢 Yatırım Verimlilik Analizi")
    c_left, c_right = st.columns(2)
    
    with c_left:
        st.write("### ⚖️ Alternatif Kıyaslama")
        mülk_verim = (net_aylik_gelir * 12 / fiyat) * 100
        if mülk_verim < (alternatif_getiri / 2):
            st.error(f"⚠️ Kira verimi (%{mülk_verim:.1f}), alternatif getirinin (%{alternatif_getiri}) çok altında. Bu yatırımın kârlı olması için mülk değer artışının çok yüksek olması gerekir.")
        else:
            st.success(f"✅ Kira verimi (%{mülk_verim:.1f}) piyasa koşullarına göre dengeli.")

    with c_right:
        st.write("### 🏦 Finansman Durumu")
        if kredi_taksit > 0:
            if nakit_akisi > 0:
                st.success(f"Yatırım Kendi Kredisini Ödüyor. Kalan: {nakit_akisi:,.0f} TL")
            else:
                st.error(f"Negatif Nakit Akışı! Aylık Cebinizden Çıkacak: {abs(nakit_akisi):,.0f} TL")
        else:
            st.info("Nakit alım yapıldı. Kredi yükü bulunmuyor.")

    # 3. GELECEK PROJEKSİYONU
    st.divider()
    st.subheader(f"🚀 10 Yıllık {senaryo} Projeksiyonu")
    yillar = list(range(1, 11))
    kira_list = [kira * ((1 + artis_orani/100) ** (y-1)) for y in yillar]
    birikmis_gelir = []
    toplam = 0
    for k in kira_list:
        toplam += k * 12
        birikmis_gelir.append(toplam)

    chart_df = pd.DataFrame({"Yıl": yillar, "Yıllık Kira (TL)": [k*12 for k in kira_list], "Kümülatif Kazanç": birikmis_gelir}).set_index("Yıl")
    st.area_chart(chart_df["Yıllık Kira (TL)"])
    

    # 4. PAZARLIK ROBOTU (Kullanıcıya Özel Uyarı)
    st.divider()
    st.subheader("🎯 Stratejik Pazarlık Notu")
    ideal_fiyat = kira * 144
    if fiyat > ideal_fiyat:
        st.warning(f"Görseldeki 'Çok İyi Yatırım' seviyesi için fiyat hedefi: **{ideal_fiyat:,.0f} TL**")
        st.info(f"Pazarlık masasında **{fiyat - ideal_fiyat:,.0f} TL** indirim talep etmeniz önerilir.")
    else:
        st.success("Fiyat, kira getirisine göre oldukça avantajlı seviyede!")
