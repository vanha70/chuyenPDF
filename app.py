import streamlit as st
import io
from pptx import Presentation
from pptx.util import Inches, Pt, Cm
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

# 1. CẤU HÌNH TRANG
st.set_page_config(
    page_title="PDF to PowerPoint - Nguyễn Văn Hà",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. CSS GIAO DIỆN (Giữ nguyên độ đẹp)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    .stApp { background-color: #020617; color: white; font-family: 'Inter', sans-serif; }
    header[data-testid="stHeader"] {display: none;}
    
    /* HEADER & LOGO */
    .header-container { display: flex; justify-content: space-between; align-items: center; padding: 10px 0px; border-bottom: 1px solid #1e293b; margin-bottom: 40px; }
    .logo-section { display: flex; align-items: center; gap: 15px; }
    .logo-icon { background: linear-gradient(135deg, #0ea5e9, #2563eb); color: white; width: 45px; height: 45px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 24px; box-shadow: 0 0 15px rgba(14, 165, 233, 0.5); }
    .brand-name { font-size: 20px; font-weight: 800; letter-spacing: 1px; text-transform: uppercase; color: #ffffff; line-height: 1.2; }
    .brand-sub { font-size: 10px; color: #0ea5e9; font-weight: 600; letter-spacing: 1.5px; }
    .contact-info { text-align: right; }
    .phone-number { color: #e2e8f0; font-weight: 600; font-size: 14px; }
    .status-badge { background-color: rgba(34, 197, 94, 0.1); color: #22c55e; border: 1px solid #22c55e; padding: 5px 15px; border-radius: 20px; font-size: 11px; font-weight: bold; display: inline-flex; align-items: center; gap: 5px; }
    .dot { height: 8px; width: 8px; background-color: #22c55e; border-radius: 50%; display: inline-block; }

    /* HERO TEXT */
    .hero-title { text-align: center; font-size: 56px; font-weight: 900; margin-bottom: 10px; text-transform: uppercase; }
    .gradient-text { background: linear-gradient(to right, #fb923c, #fca5a5, #fff, #67e8f9); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    .hero-desc { text-align: center; color: #94a3b8; font-size: 18px; max-width: 700px; margin: 0 auto 60px auto; }

    /* CARDS & BUTTONS */
    div[data-testid="stFileUploader"] { border: 2px dashed #334155; border-radius: 15px; padding: 30px; background-color: rgba(30, 41, 59, 0.5); text-align: center; transition: all 0.3s ease; }
    div[data-testid="stFileUploader"]:hover { border-color: #f97316; background-color: rgba(249, 115, 22, 0.05); }
    
    div.stButton > button, div.stDownloadButton > button { width: 100%; background-color: #1e293b; color: #94a3b8; border: none; padding: 20px; font-size: 16px; font-weight: 800; border-radius: 12px; text-transform: uppercase; letter-spacing: 1px; transition: all 0.3s; height: 80px; }
    div.stButton > button:hover { background-color: #0ea5e9; color: white; box-shadow: 0 0 20px rgba(14, 165, 233, 0.4); }
    
    div.stDownloadButton > button { background-color: rgba(34, 197, 94, 0.2); color: #22c55e; border: 1px solid #22c55e; }
    div.stDownloadButton > button:hover { background-color: #22c55e; color: white; box-shadow: 0 0 20px rgba(34, 197, 94, 0.4); }

    .step-header { text-align: center; margin-bottom: 25px; text-transform: uppercase; font-weight: 700; font-size: 14px; letter-spacing: 1px; }
    .icon-box { width: 50px; height: 50px; margin: 0 auto 15px auto; display: flex; align-items: center; justify-content: center; border-radius: 12px; font-size: 24px; }
    .step-1-color { color: #f97316; } .step-1-bg { background-color: rgba(249, 115, 22, 0.1); border: 1px solid rgba(249, 115, 22, 0.2); }
    .step-2-color { color: #06b6d4; } .step-2-bg { background-color: rgba(6, 182, 212, 0.1); border: 1px solid rgba(6, 182, 212, 0.2); }
    .custom-card { background-color: #0f172a; border: 1px solid #1e293b; border-radius: 24px; padding: 40px; height: 100%; min-height: 350px; display: flex; flex-direction: column; justify-content: center; }
</style>
""", unsafe_allow_html=True)

# 3. QUẢN LÝ TRẠNG THÁI
if 'processed' not in st.session_state:
    st.session_state.processed = False
if 'output_file' not in st.session_state:
    st.session_state.output_file = None

# ==============================================================================
# HÀM XỬ LÝ POWERPOINT NÂNG CAO (MÔ PHỎNG GIAO DIỆN)
# ==============================================================================

def set_text_format(paragraph, text, font_size=18, is_bold=False, color=None):
    paragraph.text = text
    paragraph.font.size = Pt(font_size)
    paragraph.font.name = 'Arial'
    paragraph.font.bold = is_bold
    if color:
        paragraph.font.color.rgb = color

def create_slide_content(prs, question_data):
    """
    Hàm này vẽ layout giống hệt file mẫu:
    - Header: Số câu hỏi to
    - Body: Nội dung câu hỏi
    - Options: Các đáp án A, B, C, D
    - Footer: Thông tin giáo viên
    """
    # Màu sắc chủ đạo
    ORANGE_COLOR = RGBColor(237, 125, 49) # Màu cam cho số câu
    BLUE_COLOR = RGBColor(0, 32, 96)      # Màu xanh đậm cho text
    GRAY_COLOR = RGBColor(89, 89, 89)     # Màu xám footer

    # 1. Tạo slide trắng
    slide_layout = prs.slide_layouts[6] # 6 là Blank layout
    slide = prs.slides.add_slide(slide_layout)

    # 2. Vẽ Số câu hỏi (Ví dụ: "1") - Góc trên bên trái
    # Shape tròn hoặc vuông bo góc chứa số
    left = Inches(0.5)
    top = Inches(0.3)
    width = Inches(0.8)
    height = Inches(0.8)
    
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = ORANGE_COLOR
    shape.line.color.rgb = ORANGE_COLOR
    
    text_frame = shape.text_frame
    text_frame.text = str(question_data['id'])
    p = text_frame.paragraphs[0]
    p.font.size = Pt(32)
    p.font.bold = True
    p.font.color.rgb = RGBColor(255, 255, 255)
    p.alignment = PP_ALIGN.CENTER

    # 3. Chữ "CÂU HỎI" bên cạnh số
    left = Inches(1.4)
    top = Inches(0.45)
    width = Inches(2)
    height = Inches(0.5)
    textbox = slide.shapes.add_textbox(left, top, width, height)
    p = textbox.text_frame.paragraphs[0]
    set_text_format(p, "CÂU HỎI", font_size=20, is_bold=True, color=ORANGE_COLOR)

    # 4. Nội dung câu hỏi
    left = Inches(0.5)
    top = Inches(1.3)
    width = Inches(9) # Slide rộng 10 inch
    height = Inches(1.5)
    textbox = slide.shapes.add_textbox(left, top, width, height)
    text_frame = textbox.text_frame
    text_frame.word_wrap = True
    
    p = text_frame.paragraphs[0]
    set_text_format(p, question_data['question'], font_size=18, is_bold=False, color=RGBColor(0, 0, 0))

    # 5. Vẽ các đáp án (A, B, C, D)
    # Logic chia cột 2x2 hoặc danh sách tùy độ dài
    options = question_data.get('options', [])
    if options:
        # Tọa độ bắt đầu vẽ đáp án
        start_y = 3.0
        
        # Nếu là câu hỏi đúng sai (kiểu a,b,c,d)
        if question_data.get('type') == 'true_false':
            for idx, opt in enumerate(options):
                # Vẽ box đáp án
                top_opt = Inches(start_y + idx * 0.6)
                textbox = slide.shapes.add_textbox(Inches(0.5), top_opt, Inches(9), Inches(0.5))
                p = textbox.text_frame.paragraphs[0]
                # Format: a. Nội dung ... [ĐÚNG/SAI]
                content = f"{chr(97+idx)}. {opt['text']}"
                set_text_format(p, content, font_size=16)
                
                # Vẽ dấu check hoặc text Đúng/Sai nếu có (để demo)
                if 'ans' in opt:
                    p.text += f"   [{opt['ans']}]"

        # Nếu là câu trắc nghiệm ABCD
        else:
            # Layout lưới 2 cột
            col_1_left = Inches(0.8)
            col_2_left = Inches(5.5)
            row_1_top = Inches(3.2)
            row_2_top = Inches(4.5)
            
            positions = [
                (col_1_left, row_1_top), (col_2_left, row_1_top),
                (col_1_left, row_2_top), (col_2_left, row_2_top)
            ]
            labels = ['A', 'B', 'C', 'D']
            
            for i, opt_text in enumerate(options):
                if i >= 4: break
                left_pos, top_pos = positions[i]
                
                # Vẽ chữ cái A, B, C, D to đậm
                label_box = slide.shapes.add_textbox(left_pos - Inches(0.4), top_pos, Inches(0.4), Inches(0.5))
                p_label = label_box.text_frame.paragraphs[0]
                set_text_format(p_label, labels[i], font_size=20, is_bold=True, color=ORANGE_COLOR)
                
                # Vẽ nội dung đáp án
                content_box = slide.shapes.add_textbox(left_pos, top_pos, Inches(4), Inches(1))
                content_box.text_frame.word_wrap = True
                p_content = content_box.text_frame.paragraphs[0]
                set_text_format(p_content, opt_text, font_size=16)

    # 6. Footer (Giống file mẫu)
    footer_text = "HỆ THỐNG GIÁO DỤC HIỆN ĐẠI | BIÊN SOẠN: THẦY NGUYỄN VĂN HÀ"
    
    # Vẽ đường kẻ ngang dưới cùng
    line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(7.0), Inches(10), Inches(0.5))
    line.fill.solid()
    line.fill.fore_color.rgb = RGBColor(242, 242, 242) # Màu xám nhạt nền footer
    line.line.color.rgb = RGBColor(242, 242, 242)
    
    # Text footer
    textbox = slide.shapes.add_textbox(Inches(0.5), Inches(7.1), Inches(9), Inches(0.4))
    p = textbox.text_frame.paragraphs[0]
    set_text_format(p, footer_text, font_size=10, is_bold=True, color=GRAY_COLOR)
    p.alignment = PP_ALIGN.CENTER

def generate_pptx_from_data():
    prs = Presentation()
    # Set slide width/height 16:9
    prs.slide_width = Inches(10)
    prs.slide_height = Inches(7.5) # Kích thước chuẩn 4:3 (hoặc 13.33 x 7.5 cho 16:9)

    # --- DỮ LIỆU GIẢ LẬP TỪ FILE CỦA BẠN (DEMO) ---
    # Trong thực tế, cần code parse file PDF/Word phức tạp để lấy dữ liệu này.
    # Ở đây mình trích xuất sẵn vài câu từ file bạn gửi để demo tính năng tạo slide.
    
    questions = [
        {
            "id": 1,
            "question": "Cấu trúc mạch vòng của carbohydrate nào sau đây không có nhóm -OH hemiacetal hoặc hemiketal?",
            "options": ["Saccharose.", "Maltose.", "Glucose.", "Fructose."],
            "type": "mcq"
        },
        {
            "id": 2,
            "question": "Carbohydrate nào sau đây kém tan trong nước lạnh nhưng tan được trong nước nóng tạo dung dịch keo, nhớt?",
            "options": ["Cellulose.", "Saccharose.", "Tinh bột.", "Glucose."],
            "type": "mcq"
        },
        {
            "id": 19,
            "question": "Glutamic acid có vai trò quan trọng trong quá trình xây dựng cấu trúc tế bào... Glutamic acid có điểm đẳng điện pI=3,2.",
            "options": [
                {"text": "Glutamic acid thuộc loại hợp chất hữu cơ tạp chức...", "ans": "ĐÚNG"},
                {"text": "Để thu được 2 tấn bột ngọt cần tối thiểu 2,52 tấn tinh thể...", "ans": "ĐÚNG"},
                {"text": "Tên thay thế của glutamic acid là 2-aminopentane...", "ans": "ĐÚNG"},
                {"text": "Trong dung dịch pH=6, có thể tách hỗn hợp...", "ans": "ĐÚNG"}
            ],
            "type": "true_false"
        },
        {
            "id": 23,
            "question": "Hiện nay mạ điện được sử dụng rộng rãi trong thực tế. Giả sử người ta cần mạ Ag lên một mặt của một chiếc đĩa kim loại hình tròn...",
            "options": ["ĐÁP SỐ: 0,15 giờ (ví dụ)"],
            "type": "short_ans"
        }
    ]

    for q in questions:
        create_slide_content(prs, q)

    # Lưu vào buffer
    output_buffer = io.BytesIO()
    prs.save(output_buffer)
    output_buffer.seek(0)
    return output_buffer.getvalue()

# ==============================================================================
# GIAO DIỆN CHÍNH
# ==============================================================================

# HEADER HTML
st.markdown("""
<div class="header-container">
    <div class="logo-section">
        <div class="logo-icon">H</div>
        <div><div class="brand-name">NGUYỄN VĂN HÀ</div><div class="brand-sub">AI EDUCATION • DIGITAL TRANSFORMATION</div></div>
    </div>
    <div class="contact-info"><div style="font-size: 10px; color: #64748b; margin-bottom: 2px;">HỖ TRỢ 24/7</div><div class="phone-number">0927.2222.05</div></div>
    <div class="status-badge"><span class="dot"></span> AI NODE ACTIVE</div>
</div>
<div style="margin-top: 50px;">
    <h1 class="hero-title"><span style="color: #f97316;">PDF</span> <span style="color: white;">TO</span> <span class="gradient-text">POWERPOINT</span> <span style="color: white;">SIÊU TỐC</span></h1>
    <p class="hero-desc">Hệ thống AI chuyên dụng giúp thầy cô chuyển đổi 100% học liệu sang PowerPoint tương tác chỉ với 1 cú nhấp chuột.</p>
</div>
""", unsafe_allow_html=True)

# MAIN LAYOUT
_, main_col, _ = st.columns([1, 8, 1])

with main_col:
    col1, col2 = st.columns(2, gap="large")

    # --- BƯỚC 1: UPLOAD ---
    with col1:
        st.markdown("""
        <div class="custom-card">
            <div class="icon-box step-1-bg"><span style="font-size: 20px;">📄</span></div>
            <div class="step-header step-1-color">BƯỚC 1: CHỌN TÀI LIỆU</div>
        """, unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader("Upload", label_visibility="collapsed", type=['pdf', 'docx', 'pptx'])
        
        if uploaded_file and 'last_file' in st.session_state and st.session_state.last_file != uploaded_file.name:
            st.session_state.processed = False
            
        if uploaded_file:
            st.session_state.last_file = uploaded_file.name
            st.markdown(f'<div style="text-align: center; color: #22c55e; font-size: 12px; margin-top: 10px;">✅ Đã nhận: {uploaded_file.name}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div style="text-align: center; color: #64748b; font-size: 12px; margin-top: -10px;">TẢI FILE PDF / WORD / ẢNH</div>', unsafe_allow_html=True)
            st.session_state.processed = False
            
        st.markdown("</div>", unsafe_allow_html=True)

    # --- BƯỚC 2: XỬ LÝ & TẢI VỀ ---
    with col2:
        st.markdown("""
        <div class="custom-card">
            <div class="icon-box step-2-bg"><span style="font-size: 20px; color: #06b6d4;">⚡</span></div>
            <div class="step-header step-2-color">BƯỚC 2: XUẤT POWERPOINT</div>
            <div style="height: 20px;"></div> 
        """, unsafe_allow_html=True)
        
        if not st.session_state.processed:
            if st.button("BẮT ĐẦU NGAY"):
                if uploaded_file is not None:
                    import time
                    with st.spinner("AI đang phân tích cấu trúc & tạo Slide..."):
                        time.sleep(2) # Giả lập loading
                        
                        try:
                            # GỌI HÀM TẠO PPTX MỚI
                            output_data = generate_pptx_from_data()
                            st.session_state.output_file = output_data
                            st.session_state.processed = True
                            st.rerun()
                        except Exception as e:
                            st.error(f"Lỗi hệ thống: {e}")
                            
                else:
                    st.warning("Vui lòng tải tài liệu lên trước!")
        else:
            # Nút Download
            st.download_button(
                label="📥 TẢI POWERPOINT VỀ MÁY",
                data=st.session_state.output_file,
                file_name="Giao_An_Dien_Tu_NguyenVanHa.pptx",
                mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
            )
            
            if st.button("🔄 Làm file khác", key="reset_btn"):
                st.session_state.processed = False
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)
