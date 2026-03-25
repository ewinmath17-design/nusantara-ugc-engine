import streamlit as st
import google.generativeai as genai
from PIL import Image
import json

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Nusantara UGC Engine v1.0", page_icon="✨", layout="centered")

st.title("✨ Nusantara UGC Engine v1.0")
st.markdown("Ubah foto produk biasa jadi konten UGC (TikTok/Reels) siap closing dalam hitungan detik.")

# --- SIDEBAR UNTUK API KEY ---
with st.sidebar:
    st.header("🔑 Pengaturan API")
    api_key = st.text_input("Masukkan Google Gemini API Key:", type="password")
    st.markdown("[Dapatkan API Key di Google AI Studio](https://aistudio.google.com/app/apikey)")
    st.divider()
    st.caption("Aplikasi ini otomatis mendeteksi model Gemini terbaik yang tersedia di API Key Anda.")

# --- FORM INPUT MULTIMODAL ---
st.subheader("📤 Input Aset")

col1, col2 = st.columns(2)
with col1:
    st.markdown("**1. Gambar Produk**")
    img_produk = st.file_uploader("Upload Foto Produk", type=["png", "jpg", "jpeg"], key="produk")
    if img_produk:
        st.image(img_produk, use_column_width=True)

with col2:
    st.markdown("**2. Referensi Wajah/Model**")
    img_model = st.file_uploader("Upload Foto Model", type=["png", "jpg", "jpeg"], key="model")
    if img_model:
        st.image(img_model, use_column_width=True)

kategori = st.selectbox("**3. Kategori Produk**", ["Skincare & Beauty", "Fashion & Apparel", "Gadget & Tech", "Food & Beverage", "Edukasi/Digital Product"])
gaya_konten = st.selectbox("**4. Gaya Konten**", ["Review Jujur / Testimoni", "POV Estetik (Trending)", "Hard Selling / Promo", "Unboxing / Tutorial"])

# --- SISTEM PROMPT ---
system_prompt = f"""
Anda adalah 'Nusantara UGC Engine v1.0', engine AI yang merancang aset konten affiliate marketing Indonesia.
Tugas: Analisis gambar produk dan model yang diberikan, lalu buat rancangan storyboard video UGC berdurasi 15 detik.

Kategori: {kategori}
Gaya Konten: {gaya_konten}

Output HARUS berupa format JSON MURNI tanpa markdown (jangan gunakan ```json). Format wajib:
{{
  "product_analysis": ["fitur 1", "fitur 2", "benefit utama"],
  "video_storyboard": {{
    "hook": "Kalimat pembuka/hook di awal video berbasis tren",
    "audio_vibe": "Saran musik background",
    "scenes": [
      {{
        "durasi": "0-3s",
        "visual": "Instruksi visual scene 1",
        "voiceover": "Skrip VO bahasa indonesia natural/gaul",
        "text_on_screen": "Teks yang muncul di layar"
      }},
      {{
        "durasi": "3-7s",
        "visual": "Instruksi visual scene 2",
        "voiceover": "Skrip VO",
        "text_on_screen": "Teks"
      }},
      {{
        "durasi": "7-12s",
        "visual": "Instruksi visual scene 3",
        "voiceover": "Skrip VO",
        "text_on_screen": "Teks"
      }},
      {{
        "durasi": "12-15s",
        "visual": "Instruksi visual scene CTA",
        "voiceover": "Skrip VO ajakan beli",
        "text_on_screen": "Teks CTA"
      }}
    ]
  }}
}}
"""

# --- TOMBOL GENERATE ---
if st.button("✨ Generate UGC Assets", use_container_width=True, type="primary"):
    if not api_key:
        st.error("Silakan masukkan Gemini API Key di sidebar terlebih dahulu.")
    elif not img_produk or not img_model:
        st.warning("Mohon upload Gambar Produk dan Referensi Wajah/Model.")
    else:
        try:
            with st.spinner("⏳ Sedang menganalisis aset dan mencari model AI yang sesuai..."):
                # Konfigurasi API
                genai.configure(api_key=api_key)
                
                # --- SISTEM PENDETEKSI MODEL OTOMATIS ---
                available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                
                target_model = None
                prioritas_model = ['models/gemini-1.5-flash', 'models/gemini-1.5-pro', 'models/gemini-1.5-flash-latest', 'models/gemini-pro-vision']
                
                # Cari model prioritas
                for preferred in prioritas_model:
                    if preferred in available_models:
                        target_model = preferred.replace('models/', '')
                        break
                
                # Jika tidak ada di daftar prioritas, ambil model apapun yang tersedia
                if not target_model and available_models:
                    target_model = available_models[0].replace('models/', '')
                
                # Jika sama sekali tidak ada model yang mendukung
                if not target_model:
                    st.error(f"Gagal menemukan model. Daftar model API Anda: {available_models}")
                    st.stop()
                
                st.info(f"*(Berhasil terhubung menggunakan model: **{target_model}**)*")
                
                # Inisialisasi Model Terpilih
                model = genai.GenerativeModel(target_model)
                
                # Buka file gambar dengan PIL
                pil_produk = Image.open(img_produk)
                pil_model = Image.open(img_model)
                
            with st.spinner("⏳ Sedang merancang storyboard..."):
                # Eksekusi Prompt Multimodal
                response = model.generate_content([system_prompt, pil_produk, pil_model])
                
                # Parsing JSON (Membersihkan sisa markdown jika ada)
                response_text = response.text.replace("```json", "").replace("```", "").strip()
                data = json.loads(response_text)

            # --- MENAMPILKAN HASIL ---
            st.success("✅ Aset UGC Berhasil Dibuat!")
            st.divider()

            # 1. Analisis Produk
            st.subheader("📌 Analisis Produk & Angle")
            tags_html = "".join([f"<span style='background:#e8f5e9; color:#2e7d32; padding:5px 10px; border-radius:15px; margin-right:5px; font-size:14px; display:inline-block; margin-bottom:5px;'>{fitur}</span>" for fitur in data['product_analysis']])
            st.markdown(tags_html, unsafe_allow_html=True)
            st.write("")

            # 2. Storyboard
            st.subheader("🎥 Video Storyboard (15s)")
            st.info(f"**Hook Angle:** {data['video_storyboard']['hook']} \n\n **🎵 Audio/Musik:** {data['video_storyboard']['audio_vibe']}")

            for scene in data['video_storyboard']['scenes']:
                with st.expander(f"🎬 Scene {scene['durasi']}", expanded=True):
                    st.markdown(f"**👁️ Visual:** {scene['visual']}")
                    st.markdown(f"**🗣️ Voiceover:** *\"{scene['voiceover']}\"*")
                    st.markdown(f"**📱 Text on Screen:** `{scene['text_on_screen']}`")

        except Exception as e:
            st.error(f"Terjadi kesalahan saat memproses data: {e}")
            st.caption("Pastikan gambar yang diupload tidak mengandung konten sensitif atau format yang rusak.")
