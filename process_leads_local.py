import pandas as pd
import requests
import io
import os

# --- CẤU HÌNH ---
SHEET_ID = "1zzbszm-d1yyqvAqVPc5n_Re545bG4h8rRWZmT-D-pCM"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"
OUTPUT_FILE = "Leads_Scoring_Results_Final.xlsx"

def score_lead(row):
    description = str(row['nhu_cau_mo_ta']).lower()
    score = 0
    reasons = []
    category = "Tiềm năng"

    # --- TIÊU CHÍ CỘNG 50 ĐIỂM (VIP) ---
    # Ngân sách
    if any(k in description for k in ["20 tỷ", "30 tỷ", "50 tỷ", "100 tỷ", "tài chính mạnh", "không thành vấn đề"]):
        score += 50
        reasons.append("Ngân sách lớn/Tài chính mạnh")
    
    # Loại hình cao cấp
    if any(k in description for k in ["biệt thự đơn lập", "penthouse", "shophouse mặt đường", "quỹ đất công nghiệp", "sàn văn phòng"]):
        score += 50
        reasons.append("Loại hình BĐS cao cấp")
        
    # Vị trí đắc địa
    if any(k in description for k in ["quận 1", "ven sông", "vinhomes ocean park", "phú mỹ hưng"]):
        score += 50
        reasons.append("Vị trí đắc địa/Trung tâm")
        
    # Đối tượng/Quy mô
    if any(k in description for k in ["chủ doanh nghiệp", "nhà đầu tư chuyên nghiệp", "mua sỉ", "mua số lượng lớn"]):
        score += 50
        reasons.append("Khách hàng VIP/Nhà đầu tư sỉ")

    # Pháp lý
    if any(k in description for k in ["pháp lý chuẩn", "sổ hồng riêng", "gặp trực tiếp chủ đầu tư"]):
        score += 50
        reasons.append("Yêu cầu pháp lý minh bạch/Cấp thiết")

    # --- TIÊU CHÍ TRỪ 50 ĐIỂM (RÁC) ---
    # Phi thực tế
    if "quận 1" in description and any(k in description for k in ["1 tỷ", "2 tỷ"]):
        score -= 50
        reasons.append("Yêu cầu phi thực tế (Giá quá thấp so với khu vực)")
        
    # Không có nhu cầu
    if any(k in description for k in ["nhầm số", "không có nhu cầu", "dữ liệu cũ", "nhầm ngành"]):
        score -= 50
        reasons.append("Không có nhu cầu/Dữ liệu lỗi")
        
    # Spam/Quảng cáo
    if any(k in description for k in ["bảo hiểm", "vay vốn", "mời chào", "dịch vụ"]):
        score -= 50
        reasons.append("Spam/Quảng cáo/Dịch vụ khác")
        
    # Liên lạc lỗi
    if any(k in description for k in ["thuê bao", "không bắt máy", "không phản hồi zalo"]):
        score -= 50
        reasons.append("Lỗi thông tin liên lạc")

    # --- PHÂN LOẠI ---
    if score >= 50:
        category = "VIP"
    elif score <= -50:
        category = "Rác"
    else:
        category = "Tiềm năng"
        
    return score, category, "; ".join(reasons)

def main():
    print("--- Bat dau qua trinh lay du lieu va cham diem ---")
    
    try:
        # 1. Tai du lieu
        response = requests.get(CSV_URL)
        response.raise_for_status()
        df = pd.read_csv(io.StringIO(response.text))
        print(f"OK: Da tai {len(df)} dong du lieu tu Google Sheets.")
        
        # 2. Cham diem
        print("AI: Dang cham diem du tren file skill...")
        results = df.apply(score_lead, axis=1)
        df['Diem'], df['Phan loai'], df['Ly do'] = zip(*results)
        
        # 3. Xuat file Excel
        print(f"FILE: Dang xuat ket qua ra file {OUTPUT_FILE}...")
        df.to_excel(OUTPUT_FILE, index=False)
        
        print("\n" + "="*30)
        print("HOAN THANH!")
        print(f"File ket qua: {os.path.abspath(OUTPUT_FILE)}")
        print("="*30)
        
        # In ra top 5 khach hang VIP
        vips = df[df['Phan loai'] == 'VIP'].head()
        if not vips.empty:
            print("\nDanh sach khach hang VIP tieu bieu:")
            print(vips[['ten_khach', 'Diem', 'Ly do']])
            
    except Exception as e:
        print(f"❌ Lỗi: {str(e)}")

if __name__ == "__main__":
    main()
