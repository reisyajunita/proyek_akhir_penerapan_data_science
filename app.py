import streamlit as st
import pandas as pd
import joblib
from sklearn.preprocessing import StandardScaler

# Load model dan scaler
model = joblib.load('xgb_model.pkl')
scaler = joblib.load('scaler.pkl')
feature_names = joblib.load('feature_names.pkl')

# Judul aplikasi
st.title("🎓 Prediksi Mahasiswa Dropout")
st.header("🧾 Form Input Data Mahasiswa")

# ========================
# Fitur Numerik
# ========================
st.subheader("📊 Data Numerik")

app_order = st.selectbox(
    "Urutan Pilihan Program Studi (Application_order)",
    options=["-- Pilih --"] + list(range(0, 10)),
    format_func=lambda x: x if isinstance(x, str) else f"{x} (Pilihan ke-{x+1})"
)

num_features = {}

if app_order != "-- Pilih --":
    num_features["Application_order"] = app_order

# Slider numerik langsung
slider_fields = {
    "Previous_qualification_grade": "Nilai Kualifikasi Sebelumnya",
    "Admission_grade": "Nilai Masuk Universitas",
    "Curricular_units_1st_sem_credited": "Semester 1 - SKS Diakui",
    "Curricular_units_1st_sem_enrolled": "Semester 1 - SKS Diambil",
    "Curricular_units_1st_sem_approved": "Semester 1 - SKS Lulus",
    "Curricular_units_1st_sem_grade": "Semester 1 - Nilai Rata-rata",
    "Curricular_units_2nd_sem_credited": "Semester 2 - SKS Diakui",
    "Curricular_units_2nd_sem_enrolled": "Semester 2 - SKS Diambil",
    "Curricular_units_2nd_sem_approved": "Semester 2 - SKS Lulus",
    "Curricular_units_2nd_sem_grade": "Semester 2 - Nilai Rata-rata"
}

for col, label in slider_fields.items():
    max_val = 20.0 if "grade" in col else 10.0 if "credited" in col or "enrolled" in col or "approved" in col else 200.0
    step = 0.5 if "grade" in col else 1.0 if "credited" in col or "enrolled" in col or "approved" in col else 5.0
    num_features[col] = st.slider(f"{label} ({col})", 0.0, max_val, step=step, value=0.0)

# ========================
# Fitur Kategorikal
# ========================
st.subheader("🧮 Data Kategorikal")

def radio_input(label, options_dict):
    selected = st.radio(label, ["-- Belum dipilih --"] + list(options_dict.keys()))
    return options_dict.get(selected, None)

cat_inputs = {}

cat_inputs["Daytime_evening_attendance_Evening"] = radio_input(
    "Waktu Kuliah (Daytime_evening_attendance)",
    {"Day (kelas siang)": False, "Evening (kelas malam)": True}
)

cat_inputs["Displaced_Yes"] = radio_input(
    "Status Displaced (Displaced)",
    {"Tidak Mengungsi": False, "Pindahan / Mengungsi": True}
)

cat_inputs["Debtor_Yes"] = radio_input(
    "Status Debitur (Debtor)",
    {"Bukan Debitur": False, "Debitur": True}
)

cat_inputs["Tuition_fees_up_to_date_Yes"] = radio_input(
    "Status Pembayaran UKT (Tuition_fees_up_to_date)",
    {"Belum Lunas / Tertunggak": False, "Sudah Lunas": True}
)

cat_inputs["Gender_M"] = radio_input(
    "Jenis Kelamin (Gender)",
    {"Perempuan": False, "Laki-laki": True}
)

cat_inputs["Scholarship_holder_Yes"] = radio_input(
    "Status Beasiswa (Scholarship_holder)",
    {"Bukan Penerima Beasiswa": False, "Penerima Beasiswa": True}
)

# ========================
# Validasi Input & Prediksi
# ========================
if st.button("🔍 Prediksi Dropout"):
    if "-- Pilih --" in [app_order] or None in cat_inputs.values():
        st.warning("⚠️ Harap lengkapi semua input sebelum melakukan prediksi.")
    else:
        # Gabungkan data
        input_data = {**num_features, **cat_inputs}
        input_df = pd.DataFrame([input_data])

        # Standarisasi fitur numerik
        num_cols = list(num_features.keys())
        input_df[num_cols] = scaler.transform(input_df[num_cols])

        # Tambahkan kolom dummy yang belum ada
        for col in feature_names:
            if col not in input_df.columns:
                input_df[col] = 0

        input_df = input_df[feature_names]

        # Prediksi
        prediction = model.predict(input_df)[0]
        proba = model.predict_proba(input_df)[0]

        label = "Dropout" if prediction == 0 else "Tidak Dropout"
        st.success(f"🎯 Hasil Prediksi: **{label}**")

        st.markdown("### 📈 Probabilitas:")
        st.write(f"- Kemungkinan **Dropout**: `{proba[0]*100:.2f}%`")
        st.write(f"- Kemungkinan **Tidak Dropout**: `{proba[1]*100:.2f}%`")
