import streamlit as st
import google.generativeai as genai
import re
import urllib.parse

# =====================================================================
# 1. THIẾT LẬP TRANG & CSS (LÀM ĐẸP GIAO DIỆN)
# =====================================================================
# Đặt cấu hình trang web: Mở rộng toàn màn hình, đặt tiêu đề và icon trên tab trình duyệt
st.set_page_config(page_title="Trợ Lý AI Giáo Viên Pro", layout="wide", page_icon="👨‍🏫")

# Khởi tạo bộ nhớ tạm (Session State) để giữ kết quả không bị mất khi bấm nút khác
if "ket_qua_ai" not in st.session_state:
    st.session_state.ket_qua_ai = ""
if "danh_sach_anh" not in st.session_state:
    st.session_state.danh_sach_anh = {}

# Đoạn mã CSS này giúp giao diện trở nên bóng bẩy, hiện đại và thân thiện với giáo viên
st.markdown("""
<style>
    /* Làm đẹp tiêu đề chính: Căn giữa, tô màu xanh công nghệ và đổ bóng chữ */
    h1 { 
        text-align: center; 
        color: #0284c7 !important; 
        text-shadow: 0px 2px 4px rgba(0,0,0,0.1); 
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Làm đẹp các khung viền (expander, tabs) để trông giống thẻ (cards) 3D */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 5px 5px 0 0;
        background-color: #f0f9ff;
        border: 1px solid #bae6fd;
    }
    
    /* Làm đẹp nút bấm chính (Primary Button): Nút "Tạo tài liệu" sẽ nổi bật nhất */
    .stButton>button[kind="primary"] { 
        background: linear-gradient(90deg, #0284c7 0%, #0ea5e9 100%); 
        color: white; 
        border-radius: 8px; 
        width: 100%; 
        font-weight: bold;
        font-size: 16px;
        padding: 10px;
        border: none;
        transition: 0.3s;
    }
    .stButton>button[kind="primary"]:hover { 
        transform: translateY(-3px); 
        box-shadow: 0 5px 15px rgba(14, 165, 233, 0.4);
    }
    
    /* Khung kết quả AI hiển thị giống tờ giấy A4 giúp giáo viên dễ đọc */
    .a4-paper {
        background-color: white;
        padding: 40px;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        color: #333;
        border: 1px solid #e2e8f0;
    }
</style>
""", unsafe_allow_html=True)

# =====================================================================
# 2. THANH BÊN (SIDEBAR) - KHU VỰC CÀI ĐẶT
# =====================================================================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/1903/1903162.png", width=80) # Icon giáo viên
    st.header("⚙️ Bảng Điều Khiển")
    
    # Ô nhập API Key dạng mật khẩu (ẩn ký tự)
    api_key_input = st.text_input("🔑 Nhập API Key (Gemini):", type="password", help="Lấy mã tại aistudio.google.com")
    
    st.markdown("---")
    st.markdown("""
    **💡 Mẹo sử dụng cho Thầy/Cô:**
    - AI tự động định dạng Toán học (LaTeX). Copy dán vào Word, dùng MathType để hiển thị.
    - Chức năng tạo ảnh nằm ở Tab số 2 sau khi AI tạo xong tài liệu.
    """)

# Kết nối AI nếu đã có API Key
if api_key_input:
    genai.configure(api_key=api_key_input)
    model = genai.GenerativeModel('gemini-3.8-flash')

# =====================================================================
# 3. GIAO DIỆN CHÍNH - KHU VỰC NHẬP LIỆU
# =====================================================================
st.title("👨‍🏫 TRỢ LÝ AI ĐA NĂNG CHO GIÁO VIÊN")
st.markdown("<p style='text-align: center; color: #64748b; font-size: 18px;'>Soạn Giáo Án - Lên Kịch Bản Slide - Tạo Đề Kiểm Tra trong tích tắc</p>", unsafe_allow_html=True)
st.markdown("---")

# Bộ chọn chức năng cốt lõi (Radio buttons)
loai_tai_lieu = st.radio(
    "🎯 Thầy/Cô muốn tạo tài liệu gì hôm nay?",
    ["📝 Kế hoạch bài dạy (CV 5512)", "📽️ Kịch bản Slide bài giảng", "📋 Đề kiểm tra & Đáp án"],
    horizontal=True # Hiển thị ngang cho gọn
)

st.markdown("<br>", unsafe_allow_html=True)

# Lưới chia cột để xếp các ô nhập liệu cho cân đối
col1, col2 = st.columns(2)
with col1:
    mon_hoc = st.selectbox("📚 Môn học", ["Toán học", "Ngữ Văn", "Tiếng Anh", "Vật Lý", "Hóa học", "Sinh học", "Lịch sử", "Địa lý", "Tin học", "Khác"])
    lop = st.selectbox("🎓 Khối Lớp", ["Lớp 6", "Lớp 7", "Lớp 8", "Lớp 9", "Lớp 10", "Lớp 11", "Lớp 12"])
    
with col2:
    ten_bai = st.text_input("📝 Tên bài học / Chủ đề kiểm tra", placeholder="VD: Định lý Vi-ét, Khởi nghĩa Hai Bà Trưng...")
    thoi_luong = st.number_input("⏱️ Thời lượng (Số tiết / Số phút)", min_value=1, value=1, help="Số tiết (nếu là giáo án) hoặc Số phút (nếu là đề kiểm tra)")

# Khung mở rộng chứa các tùy chọn nâng cao
with st.expander("🛠️ Tùy chỉnh chi tiết (Không bắt buộc)"):
    if loai_tai_lieu == "📋 Đề kiểm tra & Đáp án":
        cau_truc_de = st.text_input("Cấu trúc đề (VD: 20 câu trắc nghiệm, 2 câu tự luận):")
    else:
        phuong_phap = st.selectbox("Phương pháp dạy học", ["Linh hoạt", "Dạy học dự án", "Lớp học đảo ngược", "Thảo luận nhóm", "Trực quan sinh động"])
        trinh_do = st.selectbox("Trình độ học sinh", ["Đại trà (Khá - Trung bình)", "Học sinh Giỏi / Chuyên", "Cần kèm cặp thêm"])
        
    yeu_cau_them = st.text_area("Ghi chú đặc biệt cho AI:", placeholder="VD: Đề kiểm tra cần bám sát thực tế, Giáo án cần trò chơi khởi động...")

# =====================================================================
# 4. TRÁI TIM CỦA ỨNG DỤNG - XỬ LÝ LỆNH (PROMPT)
# =====================================================================
if st.button("🚀 TIẾN HÀNH TẠO TÀI LIỆU", type="primary"):
    if not api_key_input:
        st.error("⚠️ Thầy/Cô vui lòng nhập API Key ở thanh bên trái trước nhé!")
    elif not ten_bai:
        st.warning("⚠️ Thầy/Cô vui lòng nhập Tên bài học / Chủ đề kiểm tra.")
    else:
        with st.spinner("AI đang xử lý dữ liệu sư phạm... Thầy/Cô đợi một chút nhé..."):
            
            # --- Tùy chỉnh Prompt cho TỪNG loại tài liệu ---
            if loai_tai_lieu == "📝 Kế hoạch bài dạy (CV 5512)":
                prompt = f"""
                Bạn là chuyên gia sư phạm. Lập Kế hoạch bài dạy (Giáo án) theo chuẩn Công văn 5512.
                Môn: {mon_hoc} {lop}. Bài: "{ten_bai}". Trình độ: {trinh_do}. Phương pháp: {phuong_phap}.
                Ghi chú: {yeu_cau_them}
                Yêu cầu:
                - Gồm: I. Mục tiêu, II. Thiết bị dạy học, III. Tiến trình dạy học (4 hoạt động: Khởi động, Hình thành kiến thức, Luyện tập, Vận dụng).
                - Công thức Toán/Lý/Hóa phải bọc trong $$ hoặc $ để tương thích LaTeX.
                - Đề xuất hình ảnh dùng cú pháp: [Ảnh minh họa X: <Prompt tiếng Anh chi tiết>]
                """
                
            elif loai_tai_lieu == "📽️ Kịch bản Slide bài giảng":
                prompt = f"""
                Bạn là chuyên gia sư phạm. Viết kịch bản chi tiết để thiết kế Slide PowerPoint.
                Môn: {mon_hoc} {lop}. Bài: "{ten_bai}". Thời lượng: {thoi_luong} tiết.
                Ghi chú: {yeu_cau_them}
                Yêu cầu:
                - Trình bày theo từng Slide (Slide 1: Tiêu đề, Slide 2: Khởi động...). 
                - Mỗi Slide nêu rõ: Nội dung text hiển thị, Ghi chú cho giáo viên lúc thuyết trình.
                - BẮT BUỘC đề xuất hình ảnh cho các slide quan trọng bằng cú pháp: [Ảnh minh họa X: <Prompt tiếng Anh chi tiết để vẽ ảnh>]
                - Công thức Toán học dùng chuẩn LaTeX.
                """
                
            else: # Đề kiểm tra
                prompt = f"""
                Bạn là chuyên gia ra đề thi. Hãy tạo Đề kiểm tra kèm Đáp án chi tiết.
                Môn: {mon_hoc} {lop}. Chủ đề: "{ten_bai}". Thời gian: {thoi_luong} phút.
                Cấu trúc: {cau_truc_de if 'cau_truc_de' in locals() else 'Trắc nghiệm và Tự luận'}.
                Ghi chú: {yeu_cau_them}
                Yêu cầu:
                - Gồm 3 phần: I. Ma trận đề, II. Đề thi chính thức, III. Hướng dẫn chấm & Đáp án.
                - Công thức Toán học dùng chuẩn mã LaTeX bọc trong dấu $.
                - Nếu đề cần hình vẽ, dùng cú pháp: [Ảnh minh họa X: <Prompt tiếng Anh chi tiết mô tả hình vẽ>]
                """

            # Gọi API và xử lý kết quả
            try:
                response = model.generate_content(prompt)
                st.session_state.ket_qua_ai = response.text
                
                # Quét tự động để tìm các chỗ AI muốn chèn ảnh
                pattern = r"\[(Ảnh minh họa \d+):\s*(.*?)\]"
                matches = re.findall(pattern, response.text)
                st.session_state.danh_sach_anh = {match[0]: match[1] for match in matches}
                
                st.rerun() # Tải lại trang để hiện khu vực Tab bên dưới
            except Exception as e:
                st.error(f"Có lỗi từ máy chủ AI: {e}. Vui lòng thử lại.")

# =====================================================================
# 5. KHU VỰC HIỂN THỊ KẾT QUẢ & CÔNG CỤ SINH ẢNH
# =====================================================================
if st.session_state.ket_qua_ai:
    st.markdown("---")
    
    # Tạo 2 Tab: 1 cho Văn bản, 1 cho Ảnh
    tab1, tab2 = st.tabs(["📄 Nội dung Tài liệu", "🎨 Trạm tạo Ảnh minh họa"])
    
    with tab1:
        st.success("🎉 Tạo thành công! Thầy/Cô có thể Tải xuống hoặc Copy trực tiếp.")
        
        # Bọc kết quả trong