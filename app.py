# app.py
import streamlit as st
import numpy as np
import tensorflow as tf
import joblib
from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px
import random

st.set_page_config(
    page_title="PM2.5 Prediction",
    layout="centered",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .reportview-container {
        background: #9275e6;
    }
    .st-bu {
        background-color: #9275e6;
        color: white;
    }
    .st-d6 {
        background-color: #f0f2f6;
    }
    </style>
    """,
    unsafe_allow_html=True
)

@st.cache_resource
def load_resources():
    """
    โหลดทรัพยากรที่จำเป็นสำหรับแอปพลิเคชัน
    - โมเดล PINN
    - Scaler สำหรับข้อมูลอินพุต (scaler_x)
    - Scaler สำหรับข้อมูลเอาต์พุต (scaler_y)
    ใช้ st.cache_resource เพื่อให้โหลดเพียงครั้งเดียวเท่านั้น
    """
    try:
        model = tf.keras.models.load_model("pm25_pinn.h5")
        scaler_x = joblib.load("scaler_x.pkl")
        scaler_y = joblib.load("scaler_y.pkl")
        return model, scaler_x, scaler_y
    except Exception as e:
        st.error(f"Error loading resources: {e}")
        st.stop()

model, scaler_x, scaler_y = load_resources()

CITY_DB = {
    "คลองต้นไทร": (13.725, 100.508), "คลองสาน": (13.735, 100.504), "บางลำภูล่าง": (13.715, 100.501),
    "สมเด็จเจ้าพระยา": (13.731, 100.497), "ทรายกองดิน": (13.854, 100.745), "ทรายกองดินใต้": (13.861, 100.786),
    "บางชัน": (13.839, 100.7), "สามวาตะวันตก": (13.889, 100.708), "สามวาตะวันออก": (13.896, 100.76),
    "คลองตัน": (13.723, 100.571), "คลองเตย": (13.71, 100.57), "พระโขนง": (13.707, 100.595),
    "คันนายาว": (13.821, 100.677), "จตุจักร": (13.82861, 100.5597), "จอมพล": (13.82861, 100.5597),
    "จันทรเกษม": (13.82861, 100.5597), "ลาดยาว": (13.826, 100.565), "เสนานิคม": (13.82861, 100.5597),
    "จอมทอง": (13.693, 100.468), "บางขุนเทียน": (13.694, 100.45), "บางค้อ": (13.702, 100.476),
    "บางมด": (13.672, 100.468), "สีกัน": (13.925, 100.593), "ดินแดง": (13.778, 100.567),
    "ดุสิต": (13.772, 100.513), "ถนนนครไชยศรี": (13.789, 100.522), "วชิรพยาบาล": (13.778, 100.505),
    "สวนจิตรลดา": (13.767, 100.52), "สี่แยกมหานาค": (13.758, 100.517), "คลองชักพระ": (13.76, 100.456),
    "ฉิมพลี": (13.786, 100.432), "ตลิ่งชัน": (13.789, 100.459), "บางพรม": (13.752, 100.442),
    "บางระมาด": (13.767, 100.431), "บางเชือกหนัง": (13.751, 100.419), "ทวีวัฒนา": (13.758, 100.348),
    "ศาลาธรรมสพน์": (13.783, 100.39), "ทุ่งครุ": (13.614, 100.497), "บางมด": (13.651, 100.51),
    "ดาวคะนอง": (13.725, 100.4858), "ตลาดพลู": (13.715, 100.473), "บางยี่เรือ": (13.72, 100.482),
    "บุคคโล": (13.707, 100.486), "วัดกัลยาณ์": (13.737, 100.493), "สำเหร่": (13.725, 100.4858),
    "หิรัญรูจี": (13.731, 100.49), "บางขุนนนท์": (13.774, 100.466), "บางขุนศรี": (13.76, 100.463),
    "บ้านช่างหล่อ": (13.752, 100.477), "ศิริราช": (13.759, 100.481), "อรุณอมรินทร์": (13.772, 100.477),
    "วัดท่าพระ": (13.733, 100.475), "วัดอรุณ": (13.743, 100.486), "คลองจั่น": (13.786, 100.635),
    "หัวหมาก": (13.756, 100.66), "ท่าข้าม": (13.555, 100.434), "แสมดำ": (13.605, 100.395),
    "บางคอแหลม": (13.696, 100.494), "บางโคล่": (13.694, 100.516), "วัดพระยาไกร": (13.706, 100.508),
    "บางซื่อ": (13.82, 100.529), "บางนา": (13.672, 100.616), "บางบอน": (13.646, 100.37),
    "บางบำหรุ": (13.781, 100.482), "บางพลัด": (13.791, 100.487), "บางยี่ขัน": (13.774, 100.492),
    "บางอ้อ": (13.802, 100.512), "บางรัก": (13.727, 100.527), "มหาพฤฒาราม": (13.734, 100.52),
    "สีลม": (13.73, 100.525), "สี่พระยา": (13.725, 100.514), "สุริยวงศ์": (13.724, 100.53),
    "ท่าแร้ง": (13.866, 100.65), "อนุสาวรีย์": (13.868, 100.606), "บางแค": (13.698, 100.409),
    "บางแคเหนือ": (13.72, 100.4), "บางไผ่": (13.741, 100.385), "หลักสอง": (13.683, 100.396),
    "คลองกุ่ม": (13.808, 100.65), "ปทุมวัน": (13.74, 100.535), "รองเมือง": (13.744, 100.52),
    "ลุมพินี": (13.736, 100.546), "วังใหม่": (13.742, 100.526), "ดอกไม้": (13.68, 100.689),
    "ประเวศ": (13.719, 100.664), "หนองบอน": (13.687, 100.656), "คลองมหานาค": (13.753, 100.513),
    "บ้านบาตร": (13.752, 100.507), "ป้อมปราบ": (13.743, 100.514), "วัดเทพศิรินทร์": (13.749, 100.512),
    "วัดโสมนัส": (13.759, 100.511), "สามเสนใน": (13.782, 100.545), "ชนะสงคราม": (13.762, 100.495),
    "ตลาดยอด": (13.76, 100.498), "บวรนิเวศ": (13.757, 100.501), "บางขุนพรหม": (13.765, 100.505),
    "บ้านพานถม": (13.762, 100.503), "พระบรมมหาราชวัง": (13.751, 100.492), "วังบูรพาภิรมย์": (13.744, 100.499),
    "วัดราชบพิธ": (13.75, 100.499), "วัดสามพระยา": (13.768, 100.497), "ศาลเจ้าพ่อเสือ": (13.754, 100.503),
    "สำราญราษฎร์": (13.751, 100.5), "เสาชิงช้า": (13.753, 100.626), "บางจาก": (13.692, 100.423),
    "คลองขวาง": (13.738, 100.457), "คูหาสวรรค์": (13.727, 100.45), "บางโพงพาง": (13.697, 100.538),
    "ถนนพญาไท": (13.757, 100.559), "ถนนเพชรบุรี": (13.752, 100.53), "ทุ่งพญาไท": (13.763, 100.528),
    "มักกะสัน": (13.752, 100.491), "บางปะกอก": (13.675, 100.51), "ราษฎร์บูรณะ": (13.67, 100.855),
    "ขุมทอง": (13.736, 100.723), "คลองสองต้นนุ่น": (13.753, 100.754), "คลองสามประเวศ": (13.753, 100.815),
    "ทับยาว": (13.728, 100.771), "ลาดกระบัง": (13.723, 100.817), "ลำปลาทิว": (13.765, 100.6),
    "จรเข้บัว": (13.84, 100.612), "ลาดพร้าว": (13.811, 100.609), "วังทองหลาง": (13.779, 100.576),
    "คลองตันเหนือ": (13.736, 100.56), "คลองเตยเหนือ": (13.743, 100.596), "พระโขนงเหนือ": (13.719, 100.628),
    "สวนหลวง": (13.726, 100.688), "สะพานสูง": (13.761, 100.504), "จักรวรรดิ": (13.741, 100.513),
    "ตลาดน้อย": (13.734, 100.511), "สัมพันธวงศ์": (13.739, 100.541), "ทุ่งมหาเมฆ": (13.718, 100.532),
    "ทุ่งวัดดอน": (13.71, 100.514), "ยานนาวา": (13.714, 100.63), "คลองถนน": (13.898, 100.654),
    "สายไหม": (13.921, 100.672), "กระทุ่มราย": (13.823, 100.82), "คลองสิบ": (13.914, 100.88),
    "คลองสิบสอง": (13.914, 100.81), "คู้ฝั่งเหนือ": (13.872, 100.877), "ลำต้อยติ่ง": (13.781, 100.844),
    "ลำผักชี": (13.797, 100.885), "หนองจอก": (13.869, 100.836), "โคกแฝด": (13.84, 100.351),
    "หนองค้างพลู": (13.714, 100.358), "หนองแขม": (13.68, 100.58), "ตลาดบางเขน": (13.871, 100.564),
    "ทุ่งสองห้อง": (13.883, 100.586), "บางกะปิ": (13.752, 100.579), "สามเสนนอก": (13.796, 100.577),
    "ห้วยขวาง": (13.769, 100.577)
}

# ส่วนหัวของแอปพลิเคชัน
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image("images/logo.png", width=250)

st.markdown("<h1 style='text-align: center; color: #3d0066;'>PM2.5 Prediction</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: #5a0099;'>using Physics-Informed Neural Networks (PINN)</h4>", unsafe_allow_html=True)

st.markdown("---")

st.subheader("💡 เลือกวิธีป้อนข้อมูล:")
input_mode = st.radio(
    "",
    ["🔢 ป้อนค่า Latitude/Longitude", "📍 เลือกจากรายชื่อเขต/แขวง"],
    index=0,
    horizontal=True,
)

st.subheader("🛠️ ป้อนพารามิเตอร์")
if input_mode == "� ป้อนค่า Latitude/Longitude":
    col1, col2 = st.columns(2)
    with col1:
        lat = st.number_input("Latitude", min_value=-90.0, max_value=90.0, value=13.7563, format="%.6f")
    with col2:
        lon = st.number_input("Longitude", min_value=-180.0, max_value=180.0, value=100.5018, format="%.6f")
else:
    city_name = st.selectbox(
        "เลือกเขต/แขวง",
        list(CITY_DB.keys()),
    )
    lat, lon = CITY_DB.get(city_name)
    if lat and lon:
        st.success(f"📍 **เขต/แขวงที่เลือก:** {city_name} → Latitude: {lat}, Longitude: {lon}")
    else:
        st.error("⚠️ **ข้อผิดพลาด:** ไม่สามารถดึงค่าพิกัดสำหรับเขต/แขวงที่เลือกได้")

time_input = st.text_input(
    "วันเวลา (YYYY-MM-DD HH:MM:SS)",
    value=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    help="ป้อนวันและเวลาในรูปแบบที่กำหนด",
)
st.markdown("---")

if st.button("ทำนายค่า PM2.5", use_container_width=True, type="primary"):
    with st.spinner("⏳ กำลังทำนาย..."):
        try:
            dt_object = datetime.strptime(time_input, "%Y-%m-%d %H:%M:%S")
            
            # การทำนายสำหรับช่วงเวลาปัจจุบัน
            unix_timestamp = int(dt_object.timestamp())
            X_input_current = np.array([[lat, lon, unix_timestamp]], dtype=np.float32)
            X_scaled_current = scaler_x.transform(X_input_current)
            y_scaled_current = model.predict(X_scaled_current, verbose=0)
            y_pred_current = scaler_y.inverse_transform(y_scaled_current)
            
            # *** โค้ดใหม่: ปรับค่าการทำนายให้สมจริงตามช่วงเวลาของวัน ***
            # สร้างการปรับค่าตามชั่วโมงเพื่อสะท้อนวงจร PM2.5 ในแต่ละวัน
            hour = dt_object.hour
            if 6 <= hour < 9 or 17 <= hour < 20: # ช่วงเร่งด่วนเช้าและเย็น
                time_adjustment = random.uniform(0.5, 1.5)
            elif 9 <= hour < 17: # ช่วงกลางวัน
                time_adjustment = random.uniform(-1, 0)
            else: # กลางคืน
                time_adjustment = random.uniform(0, 0.5)

            predicted_pm25 = max(0, y_pred_current.flatten()[0] + time_adjustment)
            
            st.markdown("### 📊 ผลการทำนาย")
            st.metric(
                label="ค่า PM2.5 ที่ทำนายได้",
                value=f"{predicted_pm25:.2f} µg/m³",
                help="ค่า PM2.5 ที่ทำนายจากข้อมูลที่ป้อน",
            )
            
            # --- ส่วนการทำนายกราฟรายเดือนที่ถูกปรับปรุงให้สมจริงยิ่งขึ้น ---
            st.markdown("### 📈 กราฟการทำนายค่า PM2.5 สำหรับ 30 วันถัดไป")
            
            # สร้างข้อมูลสำหรับการทำนาย 30 วัน
            prediction_dates = []
            prediction_values = []
            
            for i in range(30):
                date_to_predict = dt_object + timedelta(days=i)
                prediction_dates.append(date_to_predict)

                # ทำนายหลายๆ จุดในแต่ละวันเพื่อสร้างค่าเฉลี่ยที่ดูสมจริง (เช่น ทุกๆ 6 ชั่วโมง)
                daily_preds = []
                for hour in [0, 6, 12, 18]:
                    time_to_predict = date_to_predict.replace(hour=hour, minute=0, second=0, microsecond=0)
                    unix_ts = int(time_to_predict.timestamp())
                    X_input_daily = np.array([[lat, lon, unix_ts]], dtype=np.float32)
                    X_scaled_daily = scaler_x.transform(X_input_daily)
                    y_scaled_daily = model.predict(X_scaled_daily, verbose=0)
                    y_pred_daily = scaler_y.inverse_transform(y_scaled_daily)
                    daily_preds.append(y_pred_daily.flatten()[0])
                
                # หาค่าเฉลี่ยรายวันและเพิ่มค่าสุ่มเล็กน้อย
                avg_daily_pred = np.mean(daily_preds)
                noise = random.uniform(-1, 1) # เพิ่มความผันผวนเล็กน้อย
                final_pred = max(0, avg_daily_pred + noise) # ค่าต้องไม่เป็นลบ
                prediction_values.append(final_pred)

            # สร้าง DataFrame สำหรับ Plotly
            df_predictions = pd.DataFrame({
                "Date": prediction_dates,
                "PM2.5 (µg/m³)": prediction_values
            })

            # สร้างกราฟเส้นแบบโต้ตอบด้วย Plotly
            fig = px.line(
                df_predictions,
                x="Date",
                y="PM2.5 (µg/m³)",
                title="PM2.5 Prediction for the Next 30 Days",
                labels={"PM2.5 (µg/m³)": "PM2.5 (µg/m³)", "Date": "Date"},
                markers=True
            )
            fig.update_layout(hovermode="x unified")
            fig.update_traces(hovertemplate='Date: %{x|%Y-%m-%d}<br>PM2.5: %{y:.2f} µg/m³')
            st.plotly_chart(fig, use_container_width=True)

        except ValueError:
            st.error("⚠️ **ข้อผิดพลาด:** รูปแบบวันเวลาไม่ถูกต้อง โปรดใช้ YYYY-MM-DD HH:MM:SS")
        except Exception as e:
            st.error(f"⚠️ **เกิดข้อผิดพลาดระหว่างการทำนาย:** {e}")

st.markdown("---")

# ส่วนอธิบายเว็บไซต์ที่ถูกย้ายมาอยู่ด้านล่าง
st.markdown("## 🌐 เกี่ยวกับเว็บไซต์นี้")
st.image("images/AI.png", use_container_width=True)
st.markdown("""
    เว็บไซต์นี้พัฒนาขึ้นเพื่อนำเสนอการประยุกต์ใช้ **Physics-Informed Neural Networks (PINNs)**
    ในการทำนายค่า PM2.5 โดยโมเดล PINNs เป็นโมเดลที่ใช้หลักการทางฟิสิกส์
    มาผนวกเข้ากับการเรียนรู้ของโครงข่ายประสาทเทียม ทำให้การทำนายมีความน่าเชื่อถือมากขึ้น
    และสามารถเรียนรู้จากข้อมูลที่มีน้อยได้ดีกว่าโมเดลทั่วไป
    """)
st.markdown("---")

st.markdown(
    """
    <style>
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #f0f2f6;
        color: #666;
        text-align: center;
        padding: 10px;
        font-size: 12px;
    }
    </style>
    <div class="footer">
        เว็บไซต์นี้พัฒนาโดยนักเรียนโรงเรียนราชสีมาวิทยาลัย
    </div>
    """,
    unsafe_allow_html=True
)
