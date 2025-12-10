import streamlit as st
import google.generativeai as genai
import os
import csv
import datetime
import random 

# --- 1. CẤU HÌNH TRANG VÀ CÁC THIẾT LẬP BAN ĐẦU ---
st.set_page_config(
    page_title="Trợ lý Học đường Toàn diện - YP2",
    page_icon="🏫",
    layout="wide"
)

# --- 2. CÁC HÀM HỖ TRỢ (Tối ưu Log) ---

def save_to_csv(role, content, mode):
    """Lưu lịch sử chat vào file Excel (CSV)"""
    try:
        file_exists = os.path.isfile('lich_su_chat.csv')
        # Dùng encoding 'utf-8-sig' để mở bằng Excel không bị lỗi phông chữ Việt
        with open('lich_su_chat.csv', mode='a', newline='', encoding='utf-8-sig') as file:
            writer = csv.writer(file)
            if not file_exists:
                writer.writerow(['Thời gian', 'Chế độ', 'Người nói', 'Nội dung'])
            
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            writer.writerow([timestamp, mode, role, content])
    except:
        pass # Bỏ qua lỗi nếu file đang mở/có sự cố I/O

# --- 3. CẤU HÌNH AI & DỮ LIỆU NỀN ---
# LẤY API KEY TỪ st.secrets ĐỂ BẢO MẬT
api_key = None
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except KeyError:
    # Trường hợp local testing
    api_key = os.environ.get("GEMINI_API_KEY", None)

model_name = "gemini-2.5-flash"

if not api_key:
    st.error("❌ Lỗi bảo mật: Không tìm thấy API Key (GEMINI_API_KEY). Vui lòng kiểm tra file .streamlit/secrets.toml")
else:
    try:
        genai.configure(api_key=api_key)
    except Exception:
        st.error("❌ Lỗi kết nối AI. Vui lòng kiểm tra mạng Internet hoặc API Key.")

# Dữ liệu Cuộc thi và Tư vấn Hướng nghiệp/Sáng tạo 
DU_LIEU_NEN = {
    "huong_nghiep": """
    DỮ LIỆU TUYỂN SINH THAM KHẢO & XU HƯỚNG NGHỀ NGHIỆP TẠI BẮC NINH:
    1. Đại học Kinh Bắc: CNTT, Quản trị kinh doanh (ĐB: 15-18).
    2. Cao đẳng Công nghiệp Bắc Ninh (BCI): Kỹ thuật điện tử (Cơ hội làm việc tại KCN Yên Phong).
    3. Xu hướng: Tập trung vào STEM (Khoa học, Kỹ thuật, Công nghệ) phục vụ nhu cầu công nghiệp hóa.
    """,
    "tam_ly": "Luôn dùng lời lẽ tích cực, ân cần như một người chị gái, thấu hiểu Gen Z, luôn lắng nghe và không phán xét. Sử dụng emoji dễ thương 😊.",
    "suc_khoe": "Cung cấp kiến thức khoa học, chính xác, trung lập về giới tính, sinh sản, dinh dưỡng, phòng chống tệ nạn (ví dụ: thuốc lá điện tử). Tác phong y học, rõ ràng và kín đáo.",
    "hoc_tap": "Cung cấp phương pháp học tập khoa học, quản lý thời gian (Pomodoro, Cornell), kỹ năng đọc hiểu, và chiến lược làm bài thi. Tác phong logic, thực tế, ngắn gọn.",
    "fun_facts": [
        "Sử dụng kỹ thuật ghi chú Cornell giúp bạn ôn tập hiệu quả hơn 30%. 💡",
        "Để ngủ sâu, hãy ngừng dùng màn hình điện thoại ít nhất 30 phút trước khi đi ngủ. 😴",
        "Não bộ của bạn có thể xử lý hình ảnh nhanh hơn 60.000 lần so với chữ viết! Hãy dùng sơ đồ tư duy.",
        "Thiếu kẽm có thể ảnh hưởng đến khả năng tập trung. Hãy bổ sung thực phẩm giàu kẽm như thịt bò, hạt bí. 🍎"
    ],
    "quiz_intro": {
        "an_nhien": "Bạn đang bị stress ở mức trung bình. Chị An Nhiên khuyên bạn nên thử kỹ thuật hít thở 4-7-8.",
        "kien_quoc": "Bạn có khuynh hướng nghề nghiệp về Kỹ thuật và Sáng tạo. Anh Kiến Quốc khuyên bạn tìm hiểu ngành Cơ điện tử hoặc Thiết kế.",
        "tri_viet": "Bạn thuộc nhóm người học trực quan (Visual Learner). Anh Trí Việt khuyên bạn dùng sơ đồ tư duy (Mind Map) để ghi nhớ."
    }
}

# --- 4. KHAI BÁO CÁC CHUYÊN GIA (PERSONA) ---
CHUYEN_GIA = {
    "Trang Chủ": {
        "banner": "banner_main.jpg",
        "welcome": "Chào mừng trở lại! Bạn muốn gặp chuyên gia nào hôm nay? 👇",
        "instruction": "Bạn là trợ lý chính, chỉ hướng dẫn học sinh chọn chế độ. Tuyệt đối không tư vấn."
    },
    "💖 Chị An Nhiên": {
        "banner": "banner_tamly.jpg",
        "welcome": "Chào em! Chị là An Nhiên - Góc bình yên của THPT YP2 đây. Hôm nay em có tâm sự gì không? 🌸",
        "instruction": f"Tên bạn là: 'Chị An Nhiên'. Vai trò: Chuyên gia Tâm lý học đường. Nhiệm vụ: Giúp giải tỏa căng thẳng, áp lực. Lưu ý: {DU_LIEU_NEN['tam_ly']}",
        "color": "#ff69b4" # Hồng
    },
    "🧭 Anh Kiến Quốc": {
        "banner": "banner_huongnghiep.jpg",
        "welcome": "Chào bạn! Anh là Kiến Quốc - Chuyên gia hướng nghiệp YP2 đây. Em đang băn khoăn về chọn trường, chọn ngành nào? 🚀",
        "instruction": f"Tên bạn là: 'Anh Kiến Quốc'. Vai trò: Chuyên gia Hướng nghiệp. Nhiệm vụ: Tư vấn chọn trường/ngành dựa trên dữ liệu sau: {DU_LIEU_NEN['huong_nghiep']}. Yêu cầu: Thông thái, phân tích logic, thực tế, chỉ tư vấn đúng trọng tâm.",
        "color": "#0044cc" # Xanh đậm
    },
    "🩺 Chị Yến Vy": {
        "banner": "banner_suckhoe.jpg",
        "welcome": "Chào em! Chị là Yến Vy - Cố vấn sức khỏe toàn diện. Em có bất kỳ câu hỏi nào cần giải đáp kín đáo không? ⚕️",
        "instruction": f"Tên bạn là: 'Chị Yến Vy'. Vai trò: Cố vấn Sức khỏe, Giới tính, Sinh sản. Nhiệm vụ: Tư vấn kiến thức sức khỏe, dậy thì, vệ sinh, phòng chống tệ nạn. Lưu ý: {DU_LIEU_NEN['suc_khoe']}",
        "color": "#008000" # Xanh lá
    },
    "🧠 Anh Trí Việt": {
        "banner": "banner_hoctap.jpg",
        "welcome": "Chào bạn! Anh là Trí Việt - Cố vấn phương pháp học. Hãy chia sẻ vấn đề học tập của bạn để tìm giải pháp! 💡",
        "instruction": f"Tên bạn là: 'Anh Trí Việt'. Vai trò: Cố vấn Phương pháp Học tập. Nhiệm vụ: Tư vấn phương pháp học, quản lý thời gian, rèn luyện kỹ năng. Lưu ý: {DU_LIEU_NEN['hoc_tap']}",
        "color": "#ff8c00" # Cam
    },
}

# --- 5. QUẢN LÝ SESSION STATE VÀ CHUYỂN CHẾ ĐỘ ---

if "mode" not in st.session_state:
    st.session_state.mode = "Trang Chủ"
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_object" not in st.session_state:
    st.session_state.chat_object = None

# Hàm chuyển đổi chế độ và reset chat
def set_mode(new_mode):
    if st.session_state.mode != new_mode:
        st.session_state.mode = new_mode
        st.session_state.messages = [] # Xóa lịch sử cũ khi đổi chuyên gia
        st.session_state.chat_object = None # Reset AI object

# --- 6. GIAO DIỆN THANH BÊN (SIDEBAR) ---
with st.sidebar:
    # A. LOGO TRƯỜNG & TITLE
    if os.path.exists("YP2.png"):
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image("YP2.png", width=120)
    st.markdown("<h2 style='text-align: center; color: #0044cc;'>TRỢ LÝ HỌC ĐƯỜNG YP2</h2>", unsafe_allow_html=True)
    st.divider()

    # B. MENU CHUYÊN GIA
    st.markdown("### 🎯 Chọn chuyên gia")
    
    # Nút Trang Chủ
    if st.button("🏠 Trang Chủ", key="btn_home"):
        set_mode("Trang Chủ")
    
    # Nút Chuyên Gia
    modes_to_display = [m for m in CHUYEN_GIA.keys() if m != "Trang Chủ"]
    for mode_name in modes_to_display:
        if st.button(mode_name, key=f"btn_{mode_name}"):
            set_mode(mode_name)
    
    st.divider()
    
    # C. THÔNG TIN CUỘC THI (Dựa trên Kế hoạch 115/KH-UBND)
    st.markdown("### 🏆 Hướng tới Cuộc thi Sáng tạo 2026")
    try:
        # Thời gian Sơ khảo: đến hết ngày 25/4/2026
        ngay_so_khao = datetime.datetime(2026, 4, 25)
        delta = ngay_so_khao - datetime.datetime.now()
        
        # Chỉ hiển thị ngày nếu còn thời gian
        if delta.days >= 0:
            st.info(f"⏳ Còn **{delta.days} ngày** đến hết hạn Sơ khảo!")
        else:
            st.warning("Đã qua hạn Sơ khảo. Chuẩn bị cho Vòng Chung khảo!")
            
        # Nút xem Cơ cấu giải thưởng THPT
        with st.expander("Cơ cấu giải thưởng Bảng THPT"):
            # Đã khắc phục lỗi cú pháp tại đây
            st.write("- 01 Giải Nhất: 12.000.000 đồng") 
            st.write("- 02 Giải Nhì: 8.000.000 đồng/giải")
            st.write("- 03 Giải Ba: 6.000.000 đồng/giải")
            st.write("- 07 KK: 4.000.000 đồng/giải")
            
    except Exception: # Bắt lỗi tổng quát hơn cho phần tính toán ngày tháng
        st.caption("Lỗi tính toán/hiển thị thông tin cuộc thi.")
    
    st.divider()
    
    # D. THÔNG TIN LIÊN HỆ
    with st.expander("📬 Liên hệ Nhóm YP2"):
        st.write("📞 Zalo: **0123456789**")
        st.write("📧 Email: nhomthisangtaoyp2@gmail.com")
        st.caption("© 2026 Copyright YenPhong2")

# --- 7. GIAO DIỆN CHÍNH (MAIN AREA) ---

current_mode_data = CHUYEN_GIA[st.session_state.mode]
banner_file = current_mode_data["banner"]
welcome_msg = current_mode_data["welcome"]
instruction = current_mode_data["instruction"]

# Hiển thị Banner
if os.path.exists(banner_file):
    st.image(banner_file, use_container_width=True)
else:
    st.title(f"🎓 {st.session_state.mode}")
    st.caption(f"File banner '{banner_file}' chưa được tìm thấy.")


# --- 7.1. Giao Diện Trang Chủ (Dashboard) ---
if st.session_state.mode == "Trang Chủ":
    
    st.markdown(f"## {welcome_msg}")
    
    # Chia 2 cột chính cho Trợ lý và Giải trí
    col_experts, col_fun = st.columns([2, 1])
    
    with col_experts:
        st.markdown("### 🌟 Gặp gỡ 4 Chuyên gia của bạn")
        # Hiển thị 4 chuyên gia dưới dạng Card (chia 2x2)
        cols = st.columns(2)
        modes_list = [m for m in CHUYEN_GIA.keys() if m != "Trang Chủ"]
        
        for i, mode_name in enumerate(modes_list):
            with cols[i % 2]:
                data = CHUYEN_GIA[mode_name]
                # Sử dụng HTML/CSS nhẹ để tạo hiệu ứng Card
                st.markdown(f"""
                <div style="padding: 15px; border-radius: 10px; border: 2px solid {data['color']}; margin-bottom: 10px;">
                    <h3 style='color: {data['color']}'>{mode_name}</h3>
                    <p>{data['welcome'].split(' - ')[-1].replace('? 🌸', '').replace('? 🚀', '').replace('? ⚕️', '').replace('? 💡', '')}</p>
                    {st.button(f"Chat với {mode_name.split(' ')[1]}", key=f"dash_btn_{mode_name}", on_click=set_mode, args=(mode_name,))}
                </div>
                """, unsafe_allow_html=True)
                
    with col_fun:
        st.markdown("### 🎵 Góc Giải Trí & Thư Giãn")
        
        # 1. Podcast Thư Giãn (Khu vực có sẵn nhạc)
        st.subheader("🎧 Podcast YP2: Giúp bạn tập trung")
        if os.path.exists("nhac_nen.mp3"):
            st.audio("nhac_nen.mp3", format="audio/mp3")
        else:
            st.caption("(Chưa có file nhạc/podcast)")
            
        st.divider()
        
        # 2. Fun Fact
        st.subheader("🧠 Fun Fact & Lời Khuyên")
        st.info(random.choice(DU_LIEU_NEN["fun_facts"]))
        
        st.divider()
        
        # 3. Mini Quiz (Đơn giản)
        st.subheader("❓ Trắc nghiệm Nhanh")
        quiz_choice = st.radio(
            "Bạn muốn làm trắc nghiệm về gì?",
            ["Mức độ Stress", "Khuynh hướng Học tập", "Khuynh hướng Nghề nghiệp"],
            key="quiz_radio"
        )
        
        if st.button("Bắt đầu Trắc nghiệm (5 câu)"):
            st.balloons()
            if quiz_choice == "Mức độ Stress":
                 st.warning("⚡ **Kết quả:** " + DU_LIEU_NEN["quiz_intro"]["an_nhien"])
            elif quiz_choice == "Khuynh hướng Học tập":
                 st.warning("💡 **Kết quả:** " + DU_LIEU_NEN["quiz_intro"]["tri_viet"])
            else:
                 st.warning("🚀 **Kết quả:** " + DU_LIEU_NEN["quiz_intro"]["kien_quoc"])
            
            st.caption("Hãy chuyển qua chuyên gia tương ứng để được tư vấn sâu hơn!")

# --- 7.2. Giao Diện Chat với Chuyên gia (4 Modes) ---
elif api_key: # Chỉ cho phép vào chế độ chat nếu có API Key
    # 1. Khởi tạo hoặc lấy đối tượng chat
    if st.session_state.chat_object is None:
        try:
            model = genai.GenerativeModel(model_name, system_instruction=instruction)
            st.session_state.chat_object = model.start_chat(history=[])
        except Exception as e:
            st.error(f"Lỗi khởi tạo AI. Vui lòng kiểm tra API Key và kết nối mạng: {e}")

    # 2. Khởi tạo lời chào ban đầu
    if not st.session_state.messages or st.session_state.messages[0].get("content") != welcome_msg:
        st.session_state.messages.insert(0, {"role": "model", "content": welcome_msg})
    
    # 3. Khu vực hiển thị nội dung chat
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.messages:
            avatar = "🤖" if message["role"] == "model" else "🧑‍🎓"
            with st.chat_message(message["role"], avatar=avatar):
                st.markdown(message["content"])

    # 4. KHU VỰC NHẬP LIỆU (Chat Input)
    user_input = st.chat_input(f"Gõ câu hỏi cho {st.session_state.mode} vào đây...")

    if user_input and st.session_state.chat_object:
        # 1. Hiển thị câu hỏi của người dùng
        st.chat_message("user", avatar="🧑‍🎓").markdown(user_input)
        st.session_state.messages.append({"role": "user", "content": user_input})
        save_to_csv("HocSinh", user_input, st.session_state.mode) # Lưu vào Excel

        # 2. Gửi sang AI xử lý
        try:
            with st.chat_message("model", avatar="🤖"):
                placeholder = st.empty()
                placeholder.markdown("⏳ *Đang suy nghĩ...*")
                
                response = st.session_state.chat_object.send_message(user_input)
                
                placeholder.markdown(response.text)

            # 3. Lưu câu trả lời của AI
            st.session_state.messages.append({"role": "model", "content": response.text})
            save_to_csv(f"AI ({st.session_state.mode})", response.text, st.session_state.mode) # Lưu vào Excel
            
        except Exception as e:
            st.error(f"Có lỗi xảy ra trong quá trình phản hồi của AI: {e}. Vui lòng thử lại sau.")
