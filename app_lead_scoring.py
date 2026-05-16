import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
from io import BytesIO

# --- CẤU HÌNH TRANG ---
st.set_page_config(
    page_title="MindX AI Lead Scoring",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- PHONG CÁCH GIAO DIỆN (CSS TÙY CHỈNH) ---
st.markdown("""
    <style>
    /* Tổng thể */
    .main {
        background-color: #ffffff;
    }
    
    /* Tùy chỉnh Sidebar */
    [data-testid="stSidebar"] {
        background-color: #1e293b;
        color: white;
    }
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    
    /* Nút bấm */
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        height: 3.5em;
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        color: white;
        font-weight: bold;
        border: none;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.2);
        background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%);
    }
    
    /* Thẻ chỉ số (Metrics Custom) */
    .metric-container {
        background: white;
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
        text-align: center;
    }
    
    /* Banner */
    .banner {
        background: linear-gradient(90deg, #ef4444 0%, #f97316 100%);
        padding: 40px;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 30px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIC KẾT NỐI GOOGLE SHEETS (PRIVATE) ---
def load_data_from_gsheet():
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        # Thử tìm file credentials.json
        creds_path = "credentials.json"
        if not os.path.exists(creds_path):
            st.error("❌ Không tìm thấy file credentials.json!")
            return None
            
        creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
        client = gspread.authorize(creds)
        
        # Mở bằng ID đã cho
        sheet_id = "1zzbszm-d1yyqvAqVPc5n_Re545bG4h8rRWZmT-D-pCM"
        sheet = client.open_by_key(sheet_id).sheet1
        
        data = sheet.get_all_records()
        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"❌ Lỗi kết nối Google Sheets: {str(e)}")
        return None

# --- LOGIC CHẤM ĐIỂM NỘI BỘ ---
def score_lead_local(description):
    desc = str(description).lower()
    score = 0
    reasons = []
    
    # VIP Criteria (+50)
    if any(k in desc for k in ["20 tỷ", "30 tỷ", "50 tỷ", "100 tỷ", "tài chính mạnh", "không thành vấn đề"]):
        score += 50
        reasons.append("Ngân sách lớn")
    if any(k in desc for k in ["biệt thự", "penthouse", "shophouse", "công nghiệp", "văn phòng"]):
        score += 50
        reasons.append("Loại hình cao cấp")
    if any(k in desc for k in ["quận 1", "ven sông", "vinhomes", "phú mỹ hưng"]):
        score += 50
        reasons.append("Vị trí đắc địa")
    
    # Trash Criteria (-50)
    if any(k in desc for k in ["nhầm số", "không có nhu cầu", "dữ liệu cũ", "hỏi giá cho vui"]):
        score -= 50
        reasons.append("Dữ liệu rác/Không nhu cầu")
    if "quận 1" in desc and any(k in desc for k in ["1 tỷ", "2 tỷ"]):
        score -= 50
        reasons.append("Giá phi thực tế")
        
    category = "Tiềm năng"
    if score >= 50: category = "VIP"
    elif score <= -50: category = "Rác"
    
    return score, category, "; ".join(reasons)

# --- SIDEBAR (LOGO & FILTER) ---
with st.sidebar:
    # Logo MindX (Placeholder URL hoặc từ local nếu có)
    st.image("https://mindx.edu.vn/images/logo.png", width=200) # Logo thương hiệu
    st.divider()
    st.title("⚙️ CẤU HÌNH HỆ THỐNG")
    
    st.success("🤖 AI Agent: Đang hoạt động")
    
    st.divider()
    st.subheader("🔍 BỘ LỌC TÌM KIẾM")
    filter_cat = st.multiselect(
        "Lọc trạng thái",
        options=["VIP", "Tiềm năng", "Rác", "Chưa chấm"],
        default=["VIP", "Tiềm năng", "Rác", "Chưa chấm"]
    )
    search_query = st.text_input("Tìm khách hàng...", placeholder="Nhập tên hoặc nhu cầu...")

# --- GIAO DIỆN CHÍNH ---
# Banner chào mừng
st.markdown("""
    <div class="banner">
        <h1>🎯 AI LEAD SCORING SYSTEM</h1>
        <p>Hệ thống tự động hóa phân loại & chấm điểm khách hàng Bất động sản</p>
    </div>
    """, unsafe_allow_html=True)

if 'df' not in st.session_state:
    st.session_state.df = None

# Nút chức năng chính
c_act1, c_act2 = st.columns(2)
with c_act1:
    if st.button("📥 1. LẤY DỮ LIỆU TỪ GOOGLE SHEETS"):
        with st.spinner("Đang kết nối API bảo mật..."):
            df_new = load_data_from_gsheet()
            if df_new is not None:
                st.session_state.df = df_new
                if 'Điểm AI' not in st.session_state.df.columns:
                    st.session_state.df['Điểm AI'] = 0
                    st.session_state.df['Phân loại'] = "Chưa chấm"
                    st.session_state.df['Lý do'] = ""
                st.success(f"✅ Đã tải thành công {len(st.session_state.df)} Leads từ hệ thống!")

with c_act2:
    if st.button("🤖 2. CHẠY AI SCORING TỰ ĐỘNG") and st.session_state.df is not None:
        progress_bar = st.progress(0)
        status = st.empty()
        
        for index, row in st.session_state.df.iterrows():
            status.text(f"⏳ Đang quét mô tả khách hàng: {row['ten_khach']}...")
            s, c, r = score_lead_local(row['nhu_cau_mo_ta'])
            st.session_state.df.at[index, 'Điểm AI'] = s
            st.session_state.df.at[index, 'Phân loại'] = c
            st.session_state.df.at[index, 'Lý do'] = r
            progress_bar.progress((index + 1) / len(st.session_state.df))
        
        status.success("🚀 Hoàn thành phân loại tự động!")
        st.balloons()

# --- DASHBOARD METRICS (THEO YÊU CẦU 3 CỘT) ---
if st.session_state.df is not None:
    st.divider()
    st.subheader("📊 DASHBOARD TỔNG QUAN")
    
    # Áp dụng bộ lọc cho Metric
    df_filtered = st.session_state.df.copy()
    if filter_cat:
        df_filtered = df_filtered[df_filtered['Phân loại'].isin(filter_cat)]
    if search_query:
        search_query = search_query.lower()
        df_filtered = df_filtered[
            df_filtered['ten_khach'].str.lower().str.contains(search_query, na=False) |
            df_filtered['nhu_cau_mo_ta'].str.lower().str.contains(search_query, na=False)
        ]

    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric("👥 Tổng khách hàng", len(df_filtered))
    with m2:
        vips = len(df_filtered[df_filtered['Phân loại'] == 'VIP'])
        st.metric("🏆 Khách hàng VIP (+50đ)", vips)
    with m3:
        trash = len(df_filtered[df_filtered['Phân loại'] == 'Rác'])
        st.metric("🗑️ Khách hàng Rác (-50đ)", trash)

    # --- BẢNG KIỂM TRA (AUDIT TABLE) ---
    st.divider()
    st.subheader("📝 BẢNG KIỂM TRA & DUYỆT DỮ LIỆU (AUDIT)")
    
    edited_df = st.data_editor(
        df_filtered,
        column_config={
            "Điểm AI": st.column_config.NumberColumn("Điểm", format="%d"),
            "Phân loại": st.column_config.SelectboxColumn("Trạng thái", options=["VIP", "Tiềm năng", "Rác", "Chưa chấm"]),
        },
        use_container_width=True,
        hide_index=True,
        key="audit_editor"
    )

    if st.button("💾 LƯU KẾT QUẢ KIỂM DUYỆT"):
        st.session_state.df.update(edited_df)
        st.success("✅ Đã cập nhật kết quả vào bộ nhớ hệ thống!")

    # --- XUẤT FILE ---
    st.divider()
    st.subheader("📤 XUẤT FILE BÀN GIAO")
    
    col_dl1, col_dl2 = st.columns(2)
    with col_dl1:
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            st.session_state.df.to_excel(writer, index=False, sheet_name='Final_Leads')
        st.download_button(
            label="📄 TẢI TOÀN BỘ FILE EXCEL (XUẤT SALES)",
            data=output.getvalue(),
            file_name="MindX_Leads_Report.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    with col_dl2:
        st.info("💡 Lưu ý: File Excel đã được làm sạch và phân loại sẵn cho bộ phận Sales.")

else:
    st.info("🏠 Chào mừng bạn! Hãy bấm nút 'Lấy dữ liệu' ở trên để bắt đầu quy trình.")

# --- FOOTER ---
st.divider()
st.caption("🚀 AI Agent Workflow | MindX Technology School | Version 3.0")
