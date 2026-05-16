import streamlit as st
import pandas as pd
import google.generativeai as genai
import json
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
        padding: 20px;
        border-radius: 10px;
        background: linear-gradient(135deg, #FFD700 0%, #FF8C00 100%);
        color: white;
        margin-bottom: 10px;
    }
    .trash-card {
        padding: 20px;
        border-radius: 10px;
        background: linear-gradient(135deg, #6c757d 0%, #343a40 100%);
        color: white;
        margin-bottom: 10px;
    }
    .potential-card {
        padding: 20px;
        border-radius: 10px;
        background: linear-gradient(135deg, #28a745 0%, #218838 100%);
        color: white;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://img.icons8.com/clouds/100/000000/manager.png", width=100)
    st.title("⚙️ Cấu hình Hệ thống")
    
    api_key = st.text_input("Gemini API Key", type="password", placeholder="Dán API Key vào đây...")
    sheet_id = "1zzbszm-d1yyqvAqVPc5n_Re545bG4h8rRWZmT-D-pCM"
    sheet_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
    
    st.divider()
    st.info("💡 **Hướng dẫn:**\n1. Nhập API Key.\n2. Bấm 'Lấy dữ liệu'.\n3. Bấm 'Chấm điểm bằng AI'.\n4. Chỉnh sửa nếu cần và Xuất Excel.")

# --- KHỞI TẠO AI ---
def get_ai_response(prompt, system_instruction):
    if not api_key:
        st.error("Vui lòng nhập Gemini API Key ở Sidebar!")
        return None
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=system_instruction
        )
        response = model.generate_content(prompt)
        # Loại bỏ các ký tự Markdown nếu AI trả về
        clean_text = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(clean_text)
    except Exception as e:
        st.error(f"Lỗi AI: {str(e)}")
        return None

# --- TẢI FILE SKILL ---
@st.cache_data
def load_skill():
    try:
        with open("lead_scoring_skill.md", "r", encoding="utf-8") as f:
            return f.read()
    except:
        return "Bạn là một chuyên gia Lead Scoring ngành Bất động sản. Hãy chấm điểm dựa trên mô tả nhu cầu."

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
                # Đảm bảo có các cột kết quả
                if 'Điểm AI' not in st.session_state.df.columns:
                    st.session_state.df['Điểm AI'] = 0
                    st.session_state.df['Phân loại'] = "Chưa chấm"
                    st.session_state.df['Lý do'] = ""
                st.success(f"Đã tải {len(st.session_state.df)} dòng dữ liệu!")
            except Exception as e:
                st.error(f"Lỗi tải dữ liệu: {e}")

with col2:
    if st.button("🤖 Chấm điểm bằng AI (Gemini)") and st.session_state.df is not None:
        skill_content = load_skill()
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for index, row in st.session_state.df.iterrows():
            status_text.text(f"Đang phân tích khách hàng: {row['ten_khach']}...")
            
            # Chuẩn bị prompt cho AI
            prompt = f"""
            Phân tích dữ liệu sau:
            - Tên: {row['ten_khach']}
            - Nhu cầu mô tả: {row['nhu_cau_mo_ta']}
            
            Trả về kết quả dưới định dạng JSON duy nhất:
            {{
                "score": <số điểm>,
                "category": "<VIP/Tiềm năng/Rác>",
                "reason": "<lý do ngắn gọn>"
            }}
            """
            
            result = get_ai_response(prompt, skill_content)
            
            if result:
                st.session_state.df.at[index, 'Điểm AI'] = result.get('score', 0)
                st.session_state.df.at[index, 'Phân loại'] = result.get('category', "Tiềm năng")
                st.session_state.df.at[index, 'Lý do'] = result.get('reason', "")
            
            progress_bar.progress((index + 1) / len(st.session_state.df))
        
        status_text.text("✅ Hoàn thành chấm điểm!")
        st.balloons()

# --- HIỂN THỊ DỮ LIỆU & HUMAN-IN-THE-LOOP ---
if st.session_state.df is not None:
    st.divider()
    st.subheader("📝 Kiểm duyệt dữ liệu (Human-in-the-loop)")
    
    # Cho phép chỉnh sửa trực tiếp trên bảng
    edited_df = st.data_editor(
        st.session_state.df,
        column_config={
            "Điểm AI": st.column_config.NumberColumn("Điểm", help="Điểm số do AI chấm"),
            "Phân loại": st.column_config.SelectboxColumn(
                "Phân loại",
                options=["VIP", "Tiềm năng", "Rác"],
                help="Phân loại khách hàng"
            ),
        },
        disabled=["id", "ten_khach", "sdt", "nhu_cau_mo_ta"], # Chỉ cho sửa kết quả AI
        use_container_width=True,
        hide_index=True
    )
    
    # Cập nhật lại session state sau khi sửa
    st.session_state.df = edited_df

    # --- XUẤT DỮ LIỆU ---
    st.divider()
    c1, c2, c3 = st.columns(3)
    
    with c1:
        # Thống kê nhanh
        vips = len(st.session_state.df[st.session_state.df['Phân loại'] == 'VIP'])
        st.metric("Khách hàng VIP", vips)
    
    with c2:
        # Nút xuất Excel
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            st.session_state.df.to_excel(writer, index=False, sheet_name='Leads_Processed')
        
        st.download_button(
            label="📊 Xuất file Excel bàn giao",
            data=output.getvalue(),
            file_name="Leads_Scoring_Results.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
else:
    st.warning("👈 Vui lòng bấm 'Lấy dữ liệu từ Sheets' ở Sidebar để bắt đầu.")

# --- FOOTER ---
st.divider()
st.caption("AI Agentic Framework - Lead Scoring Module v1.0 | Powered by Gemini 1.5 Flash")
