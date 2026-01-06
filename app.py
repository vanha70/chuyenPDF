import streamlit as st
import io
import re
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

# ==============================================================================
# 1. CẤU HÌNH & CSS GIAO DIỆN
# ==============================================================================
st.set_page_config(page_title="PDF to PowerPoint - Nguyễn Văn Hà", page_icon="⚡", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    .stApp { background-color: #020617; color: white; font-family: 'Inter', sans-serif; }
    header[data-testid="stHeader"] {display: none;}
    .header-container { display: flex; justify-content: space-between; align-items: center; padding: 10px 0px; border-bottom: 1px solid #1e293b; margin-bottom: 40px; }
    .logo-section { display: flex; align-items: center; gap: 15px; }
    .logo-icon { background: linear-gradient(135deg, #0ea5e9, #2563eb); color: white; width: 45px; height: 45px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 24px; box-shadow: 0 0 15px rgba(14, 165, 233, 0.5); }
    .brand-name { font-size: 20px; font-weight: 800; letter-spacing: 1px; text-transform: uppercase; color: #ffffff; line-height: 1.2; }
    .brand-sub { font-size: 10px; color: #0ea5e9; font-weight: 600; letter-spacing: 1.5px; }
    .hero-title { text-align: center; font-size: 56px; font-weight: 900; margin-bottom: 10px; text-transform: uppercase; }
    .gradient-text { background: linear-gradient(to right, #fb923c, #fca5a5, #fff, #67e8f9); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    div[data-testid="stFileUploader"] { border: 2px dashed #334155; border-radius: 15px; padding: 30px; background-color: rgba(30, 41, 59, 0.5); text-align: center; }
    div.stButton > button, div.stDownloadButton > button { width: 100%; background-color: #1e293b; color: #94a3b8; border: none; padding: 20px; font-size: 16px; font-weight: 800; border-radius: 12px; text-transform: uppercase; height: 80px; }
    div.stButton > button:hover { background-color: #0ea5e9; color: white; }
    div.stDownloadButton > button { background-color: rgba(34, 197, 94, 0.2); color: #22c55e; border: 1px solid #22c55e; }
    div.stDownloadButton > button:hover { background-color: #22c55e; color: white; }
    .custom-card { background-color: #0f172a; border: 1px solid #1e293b; border-radius: 24px; padding: 40px; height: 100%; min-height: 350px; }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. XỬ LÝ TEXT & LOGIC (ĐÃ SỬA LỖI)
# ==============================================================================

def remove_invalid_xml_chars(text):
    """Lọc bỏ ký tự lạ để tránh lỗi Repair trong PowerPoint."""
    if not text: return ""
    # Giữ lại ký tự in được, xuống dòng, tab
    return "".join(ch for ch in text if ch.isprintable() or ch in ['\n', '\r', '\t'])

def clean_text(text):
    """Làm sạch text cơ bản"""
    if not text: return ""
    # Xóa tag 
    text = re.sub(r'\', '', text)
    # Loại bỏ dấu gạch chéo ngược (Fix lỗi SyntaxError tại đây)
    text = text.replace('\\', '') 
    return text.strip()

def format_chemical_text(paragraph, text, font_size=18, is_bold=False, color=None):
    """Xử lý hiển thị công thức hóa học (H2SO4, Cu2+)"""
    paragraph.clear()
    p = paragraph
    
    safe_text = remove_invalid_xml_chars(text)
    tokens = re.split(r'(\d+[+-]?|\s+)', safe_text)
    
    for token in tokens:
        if not token: continue
        
        run = p.add_run()
        run.font.size = Pt(font_size)
        run.font.name = 'Arial'
        run.font.bold = is_bold
        if color:
            run.font.color.rgb = color
            
        if re.match(r'^\d+$', token): 
            run.text = token
            run.font.subscript = True
        elif re.match(r'^\d*[+-]$', token): 
            run.text = token
            run.font.superscript = True
        else:
            run.text = token

def parse_exam_content(full_content):
    """Phân tích nội dung text đầu vào"""
    questions = []
    lines = full_content.split('\n')
    
    current_q = None
    state = "START"
    
    for line in lines:
        raw_line = clean_text(line)
        if not raw_line: continue
        
        # 1. Phát hiện số câu hỏi
        if re.match(r'^\d+$', raw_line):
            if current_q: questions.append(current_q)
            current_q = {
                "id": raw_line,
                "content": "",
                "options": [],
                "type": "mcq"
            }
            state = "QUESTION"
            continue
            
        # 2. Bỏ qua tiêu đề thừa
        if "CÂU HỎI" in raw_line.upper(): continue
        if "HỆ THỐNG GIÁO DỤC" in raw_line.upper(): continue
        if "BIÊN SOẠN" in raw_line.upper(): continue
            
        # 3. Phát hiện đáp án
        if re.match(r'^[A-D]$', raw_line) or re.match(r'^[a-d]\.', raw_line):
             if current_q:
                if re.match(r'^[a-d]\.', raw_line):
                    current_q['type'] = "true_false"
                current_q['options'].append({"label": raw_line, "text": ""})
                state = "OPTIONS"
             continue

        # 4. Phát hiện đáp án đúng/kết quả
        if "✦" in raw_line:
             if current_q and current_q['options']:
                 current_q['options'][-1]['is_correct'] = True
             continue
             
        if "ĐÚNG ✔" in raw_line or "SAI ✘" in raw_line:
             if current_q and current_q['options']:
                 current_q['options'][-1]['result'] = raw_line
             continue
        
        if raw_line.startswith("ĐÁP SỐ:"):
            if current_q:
                current_q['type'] = "short_ans"
                current_q['answer_text'] = raw_line
            continue

        # 5. Cộng dồn nội dung
        if current_q:
            if state == "QUESTION":
                current_q['content'] += raw_line + " "
            elif state == "OPTIONS":
                if current_q['options']:
                    current_q['options'][-1]['text'] += raw_line + " "

    if current_q: questions.append(current_q)
    return questions

# ==============================================================================
# 3. TẠO SLIDE POWERPOINT
# ==============================================================================

def create_pptx_file(questions):
    prs = Presentation()
    prs.slide_width = Inches(13.33)
    prs.slide_height = Inches(7.5)

    ORANGE = RGBColor(237, 125, 49)
    NAVY = RGBColor(0, 32, 96)
    GRAY = RGBColor(120, 120, 120)

    for q in questions:
        slide = prs.slides.add_slide(prs.slide_layouts[6]) 
        
        # SỐ CÂU
        shape_num = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.5), Inches(0.4), Inches(0.8), Inches(0.8))
        shape_num.fill.solid()
        shape_num.fill.fore_color.rgb = ORANGE
        shape_num.line.color.rgb = ORANGE
        p_num = shape_num.text_frame.paragraphs[0]
        p_num.text = str(q['id'])
        p_num.font.size = Pt(36)
        p_num.font.bold = True
        p_num.alignment = PP_ALIGN.CENTER
        
        # LABEL
        tb_lbl = slide.shapes.add_textbox(Inches(1.4), Inches(0.5), Inches(2), Inches(0.5))
        p_lbl = tb_lbl.text_frame.paragraphs[0]
        p_lbl.text = "CÂU HỎI"
        p_lbl.font.size = Pt(24)
        p_lbl.font.bold = True
        p_lbl.font.color.rgb = ORANGE

        # NỘI DUNG
        tb_content = slide.shapes.add_textbox(Inches(0.5), Inches(1.5), Inches(12), Inches(1.5))
        tb_content.text_frame.word_wrap = True
        format_chemical_text(tb_content.text_frame.paragraphs[0], q['content'], font_size=24, is_bold=True, color=NAVY)

        # ĐÁP ÁN
        start_y = 3.5
        if q['type'] == 'mcq':
            col_coords = [(Inches(1.0), Inches(3.5)), (Inches(7.0), Inches(3.5)), 
                          (Inches(1.0), Inches(5.0)), (Inches(7.0), Inches(5.0))]
            for idx, opt in enumerate(q['options']):
                if idx >= 4: break
                left, top = col_coords[idx]
                
                labels = ["A", "B", "C", "D"]
                tb_opt_lbl = slide.shapes.add_textbox(left - Inches(0.5), top, Inches(0.5), Inches(0.5))
                p_opt_lbl = tb_opt_lbl.text_frame.paragraphs[0]
                p_opt_lbl.text = labels[idx]
                p_opt_lbl.font.size = Pt(24)
                p_opt_lbl.font.bold = True
                p_opt_lbl.font.color.rgb = ORANGE
                
                tb_opt_txt = slide.shapes.add_textbox(left, top, Inches(5.5), Inches(1.2))
                tb_opt_txt.text_frame.word_wrap = True
                format_chemical_text(tb_opt_txt.text_frame.paragraphs[0], opt['text'], font_size=20)
                
                if opt.get('is_correct'):
                    rect = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left - Inches(0.6), top - Inches(0.1), Inches(6), Inches(1.3))
                    rect.fill.background()
                    rect.line.color.rgb = RGBColor(255, 0, 0)
                    rect.line.width = Pt(2)

        elif q['type'] == 'true_false':
            for idx, opt in enumerate(q['options']):
                top = Inches(start_y + idx * 0.9)
                tb_row = slide.shapes.add_textbox(Inches(0.5), top, Inches(12), Inches(0.8))
                p_row = tb_row.text_frame.paragraphs[0]
                full_text = f"{opt['label']} {opt['text']}"
                if opt.get('result'): full_text += f"   [{opt['result']}]"
                format_chemical_text(p_row, full_text, font_size=20)

        elif q['type'] == 'short_ans':
             tb_ans = slide.shapes.add_textbox(Inches(1.0), Inches(4.0), Inches(10), Inches(1.0))
             p_ans = tb_ans.text_frame.paragraphs[0]
             p_ans.text = q.get('answer_text', '')
             p_ans.font.size = Pt(24)
             p_ans.font.bold = True
             p_ans.font.color.rgb = RGBColor(255, 0, 0)

        # FOOTER
        line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(7.0), Inches(13.33), Inches(0.05))
        line.fill.solid()
        line.fill.fore_color.rgb = RGBColor(220, 220, 220)
        
        tb_footer = slide.shapes.add_textbox(Inches(0), Inches(7.1), Inches(13.33), Inches(0.4))
        p_footer = tb_footer.text_frame.paragraphs[0]
        p_footer.text = "HỆ THỐNG GIÁO DỤC HIỆN ĐẠI | BIÊN SOẠN: THẦY NGUYỄN VĂN HÀ"
        p_footer.font.size = Pt(12)
        p_footer.font.color.rgb = GRAY
        p_footer.alignment = PP_ALIGN.CENTER

    output = io.BytesIO()
    prs.save(output)
    output.seek(0)
    return output

# ==============================================================================
# 4. GIAO DIỆN CHÍNH
# ==============================================================================

st.markdown("""
<div class="header-container">
    <div class="logo-section"><div class="logo-icon">H</div><div><div class="brand-name">NGUYỄN VĂN HÀ</div><div class="brand-sub">AI EDUCATION • DIGITAL TRANSFORMATION</div></div></div>
    <div class="contact-info"><div style="font-size: 10px; color: #64748b; margin-bottom: 2px;">HỖ TRỢ 24/7</div><div class="phone-number">0927.2222.05</div></div>
    <div class="status-badge"><span class="dot"></span> AI NODE ACTIVE</div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="margin-top: 50px;">
    <h1 class="hero-title"><span style="color: #f97316;">PDF</span> <span style="color: white;">TO</span> <span class="gradient-text">POWERPOINT</span> <span style="color: white;">SIÊU TỐC</span></h1>
    <p class="hero-desc">Hệ thống AI chuyên dụng giúp thầy cô chuyển đổi 100% học liệu sang PowerPoint tương tác chỉ với 1 cú nhấp chuột.</p>
</div>
""", unsafe_allow_html=True)

_, main_col, _ = st.columns([1, 8, 1])
with main_col:
    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown('<div class="custom-card"><div class="step-header" style="color:#f97316">BƯỚC 1: DỮ LIỆU</div>', unsafe_allow_html=True)
        uploaded_file = st.file_uploader("Chọn file Text (.txt)", type=['txt'])
        
        default_content = """1
CÂU HỎI
Cấu trúc mạch vòng của carbohydrate nào sau đây không có nhóm -OH hemiacetal hoặc hemiketal?
A
Saccharose.
✦
B
Maltose.
C
Glucose.
D
Fructose.
2
CÂU HỎI
Carbohydrate nào sau đây kém tan trong nước lạnh nhưng tan được trong nước nóng tạo dung dịch keo, nhớt?
A
Cellulose.
B
Saccharose.
C
Tinh bột.
✦
D
Glucose.
"""
        if uploaded_file:
            stringio = io.StringIO(uploaded_file.getvalue().decode("utf-8"))
            content_input = stringio.read()
            st.success(f"Đã đọc file: {uploaded_file.name}")
        else:
            st.info("Dán nội dung vào bên dưới hoặc dùng dữ liệu mẫu:")
            content_input = st.text_area("Nội dung thô:", value=default_content, height=200)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="custom-card"><div class="step-header" style="color:#06b6d4">BƯỚC 2: XUẤT POWERPOINT</div>', unsafe_allow_html=True)
        if st.button("BẮT ĐẦU CHUYỂN ĐỔI"):
            import time
            with st.spinner("Đang xử lý dữ liệu và tạo slide..."):
                time.sleep(1)
                try:
                    questions_data = parse_exam_content(content_input)
                    if not questions_data:
                        st.warning("Không tìm thấy câu hỏi! Vui lòng kiểm tra lại nội dung đầu vào.")
                    else:
                        st.toast(f"Đã tìm thấy {len(questions_data)} câu hỏi!")
                        pptx_file = create_pptx_file(questions_data)
                        st.session_state.pptx_out = pptx_file
                        st.success("Xử lý thành công!")
                except Exception as e:
                    st.error(f"Lỗi: {e}")

        if 'pptx_out' in st.session_state:
            st.download_button(
                label="📥 TẢI POWERPOINT HOÀN CHỈNH",
                data=st.session_state.pptx_out,
                file_name="Giao_An_Hoa_Hoc_AI.pptx",
                mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
            )
        st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)
