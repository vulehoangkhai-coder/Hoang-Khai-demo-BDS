# SKILL: HỆ THỐNG AI LEAD SCORING & PHÂN LOẠI KHÁCH HÀNG BẤT ĐỘNG SẢN

## 1. TỔNG QUAN (OVERVIEW)
Skill này giúp AI Agent tự động phân tích nhu cầu khách hàng từ các mô tả văn bản, từ đó chấm điểm và phân loại tiềm năng khách hàng. Mục tiêu là giúp đội ngũ kinh doanh ưu tiên chăm sóc các khách hàng chất lượng cao (VIP) và loại bỏ các dữ liệu rác.

## 2. CẤU TRÚC DỮ LIỆU ĐẦU VÀO (INPUT DATA STRUCTURE)
Dữ liệu được lấy từ Google Sheets với các trường thông tin sau:
- `id`: Mã định danh khách hàng.
- `ten_khach`: Họ và tên khách hàng.
- `sdt`: Số điện thoại liên lạc.
- `nhu_cau_mo_ta`: Nội dung khách hàng mô tả về nhu cầu, ngân sách, vị trí, và các yêu cầu khác. (Đây là trường dữ liệu chính để AI phân tích).

## 3. QUY TẮC CHẤM ĐIỂM (SCORING RULES)

### A. Nhóm VIP / SIÊU TIỀM NĂNG (+50 Điểm)
Cộng 50 điểm nếu mô tả khách hàng khớp với một trong các dấu hiệu sau:
- **Ngân sách lớn:** Đề cập số tiền ≥ 20 tỷ VNĐ hoặc các từ khóa: "tài chính mạnh", "tài chính không thành vấn đề", "ngân sách mở".
- **Loại hình cao cấp:** Tìm kiếm "Biệt thự đơn lập", "Penthouse", "Shophouse mặt đường lớn", "Quỹ đất công nghiệp", "Sàn văn phòng diện tích lớn".
- **Vị trí đắc địa:** Yêu cầu các khu vực: "Quận 1", "Ven sông", "Vinhomes Ocean Park", "Phú Mỹ Hưng".
- **Đối tượng đặc biệt:** Là "Chủ doanh nghiệp", "Nhà đầu tư chuyên nghiệp", "Mua sỉ", "Mua số lượng lớn".
- **Tính cấp thiết & Minh bạch:** Yêu cầu "Pháp lý chuẩn 100%", "Sổ hồng riêng", "Muốn gặp trực tiếp chủ đầu tư để đàm phán".

### B. Nhóm RÁC / KHÔNG TIỀM NĂNG (-50 Điểm)
Trừ 50 điểm nếu có các dấu hiệu sau:
- **Yêu cầu phi thực tế:** Giá thấp vô lý so với thị trường (Ví dụ: Nhà Quận 1 giá 1-2 tỷ, nhà trung tâm có hồ bơi giá vài trăm triệu).
- **Không có nhu cầu:** "Nhầm số", "Dữ liệu cũ", "Nhầm ngành", "Không có nhu cầu".
- **Không thiện chí:** "Hỏi giá cho vui", "Chưa có ý định mua", "Thái độ không hợp tác".
- **Spam / Quảng cáo:** Chứa nội dung về "Bảo hiểm", "Vay vốn", "Mời chào dịch vụ khác".
- **Lỗi liên lạc:** "Thuê bao", "Gọi nhiều lần không bắt máy", "Không phản hồi Zalo".

### C. Nhóm TIỀM NĂNG TRUNG BÌNH (0 - 10 Điểm)
Giữ nguyên điểm hoặc cộng ít (tối đa 10 điểm) cho các trường hợp:
- Khách hàng tìm mua chung cư, nhà phố tầm trung (3-10 tỷ).
- Cần vay ngân hàng, đang cân nhắc chính sách.
- Có nhu cầu thực nhưng cần tư vấn thêm về pháp lý hoặc vị trí.

## 4. QUY TRÌNH XỬ LÝ CỦA AI (AI WORKFLOW)
1. **Trích xuất thông tin:** Đọc dữ liệu từ cột `nhu_cau_mo_ta`.
2. **Phân loại từ khóa:** Nhận diện các từ khóa liên quan đến Ngân sách, Vị trí, Loại hình, và Thái độ.
3. **Tính toán điểm số:** Áp dụng các quy tắc cộng/trừ điểm ở Mục 3.
4. **Phân loại trạng thái:**
   - **ĐIỂM > 40:** Khách hàng VIP - Cần chăm sóc ngay.
   - **ĐIỂM từ 0 đến 40:** Khách hàng Tiềm năng - Đưa vào luồng tư vấn bình thường.
   - **ĐIỂM < 0:** Khách hàng Rác - Loại bỏ hoặc lưu trữ.
5. **Đề xuất hành động:** Đưa ra lý do ngắn gọn tại sao chấm điểm như vậy (Ví dụ: "Khách tìm Penthouse Quận 1, ngân sách lớn -> VIP").

## 5. MẪU ĐẦU RA KỲ VỌNG (EXPECTED OUTPUT)
| ID | Tên khách | Điểm | Phân loại | Lý do |
|---|---|---|---|---|
| 1 | Nguyễn Văn A | 50 | VIP | Khách tìm biệt thự đơn lập Quận 1, tài chính mạnh. |
| 2 | Trần Thị B | -50 | Rác | Khách báo nhầm số, không có nhu cầu. |
| 3 | Lê Văn C | 10 | Tiềm năng | Mua chung cư 2PN, cần vay ngân hàng. |
