import streamlit as st

# 1. CẤU HÌNH TRANG (Đặt đầu tiên)
st.set_page_config(
    page_title="PDF to PowerPoint - Nguyễn Văn Hà",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. TỐI ƯU HÓA: CACHING CSS & HTML
# Dùng @st.cache_data để Streamlit không phải tải lại CSS mỗi lần user bấm nút
@st.cache_data
def load_css():
    return """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
        .stApp { background-color: #020617; color: white; font-family: 'Inter', sans-serif; }
        header[data-testid="stHeader"] {display: none;}
        
        /* HEADER */
        .header-container { display: flex; justify-content: space-between; align-items: center; padding: 10px 0px; border-bottom: 1px solid #1e293b; margin-bottom: 40px; }
        .logo-section { display: flex; align-items: center; gap: 15px; }
        .logo-icon { background: linear-gradient(135deg, #0ea5e9, #2563eb); color: white; width: 45px; height: 45px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 24px; box-shadow: 0 0 15px rgba(14, 165, 233, 0.5); }
        .brand-name { font-size: 20px; font-weight: 800; letter-spacing: 1px; text-transform: uppercase; color: #ffffff; line-height: 1.2; }
        .brand-sub { font-size: 10px; color: #0ea5e9; font-weight: 600; letter-spacing: 1.5px; }
        .contact-info { text-align: right; }
        .phone-number { color: #e2e8f0; font-weight: 600; font-size: 14px; }
        .status-badge { background-color: rgba(34, 197, 94, 0.1); color: #22c55e; border: 1px solid #22c55e; padding: 5px 15px; border-radius: 20px; font-size: 11px; font-weight: bold; display: inline-flex; align-items: center; gap: 5px; }
        .dot { height: 8px; width: 8px; background-color: #22c55e; border-radius: 50%; display: inline-block; }

        /* HERO */
        .hero-title { text-align: center; font-size: 56px; font-weight: 900; margin-bottom: 10px; text-transform: uppercase; }
        .gradient-text { background: linear-gradient(to right, #fb923c, #fca5a5, #fff, #67e8f9); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .hero-desc { text-align: center; color: #94a3b8; font-size: 18px; max-width: 700px; margin: 0 auto 60px auto; }

        /* CARDS */
        div[data-testid="stFileUploader"] { border: 2px dashed #334155; border-radius: 15px; padding: 30px; background-color: rgba(30, 41, 59, 0.5); text-align: center; transition: all 0.3s ease; }
        div[data-testid="stFileUploader"]:hover { border-color: #f97316; background-color: rgba(249, 115, 22, 0.05); }
        div.stButton > button { width: 100%; background-color: #1e293b; color: #94a3b8; border: none; padding: 20px; font-size: 16px; font-weight: 800; border-radius: 12px; text-transform: uppercase; letter-spacing: 1px; transition: all 0.3s; height: 80px; }
        div.stButton > button:hover { background-color: #0ea5e9; color: white; box-shadow: 0 0 20px rgba(14, 165, 233, 0.4); }
        div.stButton > button:active { transform: scale(0.98); } /* Hiệu ứng bấm nút */

        .step-header { text-align: center; margin-bottom: 25px; text-transform: uppercase; font-weight: 700; font-size: 14px; letter-spacing: 1px; }
        .icon-box { width: 50px; height: 50px; margin: 0 auto 15px auto; display: flex; align-items: center; justify-content: center; border-radius: 12px; font-size: 24px; }
        .step-1-color { color: #f97316; } .step-1-bg { background-color: rgba(249, 115, 22, 0.1); border: 1px solid rgba(249, 115, 22, 0.2); }
        .step-2-color { color: #06b6d4; } .step-2-bg { background-color: rgba(6, 182, 212, 0.1); border: 1px solid rgba(6, 182, 212, 0.2); }
        .custom-card { background-color: #0f172a; border: 1px solid #1e293b; border-radius: 24px; padding: 40px; height: 100%; min-height: 350px; display: flex; flex-direction: column; justify-content: center; }
    </style>
    """

@st.cache_data
def load_static_html():
    # Gom HTML tĩnh vào 1 hàm để cache
    header = """
    <div class="header-container">
        <div class="logo-section">
            <div class="logo-icon">H</div>
            <div><div class="brand-name">NGUYỄN VĂN HÀ</div><div class="brand-sub">AI EDUCATION • DIGITAL TRANSFORMATION</div></div>
        </div>
        <div class="contact-info"><div style="font-size: 10px; color: #64748b; margin-bottom: 2px;">HỖ TRỢ 24/7</div><div class="phone-number">0927.2222.05</div></div>
        <div class="status-badge"><span class="dot"></span> AI NODE ACTIVE</div>
    </div>
    """
    hero = """
    <div style="margin-top: 50px;">
        <h1 class="hero-title"><span style="color: #f97316;">PDF</span> <span style="color: white;">TO</span> <span class="gradient-text">POWERPOINT</span> <span style="color: white;">SIÊU TỐC</span></h1>
        <p class="hero-desc">Hệ thống AI chuyên dụng giúp thầy cô chuyển đổi 100% học liệu sang PowerPoint tương tác chỉ với 1 cú nhấp chuột.</p>
    </div>
    """
    return header + hero

# --- RENDER GIAO DIỆN ---
st.markdown(load_css(), unsafe_allow_html=True)
st.markdown(load_static_html(), unsafe_allow_html=True)

# --- MAIN CONTENT ---
_, main_col, _ = st.columns([1, 8, 1])

with main_col:
    col1, col2 = st.columns(2, gap="large")

    # --- CỘT 1 ---
    with col1:
        st.markdown("""
        <div class="custom-card">
            <div class="icon-box step-1-bg"><span style="font-size: 20px;">📄</span></div>
            <div class="step-header step-1-color">BƯỚC 1: CHỌN TÀI LIỆU</div>
        """, unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader("Upload", label_visibility="collapsed", type=['pdf', 'docx', 'png'])
        
        if not uploaded_file:
            st.markdown('<div style="text-align: center; color: #64748b; font-size: 12px; margin-top: -10px;">TẢI FILE PDF / WORD / ẢNH</div>', unsafe_allow_html=True)
        else:
            # Hiển thị tên file đã chọn để user biết đã nhận file
            st.markdown(f'<div style="text-align: center; color: #22c55e; font-size: 12px; margin-top: 10px;">✅ Đã nhận: {uploaded_file.name}</div>', unsafe_allow_html=True)
            
        st.markdown("</div>", unsafe_allow_html=True)

    # --- CỘT 2 ---
    with col2:
        st.markdown("""
        <div class="custom-card">
            <div class="icon-box step-2-bg"><span style="font-size: 20px; color: #06b6d4;">⚡</span></div>
            <div class="step-header step-2-color">BƯỚC 2: XUẤT POWERPOINT</div>
            <div style="height: 20px;"></div> 
        """, unsafe_allow_html=True)
        
        # Nút bấm
        if st.button("BẮT ĐẦU NGAY"):
            if uploaded_file is not None:
                # Sử dụng Spinner để báo hiệu đang xử lý (UX tốt hơn)
                with st.spinner("AI đang phân tích tài liệu..."):
                    import time
                    time.sleep(2) # Giả lập AI đang chạy
                    st.success("Xử lý thành công! (Demo)")
            else:
                st.error("⚠️ Vui lòng tải tài liệu lên trước!")
                
        st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)
