import streamlit as st
import pandas as pd
import os
from io import BytesIO

# --- CẤU HÌNH TRANG ---
st.set_page_config(
    page_title="AI Lead Scoring System",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- PHONG CÁCH GIAO DIỆN (CSS) ---
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3em;
        background-color: #007bff;
        color: white;
        font-weight: bold;
        border: none;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #0056b3;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .vip-card {
        padding: 10px;
        border-radius: 5px;
        background-color: #FFD700;
        color: black;
        font-weight: bold;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIC CHẤM ĐIỂM NỘI BỘ (KHÔNG CẦN API KEY) ---
def score_lead_local(description):
    desc = str(description).lower()
    score = 0
    reasons = []
    
    # VIP Criteria
    if any(k in desc for k in ["20 tỷ", "30 tỷ", "50 tỷ", "100 tỷ", "tài chính mạnh", "không thành vấn đề"]):
        score += 50
        reasons.append("Ngân sách lớn")
    if any(k in desc for k in ["biệt thự", "penthouse", "shophouse", "công nghiệp", "văn phòng"]):
        score += 50
        reasons.append("Loại hình cao cấp")
    if any(k in desc for k in ["quận 1", "ven sông", "vinhomes", "phú mỹ hưng"]):
        score += 50
        reasons.append("Vị trí đắc địa")
    if any(k in desc for k in ["chủ doanh nghiệp", "nhà đầu tư", "mua sỉ"]):
        score += 50
        reasons.append("Khách hàng VIP")
    if any(k in desc for k in ["pháp lý", "sổ hồng", "chủ đầu tư"]):
        score += 50
        reasons.append("Pháp lý/Cấp thiết")

    # Trash Criteria
    if "quận 1" in desc and any(k in desc for k in ["1 tỷ", "2 tỷ"]):
        score -= 50
        reasons.append("Giá phi thực tế")
    if any(k in desc for k in ["nhầm số", "không có nhu cầu", "dữ liệu cũ"]):
        score -= 50
        reasons.append("Dữ liệu lỗi")
    if any(k in desc for k in ["bảo hiểm", "vay vốn", "quảng cáo"]):
        score -= 50
        reasons.append("Spam/Dịch vụ khác")
        
    category = "Tiềm năng"
    if score >= 50: category = "VIP"
    elif score <= -50: category = "Rác"
    
    return score, category, "; ".join(reasons)

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://img.icons8.com/clouds/100/000000/manager.png", width=100)
    st.title("⚙️ Hệ thống Lead Scoring")
    
    st.success("✅ Chế độ: Chấm điểm Nội bộ (Không cần API Key)")
    
    sheet_id = "1zzbszm-d1yyqvAqVPc5n_Re545bG4h8rRWZmT-D-pCM"
    sheet_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
    
    st.divider()
    st.info("💡 **Quy trình:**\n1. Lấy dữ liệu từ Google Sheets.\n2. Hệ thống tự động chấm điểm.\n3. Kiểm duyệt và Xuất Excel.")

# --- GIAO DIỆN CHÍNH ---
st.title("🎯 AI LEAD SCORING & AUTOMATION")
st.subheader("Hệ thống chấm điểm khách hàng tiềm năng tự động")

if 'df' not in st.session_state:
    st.session_state.df = None

col1, col2 = st.columns([1, 4])

with col1:
    if st.button("📥 Lấy dữ liệu từ Sheets"):
        with st.spinner("Đang tải dữ liệu..."):
            try:
                st.session_state.df = pd.read_csv(sheet_url)
                st.success(f"Đã tải {len(st.session_state.df)} dòng!")
            except Exception as e:
                st.error(f"Lỗi tải dữ liệu: {e}")

with col2:
    if st.button("🤖 Bắt đầu chấm điểm tự động") and st.session_state.df is not None:
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Tạo các cột mới
        scores = []
        categories = []
        reasons = []
        
        for index, row in st.session_state.df.iterrows():
            status_text.text(f"Đang xử lý: {row['ten_khach']}...")
            s, c, r = score_lead_local(row['nhu_cau_mo_ta'])
            scores.append(s)
            categories.append(c)
            reasons.append(r)
            progress_bar.progress((index + 1) / len(st.session_state.df))
        
        st.session_state.df['Điểm AI'] = scores
        st.session_state.df['Phân loại'] = categories
        st.session_state.df['Lý do'] = reasons
        
        status_text.text("✅ Hoàn thành chấm điểm!")
        st.balloons()

# --- HIỂN THỊ & KIỂM DUYỆT ---
if st.session_state.df is not None:
    st.divider()
    st.subheader("📝 Kiểm duyệt & Bàn giao (Human-in-the-loop)")
    
    # Hiển thị bảng kết quả cho phép sửa
    edited_df = st.data_editor(
        st.session_state.df,
        column_config={
            "Điểm AI": st.column_config.NumberColumn("Điểm"),
            "Phân loại": st.column_config.SelectboxColumn("Phân loại", options=["VIP", "Tiềm năng", "Rác"]),
        },
        use_container_width=True,
        hide_index=True
    )
    st.session_state.df = edited_df

    # --- THỐNG KÊ & XUẤT FILE ---
    st.divider()
    c1, c2 = st.columns([1, 1])
    
    with c1:
        vips = len(st.session_state.df[st.session_state.df['Phân loại'] == 'VIP'])
        st.metric("Tổng số khách hàng VIP", vips)
    
    with c2:
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            st.session_state.df.to_excel(writer, index=False, sheet_name='Leads_Results')
        
        st.download_button(
            label="📊 Tải file Excel bàn giao",
            data=output.getvalue(),
            file_name="Leads_Scoring_Results.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
else:
    st.warning("👈 Vui lòng bấm 'Lấy dữ liệu từ Sheets' để bắt đầu.")

st.divider()
st.caption("AI Agentic Framework | Lead Scoring Dashboard v2.0")
