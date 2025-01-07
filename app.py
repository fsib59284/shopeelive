import threading

import streamlit as st
import requests
import time

running = False
# Judul Aplikasi
st.title("Form Input dengan Streamlit")

# Entry untuk memasukkan data
session = st.text_input("Masukkan Session:")
shopid = st.text_input("Masukkan Shop ID:")
userig = st.text_input("Masukkan User IG:")  # Menghapus usersig, hanya menggunakan userig
uuid = st.text_input("Masukkan UUID:")
pesan = st.text_area("Masukkan Pesan:")
url_raw_github = st.text_input("Masukkan URL Raw GitHub untuk Cookies:")
like_cnt = st.number_input("Masukkan Jumlah Like:", min_value=1, value=1)
delay_between_actions = st.number_input("Delay antar Aksi (detik):", min_value=0.1, value=1.0)

# Fungsi untuk memuat cookies dari URL GitHub
def load_cookies_from_github(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        cookies_list = response.text.splitlines()
        return [cookie.strip() for cookie in cookies_list]
    except Exception as e:
        st.error(f"Gagal mengunduh file cookies: {e}")
        return []

# Fungsi untuk mengirim like dengan header spesifik
def send_like(session_id, cookies, like_count):
    url = f"https://live.shopee.co.id/api/v1/session/{session_id}/like"
    headers = {
        "cookie": "; ".join(cookies),
        "content-type": "application/json",
        "user-agent": "ShopeeApp/3.0 (Android; Mobile; AppVer=3.0)",
        "accept": "*/*"
    }
    data = {"like_cnt": like_count}
    try:
        response = requests.post(url, headers=headers, json=data)
        return response.json()
    except Exception as e:
        return f"Error: {e}"


# Fungsi untuk mengirim pesan dengan response yang lebih simpel
def send_message(session_id, cookies, uuid, userig, content):
    url = f"https://live.shopee.co.id/api/v1/session/{session_id}/message"
    headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en-US,en;q=0.9',
        'af-ac-enc-dat': '001ed94da16d0da5',
        'client-info': 'platform=9;device_id=9WKYLbnCkcojeuzaOGw7bKz1BScokjgs',
        'content-type': 'application/json',
        'origin': 'https://live.shopee.co.id',
        'priority': 'u=1, i',
        'referer': f'https://live.shopee.co.id/pc/live?session={session_id}',
        'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, seperti Gecko) Chrome/131.0.0.0 Safari/537.36',
        'x-sz-sdk-version': '1.10.7',
        "cookie": "; ".join(cookies)  # Cookies tetap dimasukkan di header
    }

    # Data JSON yang dikirimkan
    json_data = {
        'uuid': uuid,
        'usersig': userig,  # Menggunakan userig sebagai user signature
        'content': f'{{"type":100,"content":"{content}"}}',
        'pin': False
    }

    try:
        # Mengirim permintaan POST ke server Shopee
        response = requests.post(url, headers=headers, json=json_data)

        # Jika status code 200, pesan sukses
        if response.status_code == 200:
            return "✅ Pesan berhasil dikirim!"
        else:
            # Menampilkan status kode selain 200
            return f"❌ Gagal mengirim pesan. Kode Status: {response.status_code}"
    except requests.exceptions.RequestException as e:
        return f"❌ Request Error: {e}"
    except Exception as e:
        return f"❌ Terjadi kesalahan: {e}"


# Fungsi untuk mengirim follow dengan header spesifik
def send_follow(session_id, shop_id, cookies):
    url = f"https://live.shopee.co.id/api/v1/session/{session_id}/follow/{shop_id}"
    headers = {
        "cookie": "; ".join(cookies),
        "user-agent": "ShopeeApp/3.0 (iOS; Mobile; AppVer=3.0)",
        "accept": "*/*",
        "content-type": "application/json"
    }
    try:
        response = requests.post(url, headers=headers, json={})
        return response.json()
    except Exception as e:
        return f"Error: {e}"

# Fungsi untuk mengirim buy dengan header spesifik
def send_buy(session_id, cookies):
    url = f"https://live.shopee.co.id/api/v1/session/{session_id}/msg/buy"
    headers = {
        "cookie": "; ".join(cookies),
        "user-agent": "ShopeeApp/3.0 (Windows; Desktop; AppVer=3.0)",
        "content-type": "application/json",
        "accept": "*/*"
    }
    try:
        response = requests.post(url, headers=headers, json={})
        return response.json()
    except Exception as e:
        return f"Error: {e}"


# Fungsi untuk menjalankan looping selamanya di background
def start_loop():
    global running
    running = True
    cookies_list = load_cookies_from_github(url_raw_github)

    if cookies_list:
        while running:
            for index, cookie in enumerate(cookies_list):
                cookie_list = [cookie]

                # Mengirim Like dengan log dinamis
                print(f"Mengirim Like... ({index + 1}/{len(cookies_list)})")
                send_like(session, cookie_list, like_cnt)

                # Mengirim Pesan dengan log dinamis
                print(f"Mengirim Pesan... ({index + 1}/{len(cookies_list)})")
                send_message(session, cookie_list, uuid, userig, pesan)

                # Mengirim Follow dengan log dinamis
                print(f"Mengirim Follow... ({index + 1}/{len(cookies_list)})")
                send_follow(session, shopid, cookie_list)

                # Mengirim Buy dengan log dinamis
                print(f"Mengirim Buy... ({index + 1}/{len(cookies_list)})")
                send_buy(session, cookie_list)

                # Jeda antar aksi
                time.sleep(delay_between_actions)
    else:
        print("❌ Gagal memuat cookies, pastikan URL Raw GitHub benar.")



col1, col2 = st.columns(2)

with col1:
    if st.button("Start"):
        if not running:
            threading.Thread(target=start_loop, daemon=True).start()
            st.success("Looping di background dimulai! Aplikasi akan tetap berjalan.")

