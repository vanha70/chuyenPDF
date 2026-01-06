import streamlit as st
import time
import io
from pptx import Presentation # Thư viện tạo PowerPoint
from pptx.util import Inches

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

# ---------------------------------------------------------
# HÀM TẠO FILE POWERPOINT THẬT (FIX LỖI CORRUPTED FILE)
# ---------------------------------------------------------
def create_sample_pptx(filename_input):
    # Khởi tạo một file PPT mới
    prs = Presentation()
    
    # Tạo Slide 1: Tiêu đề
    slide_layout = prs.slide_layouts[0] # 0 là layout tiêu đề
    slide = prs.slides.add_slide(slide_layout)
    title = slide.shapes.title
    subtitle = slide.placeholders[1]
    
    title.text = "Giáo Án Điện Tử AI"
    subtitle.text = f"Được tạo tự động từ file: {filename_input}\nbởi Hệ thống Nguyễn Văn Hà"
    
    # Tạo Slide 2: Nội dung mẫu
    bullet_slide_layout = prs.slide_layouts[1]
    slide2 = prs.slides.add_slide(bullet_slide_layout)
    shapes = slide2.shapes
    title_shape = shapes.title
    body_shape = shapes.placeholders[1]
    
    title_shape.text = "Nội dung chính"
    tf = body_shape.text_frame
    tf.text = "Đây là slide mẫu được tạo bởi Python-PPTX"
    p = tf.add_paragraph()
    p.text = "File này hoàn toàn hợp lệ và không bị lỗi."
    p.level = 1

    # Lưu file vào bộ nhớ đệm (RAM) thay vì lưu ra đĩa cứng
    output_buffer = io.BytesIO()
    prs.save(output_buffer)
    output_buffer.seek(0) # Đưa con trỏ về đầu file
    return output_buffer.getvalue()

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
        
        # Reset nếu đổi file
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
                    with st.spinner("AI đang thiết kế Slide..."):
                        time.sleep(2) 
                        
                        # --- GỌI HÀM TẠO FILE PPTX THẬT ---
                        try:
                            output_data = create_sample_pptx(uploaded_file.name)
                            st.session_state.output_file = output_data
                            st.session_state.processed = True
                            st.rerun()
                        except Exception as e:
                            st.error(f"Có lỗi xảy ra: {e}")
                            
                else:
                    st.warning("Vui lòng tải tài liệu lên trước!")
        else:
            # Nút Download màu xanh lá
            st.download_button(
                label="📥 TẢI POWERPOINT VỀ MÁY",
                data=st.session_state.output_file,
                file_name="Giao_An_Dien_Tu_AI.pptx",
                mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
            )
            
            if st.button("🔄 Làm file khác", key="reset_btn"):
                st.session_state.processed = False
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)
