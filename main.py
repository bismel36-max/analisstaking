import streamlit as st
import requests
import math
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

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
# Fungsi APR Scraper
# =========================
def get_lgns_apr():
    try:
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        driver = webdriver.Chrome(options=options)
        driver.get("https://app.origindefi.com/stake")
        time.sleep(5)
        apr_element = driver.find_element(By.XPATH, "//div[contains(text(), 'APR')]/following-sibling::div")
        apr_text = apr_element.text.replace('%', '').strip()
        driver.quit()
        return float(apr_text)
    except Exception as e:
        return None

def get_axs_apr():
    try:
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        driver = webdriver.Chrome(options=options)
        driver.get("https://stake.axieinfinity.com/")
        time.sleep(5)
        apr_element = driver.find_element(By.XPATH, "//div[contains(text(), 'APR')]/following-sibling::div")
        apr_text = apr_element.text.replace('%', '').strip()
        driver.quit()
        return float(apr_text)
    except Exception as e:
        return None

# =========================
# Fungsi Compound
# =========================
def compound_growth(principal, rate_per_rebase, rebase_per_day, days):
    total_rebase = rebase_per_day * days
    return principal * ((1 + rate_per_rebase) ** total_rebase)

def compound_growth_apy(principal, apr_percent, days):
    apr = apr_percent / 100
    daily_rate = apr / 365
    return principal * ((1 + daily_rate) ** days)

# =========================
# Rekomendasi Top 5 Staking
# =========================
def get_top_staking_options():
    return [
        {"Token": "LGNS", "Platform": "Origin DeFi", "APR": lgns_apr, "Risiko": "Tinggi"},
        {"Token": "AXS", "Platform": "Stake.axieinfinity.com", "APR": axs_apr, "Risiko": "Moderat"},
        {"Token": "ATOM", "Platform": "Keplr", "APR": 19.0, "Risiko": "Moderat"},
        {"Token": "OSMO", "Platform": "Osmosis Zone", "APR": 45.0, "Risiko": "Tinggi"},
        {"Token": "ETH (LSD)", "Platform": "Lido Finance", "APR": 3.6, "Risiko": "Aman"}
    ]

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

# Ambil APR
st.subheader("📡 Mengambil APR Real-Time...")
lgns_apr = get_lgns_apr()
axs_apr = get_axs_apr()

if lgns_apr is None or axs_apr is None:
    st.warning("Gagal mengambil APR secara real-time. Pastikan koneksi internet dan ChromeDriver tersedia.")
    st.stop()

st.success(f"APR LGNS: {lgns_apr:.2f}% | APR AXS: {axs_apr:.2f}%")

# =========================
# LGNS Simulation
# =========================
jumlah_lgns = modal_rupiah / price_lgns
rebase_per_day = 3
rebase_yield = (lgns_apr / 100) / 365 * rebase_per_day

hasil_lgns_1d = compound_growth(jumlah_lgns, rebase_yield / rebase_per_day, rebase_per_day, 1) * price_lgns
hasil_lgns_7d = compound_growth(jumlah_lgns, rebase_yield / rebase_per_day, rebase_per_day, 7) * price_lgns
hasil_lgns_30d = compound_growth(jumlah_lgns, rebase_yield / rebase_per_day, rebase_per_day, 30) * price_lgns

st.subheader("🔷 Estimasi Staking LGNS")
st.write(f"Setelah 1 hari: Rp {hasil_lgns_1d:,.0f}")
st.write(f"Setelah 7 hari: Rp {hasil_lgns_7d:,.0f}")
st.write(f"Setelah 30 hari: Rp {hasil_lgns_30d:,.0f}")
st.info("⚠️ **Risiko LGNS**: High-risk. APR sangat tinggi namun tidak stabil. Waspadai potensi rug pull dan fluktuasi harga yang ekstrem. Cocok hanya untuk jangka pendek/spekulasi.")

# =========================
# AXS Simulation
# =========================
jumlah_axs = modal_rupiah / price_axs
hasil_axs_1d = compound_growth_apy(jumlah_axs, axs_apr, 1) * price_axs
hasil_axs_7d = compound_growth_apy(jumlah_axs, axs_apr, 7) * price_axs
hasil_axs_30d = compound_growth_apy(jumlah_axs, axs_apr, 30) * price_axs

st.subheader("🟢 Estimasi Staking AXS")
st.write(f"Setelah 1 hari: Rp {hasil_axs_1d:,.0f}")
st.write(f"Setelah 7 hari: Rp {hasil_axs_7d:,.0f}")
st.write(f"Setelah 30 hari: Rp {hasil_axs_30d:,.0f}")
st.info("⚠️ **Risiko AXS**: Moderate. APR cukup stabil, cocok untuk jangka menengah. Risiko penurunan harga tetap ada namun lebih terkendali dibanding LGNS.")

# =========================
# Tabel Rekomendasi Staking
# =========================
st.subheader("📊 Top 5 Rekomendasi Staking Token Saat Ini")
top_staking = get_top_staking_options()
st.table(top_staking)

st.caption("📊 Data harga dari CoinGecko. APR dari scraping real-time Origin & Axie Infinity. Saran staking berdasarkan estimasi APR dan profil risiko. Untuk keperluan edukasi, bukan nasihat finansial.")
