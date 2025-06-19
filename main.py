import streamlit as st
import requests
import math

# =========================
# Fungsi Harga Real-Time
# =========================
def get_price(token_id):
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={token_id}&vs_currencies=idr"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data.get(token_id, {}).get("idr", None)
    return None

# =========================
# Fungsi APR dari API/aggregator
# =========================
def get_apr_from_defillama(token_name):
    url = "https://yields.llama.fi/yields"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        for item in data:
            if item.get("symbol", "").lower() == token_name.lower():
                return item.get("apy", 0) * 100
    return None

# =========================
# Fungsi Compound
# =========================
def compound_growth(principal, apr_percent, days):
    apr = apr_percent / 100
    daily_rate = apr / 365
    return principal * ((1 + daily_rate) ** days)

# =========================
# Streamlit GUI
# =========================
st.set_page_config(page_title="Simulasi Staking LGNS & AXS", layout="centered")
st.title("📈 Simulasi Profit Staking: LGNS vs AXS")

# Input
rupiah_input = st.text_input("Masukkan jumlah modal dalam Rupiah:", value="10.000.000")
rupiah_input_cleaned = rupiah_input.replace(".", "").replace(",", "")

try:
    modal_rupiah = int(rupiah_input_cleaned)
except ValueError:
    st.error("Format angka tidak valid. Gunakan titik sebagai pemisah ribuan, contoh: 1.000.000")
    st.stop()

# Harga Token
price_lgns = get_price("origin-lgns")
price_axs = get_price("axie-infinity")

if price_lgns is None or price_axs is None:
    st.error("Gagal mengambil data harga token dari CoinGecko.")
    st.stop()

st.markdown(f"💰 Harga **LGNS** saat ini: Rp {price_lgns:,.0f}")
st.markdown(f"💰 Harga **AXS** saat ini: Rp {price_axs:,.0f}")

# Ambil APR dari aggregator (bukan Selenium)
st.subheader("📡 Mengambil APR dari berbagai sumber terpercaya...")
lgns_apr = get_apr_from_defillama("LGNS") or 100.0  # fallback default
axs_apr = get_apr_from_defillama("AXS") or 28.0
atom_apr = get_apr_from_defillama("ATOM") or 19.0
osmo_apr = get_apr_from_defillama("OSMO") or 22.0
eth_apr = get_apr_from_defillama("stETH") or 3.6

st.success(f"APR LGNS: {lgns_apr:.2f}% | APR AXS: {axs_apr:.2f}%")

# =========================
# LGNS Simulation
# =========================
jumlah_lgns = modal_rupiah / price_lgns
hasil_lgns_1d = compound_growth(jumlah_lgns, lgns_apr, 1) * price_lgns
hasil_lgns_7d = compound_growth(jumlah_lgns, lgns_apr, 7) * price_lgns
hasil_lgns_30d = compound_growth(jumlah_lgns, lgns_apr, 30) * price_lgns

st.subheader("🔷 Estimasi Staking LGNS")
st.write(f"Setelah 1 hari: Rp {hasil_lgns_1d:,.0f}")
st.write(f"Setelah 7 hari: Rp {hasil_lgns_7d:,.0f}")
st.write(f"Setelah 30 hari: Rp {hasil_lgns_30d:,.0f}")
st.info("⚠️ **Risiko LGNS**: High-risk. APR tinggi namun tidak stabil. Hindari investasi jangka panjang tanpa riset lanjutan.")

# =========================
# AXS Simulation
# =========================
jumlah_axs = modal_rupiah / price_axs
hasil_axs_1d = compound_growth(jumlah_axs, axs_apr, 1) * price_axs
hasil_axs_7d = compound_growth(jumlah_axs, axs_apr, 7) * price_axs
hasil_axs_30d = compound_growth(jumlah_axs, axs_apr, 30) * price_axs

st.subheader("🟢 Estimasi Staking AXS")
st.write(f"Setelah 1 hari: Rp {hasil_axs_1d:,.0f}")
st.write(f"Setelah 7 hari: Rp {hasil_axs_7d:,.0f}")
st.write(f"Setelah 30 hari: Rp {hasil_axs_30d:,.0f}")
st.info("⚠️ **Risiko AXS**: Moderate. APR stabil dan ekosistem besar. Tetap waspadai volatilitas harga.")

# =========================
# Rekomendasi Tabel
# =========================
rekomendasi = [
    {"Token": "LGNS", "Platform": "Origin DeFi", "APR": f"{lgns_apr:.2f}%", "Risiko": "Tinggi"},
    {"Token": "AXS", "Platform": "Stake.axieinfinity.com", "APR": f"{axs_apr:.2f}%", "Risiko": "Moderat"},
    {"Token": "ATOM", "Platform": "Keplr", "APR": f"{atom_apr:.2f}%", "Risiko": "Moderat"},
    {"Token": "OSMO", "Platform": "Osmosis Zone", "APR": f"{osmo_apr:.2f}%", "Risiko": "Moderat"},
    {"Token": "stETH", "Platform": "Lido Finance", "APR": f"{eth_apr:.2f}%", "Risiko": "Aman"},
]

st.subheader("📊 Top 5 Rekomendasi Staking")
st.table(rekomendasi)

st.caption("📊 Data harga dari CoinGecko. APR dari DefiLlama & sumber terpercaya. Untuk edukasi, bukan nasihat finansial.")
