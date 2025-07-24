import streamlit as st
from fpdf import FPDF
import datetime
import os
from PIL import Image

# --- 페이지 설정 ---
st.set_page_config(
    page_title="턱관절 자가 문진 시스템 | 스마트 헬스케어",
    layout="wide", 
    initial_sidebar_state="collapsed",
    menu_items={
        'About': '이 앱은 턱관절 자가 문진을 위한 도구입니다.'
    }
)

# --- 세션 상태 초기화 ---
if 'step' not in st.session_state:
    st.session_state.step = 0
    # 사용자 데이터는 기존 st.session_state.<key> 방식으로 유지
    # st.session_state.validation_errors 딕셔너리 추가
    st.session_state.validation_errors = {}

# --- 헬퍼 함수 ---
def go_next():
    st.session_state.step += 1
    st.session_state.validation_errors = {} # 다음 단계로 넘어갈 때 에러 초기화

def go_back():
    st.session_state.step -= 1
    st.session_state.validation_errors = {} # 이전 단계로 돌아갈 때 에러 초기화

# 설명
dc_tmd_explanations = {
    "Myalgia": "근육성 통증: 씹는 근육의 과사용 또는 긴장으로 인한 통증입니다.",
    "Arthralgia": "관절 통증: 턱관절 자체의 염증이나 자극으로 발생하는 통증입니다.",
    "Headache attributed to TMD": "턱관절과 관련된 두통: 측두부의 긴장이나 통증이 턱 기능장애와 관련되어 나타납니다.",
    "Disc displacement with reduction": "턱관절 디스크가 위치 이탈 후 다시 돌아오는 상태로, 입을 벌릴 때 '딸깍' 소리가 날 수 있습니다.",
    "Disc displacement without reduction": "디스크가 위치 이탈된 채 돌아오지 않는 상태로, 입이 잘 벌어지지 않거나 움직임 제한이 있습니다.",
    "Degenerative joint disease": "퇴행성 관절 질환: 관절 연골의 마모나 퇴행으로 인해 통증, 마찰음, 기능 제한이 발생합니다."
}


# --- PDF 생성 함수 ---
def generate_pdf_report(state, diagnosis_results):
    pdf = FPDF()
    pdf.add_page()

    # 한글 폰트 설정 (malgun.ttf 파일이 코드와 같은 디렉토리에 있어야 합니다.)
    try:
        pdf.add_font('malgun', '', 'malgun.ttf', uni=True)
        pdf.set_font('malgun', '', 12)
    except RuntimeError:
        st.warning("⚠️ 'malgun.ttf' 폰트를 찾을 수 없습니다. PDF에 한글이 깨져 보일 수 있습니다. 해당 폰트 파일을 스크립트와 같은 폴더에 넣어주세요.")
        pdf.set_font('helvetica', '', 12) # 대체 폰트

    pdf.cell(0, 10, txt="턱관절 자가 문진 상세 보고서", ln=True, align='C')
    pdf.ln(10)

    # --- 환자 기본 정보 ---
    pdf.set_font('malgun', '', 10)
    pdf.cell(0, 7, txt="--- 📋 환자 기본 정보 ---", ln=True)
    pdf.multi_cell(0, 5, txt=f"이름: {state.get('name', '미입력')}")
    pdf.multi_cell(0, 5, txt=f"생년월일: {state.get('birthdate', datetime.date(1900,1,1)).strftime('%Y년 %m월 %d일')}")
    pdf.multi_cell(0, 5, txt=f"성별: {state.get('gender', '미선택')}")
    pdf.multi_cell(0, 5, txt=f"이메일: {state.get('email', '미입력')}")
    pdf.multi_cell(0, 5, txt=f"연락처: {state.get('phone', '미입력')}")
    pdf.multi_cell(0, 5, txt=f"주소: {state.get('address', '미입력')}")
    pdf.multi_cell(0, 5, txt=f"직업: {state.get('occupation', '미입력')}")
    pdf.multi_cell(0, 5, txt=f"내원 목적: {state.get('visit_reason', '미입력')}")
    pdf.ln(5)

    # --- 설문 답변 요약 ---
    pdf.cell(0, 7, txt="--- 📝 주요 설문 답변 ---", ln=True)
    pdf.set_font('malgun', '', 9)

    # 주 호소
    pdf.multi_cell(0, 5, txt=f"주 호소: {state.get('chief_complaint', '미선택')}")
    if state.get("chief_complaint") == "기타":
        pdf.multi_cell(0, 5, txt=f"  - 기타 사유: {state.get('chief_complaint_other', '미입력')}")
    pdf.multi_cell(0, 5, txt=f"첫 발생 시기: {state.get('onset', '미입력').strftime('%Y년 %m월 %d일')}")

    # 통증 부위
    pdf.multi_cell(0, 5, txt=f"통증 부위: {', '.join(state.get('selected_parts', ['없음']))}")
    
    # 통증 양상
    pdf.multi_cell(0, 5, txt=f"통증 양상: {state.get('pain_quality', '미선택')}")
    if state.get("pain_quality") == "기타":
        pdf.multi_cell(0, 5, txt=f"  - 기타 양상: {state.get('pain_quality_other', '미입력')}")
    pdf.multi_cell(0, 5, txt=f"현재 통증 정도 (0-10): {state.get('pain_level', '미선택')}")

    # 빈도 및 시기
    freq_summary = []
    if state.get('frequency', {}).get("매일"): freq_summary.append("매일")
    if state.get('frequency', {}).get("주 2~3회"): freq_summary.append("주 2~3회")
    if state.get('frequency', {}).get("기타"): freq_summary.append(f"기타({state.get('frequency', {}).get('기타')})")
    pdf.multi_cell(0, 5, txt=f"증상 빈도: {', '.join(freq_summary) if freq_summary else '미선택'}")

    time_summary = []
    if state.get('time_of_day', {}).get("아침"): time_summary.append("아침")
    if state.get('time_of_day', {}).get("오후"): time_summary.append("오후")
    if state.get('time_of_day', {}).get("저녁"): time_summary.append("저녁")
    if state.get('time_of_day', {}).get("기타"): time_summary.append(f"기타({state.get('time_of_day', {}).get('기타')})")
    pdf.multi_cell(0, 5, txt=f"주로 발생 시간: {', '.join(time_summary) if time_summary else '미선택'}")

    # 습관
    pdf.multi_cell(0, 5, txt=f"주요 습관: {', '.join(state.get('selected_habits', ['없음']))}")
    if state.get('habit_other_detail'):
        pdf.multi_cell(0, 5, txt=f"  - 기타 습관 상세: {state.get('habit_other_detail')}")

    # 두통 관련 증상
    pdf.multi_cell(0, 5, txt=f"두통 유무: {state.get('headache_option', '미선택')}")
    if state.get('headache_other'): pdf.multi_cell(0, 5, txt=f"  - 기타 두통 정보: {state.get('headache_other')}")
    
    headache_loc_summary = []
    if state.get('loc_temples', False): headache_loc_summary.append("관자놀이")
    if state.get('loc_occipital', False): headache_loc_summary.append("뒤통수")
    if state.get('loc_other_detail'): headache_loc_summary.append(f"기타({state.get('loc_other_detail')})")
    pdf.multi_cell(0, 5, txt=f"두통 위치: {', '.join(headache_loc_summary) if headache_loc_summary else '미선택'}")
    
    pdf.multi_cell(0, 5, txt=f"두통 빈도: {state.get('headache_freq', '미선택')}")
    pdf.multi_cell(0, 5, txt=f"두통 양상: {state.get('headache_type', '미선택')}")
    pdf.multi_cell(0, 5, txt=f"악화 요인: {state.get('aggravating', '미선택')}")
    pdf.multi_cell(0, 5, txt=f"완화 요인: {state.get('relieving', '미선택')}")
    pdf.multi_cell(0, 5, txt=f"두통 강도 (0-10): {state.get('headache_scale', '미선택')}")

    # 귀 관련 증상
    pdf.multi_cell(0, 5, txt=f"귀 관련 증상: {', '.join(state.get('selected_ear_symptoms', ['없음']))}")
    if state.get('ear_symptom_other'):
        pdf.multi_cell(0, 5, txt=f"  - 기타 귀 증상 상세: {state.get('ear_symptom_other')}")

    # 경추/목/어깨 관련 증상
    neck_symptoms_summary = []
    if state.get('neck_none'): neck_symptoms_summary.append("없음")
    if state.get('neck_shoulder_symptoms', {}).get('neck_pain'): neck_symptoms_summary.append("목 통증")
    if state.get('neck_shoulder_symptoms', {}).get('shoulder_pain'): neck_symptoms_summary.append("어깨 통증")
    if state.get('neck_shoulder_symptoms', {}).get('stiffness'): neck_symptoms_summary.append("뻣뻣함(강직감)")
    pdf.multi_cell(0, 5, txt=f"목/어깨 증상: {', '.join(neck_symptoms_summary) if neck_symptoms_summary else '미선택'}")
    pdf.multi_cell(0, 5, txt=f"목 외상 이력: {state.get('neck_trauma', '미선택')}")
    if state.get('neck_trauma') == '예':
        pdf.multi_cell(0, 5, txt=f"  - 외상 상세: {state.get('trauma_detail', '미입력')}")

    # 정서적 스트레스
    pdf.multi_cell(0, 5, txt=f"스트레스 유무: {state.get('stress', '미선택')}")
    if state.get('stress_other'): pdf.multi_cell(0, 5, txt=f"  - 기타 의견: {state.get('stress_other')}")
    if state.get('stress_detail'): pdf.multi_cell(0, 5, txt=f"  - 상세 내용: {state.get('stress_detail')}")

    # 과거 의과적 이력
    pdf.multi_cell(0, 5, txt=f"과거 의과적 이력: {state.get('past_history', '없음')}")
    pdf.multi_cell(0, 5, txt=f"현재 복용 약물: {state.get('current_medications', '없음')}")

    # 과거 치과적 이력
    pdf.multi_cell(0, 5, txt=f"교정치료 경험: {state.get('ortho_exp', '미선택')}")
    if state.get('ortho_exp_other'): pdf.multi_cell(0, 5, txt=f"  - 기타 교정 상세: {state.get('ortho_exp_other')}")
    if state.get('ortho_detail'): pdf.multi_cell(0, 5, txt=f"  - 교정 기간/내용: {state.get('ortho_detail')}")
    pdf.multi_cell(0, 5, txt=f"보철치료 경험: {state.get('prosth_exp', '미선택')}")
    if state.get('prosth_exp_other'): pdf.multi_cell(0, 5, txt=f"  - 기타 보철 상세: {state.get('prosth_exp_other')}")
    if state.get('prosth_detail'): pdf.multi_cell(0, 5, txt=f"  - 보철 내용: {state.get('prosth_detail')}")
    pdf.multi_cell(0, 5, txt=f"기타 치과 치료 이력: {state.get('other_dental', '없음')}")
    
    # 턱 운동 범위 및 관찰 (측정값은 사용자 입력이므로 그대로)
    pdf.multi_cell(0, 5, txt=f"자발적 개구: {state.get('active_opening', '미입력')}, 통증: {state.get('active_pain', '미선택')}")
    pdf.multi_cell(0, 5, txt=f"수동적 개구: {state.get('passive_opening', '미입력')}, 통증: {state.get('passive_pain', '미선택')}")
    pdf.multi_cell(0, 5, txt=f"편위: {state.get('deviation', '미선택')}, 편향: {state.get('deflection', '미선택')}")
    pdf.multi_cell(0, 5, txt=f"앞으로 내밀기(Protrusion): {state.get('protrusion', '미입력')}mm, 통증: {state.get('protrusion_pain', '미선택')}")
    pdf.multi_cell(0, 5, txt=f"측방운동(우): {state.get('latero_right', '미입력')}mm, 통증: {state.get('latero_right_pain', '미선택')}")
    pdf.multi_cell(0, 5, txt=f"측방운동(좌): {state.get('latero_left', '미입력')}mm, 통증: {state.get('latero_left_pain', '미선택')}")
    pdf.multi_cell(0, 5, txt=f"교합: {state.get('occlusion', '미선택')}")
    if state.get('occlusion') == '아니오':
        pdf.multi_cell(0, 5, txt=f"  - 교합 어긋남: {state.get('occlusion_shift', '미선택')}")

    # 턱관절 소리
    pdf.multi_cell(0, 5, txt=f"TMJ 소리 (우-벌릴 때): {state.get('tmj_noise_right_open', '미선택')}")
    if state.get('tmj_noise_right_open') == '기타':
        pdf.multi_cell(0, 5, txt=f"  - 상세: {state.get('tmj_noise_right_open_other', '미입력')}")
    pdf.multi_cell(0, 5, txt=f"TMJ 소리 (좌-벌릴 때): {state.get('tmj_noise_left_open', '미선택')}")
    if state.get('tmj_noise_left_open') == '기타':
        pdf.multi_cell(0, 5, txt=f"  - 상세: {state.get('tmj_noise_left_open_other', '미입력')}")
    pdf.multi_cell(0, 5, txt=f"TMJ 소리 (우-다물 때): {state.get('tmj_noise_right_close', '미선택')}")
    if state.get('tmj_noise_right_close') == '기타':
        pdf.multi_cell(0, 5, txt=f"  - 상세: {state.get('tmj_noise_right_close_other', '미입력')}")
    pdf.multi_cell(0, 5, txt=f"TMJ 소리 (좌-다물 때): {state.get('tmj_noise_left_close', '미선택')}")
    if state.get('tmj_noise_left_close') == '기타':
        pdf.multi_cell(0, 5, txt=f"  - 상세: {state.get('tmj_noise_left_close_other', '미입력')}")

    # 자극 검사
    pdf.multi_cell(0, 5, txt=f"오른쪽 어금니 물 때: {state.get('bite_right', '미선택')}")
    pdf.multi_cell(0, 5, txt=f"왼쪽 어금니 물 때: {state.get('bite_left', '미선택')}")
    pdf.multi_cell(0, 5, txt=f"압력 가하기(Loading Test): {state.get('loading_test', '미선택')}")
    pdf.multi_cell(0, 5, txt=f"저항 검사(Resistance Test): {state.get('resistance_test', '미선택')}")
    pdf.multi_cell(0, 5, txt=f"치아 마모(Attrition): {state.get('attrition', '미선택')}")

    pdf.ln(5)

    # 진단 결과
    pdf.set_font('malgun', '', 12)
    pdf.cell(0, 10, txt="--- ✨ 진단 결과 ---", ln=True)
    
    if not diagnosis_results:
        pdf.multi_cell(0, 10, txt="DC/TMD 기준상 명확한 진단 근거는 확인되지 않았습니다.")
    else:
        for diagnosis, score in diagnosis_results:
            desc = dc_tmd_explanations.get(diagnosis, "설명 없음")
            pdf.multi_cell(0, 7, txt=f"진단명: {diagnosis}")
            pdf.multi_cell(0, 7, txt=f"예상 확률: {score}%")
            pdf.multi_cell(0, 7, txt=f"설명: {desc}")
            pdf.ln(2)

    pdf.ln(5)
    pdf.set_font('malgun', '', 10)
    pdf.multi_cell(0, 7, txt="본 보고서는 자가 문진 결과를 바탕으로 한 예비 진단입니다. 정확한 진단 및 치료를 위해서는 반드시 전문 의료기관을 방문하여 의사와 상담하시기 바랍니다.")
    pdf.ln(10)

    pdf_output_path = f"턱관절_문진보고서_{datetime.date.today()}.pdf"
    pdf.output(pdf_output_path)
    return pdf_output_path

# 총 단계 수 (0부터 시작)
# 기존 0-16단계 + 새로운 0단계(Welcome) = 총 18단계 (0-17)
total_steps = 17 

# --- 사이드바 ---
st.sidebar.markdown("# 시스템 정보")
st.sidebar.info("이 시스템은 턱관절 건강 자가 점검을 돕기 위해 개발되었습니다. 제공되는 정보는 참고용이며, 의료 진단을 대체할 수 없습니다.")
st.sidebar.markdown("---")
st.sidebar.markdown(f"**현재 단계: {st.session_state.step + 1}/{total_steps + 1}**")
st.sidebar.progress((st.session_state.step + 1) / (total_steps + 1))
st.sidebar.markdown("---")
st.sidebar.markdown("### ❓ FAQ")
with st.sidebar.expander("턱관절 질환이란?"):
    st.write("턱관절 질환은 턱 주변의 근육, 관절, 인대 등에 문제가 생겨 통증, 소리, 개구 제한 등을 유발하는 상태를 말합니다.")
with st.sidebar.expander("자가 문진의 의미는?"):
    st.write("간단한 문진을 통해 스스로 증상을 파악하고, 전문가 진료의 필요성을 가늠해 볼 수 있는 초기 단계의 검사입니다.")
st.sidebar.markdown("---")
st.sidebar.markdown("### 📞 문의")
st.sidebar.write("contact@example.com") # 실제 이메일 주소로 변경
st.sidebar.write("000-1234-5678") # 실제 전화번호로 변경


# --- 메인 UI 렌더링 ---
st.title("🦷 턱관절 자가 문진 시스템")
st.markdown("---")

# STEP 0: Welcome Page (새로 추가된 단계)
if st.session_state.step == 0:
 
    st.header("✨ 당신의 턱관절 건강, 지금 바로 확인하세요!")
    st.write("""
    이 시스템은 턱관절 건강 상태를 스스로 점검하고, 잠재적인 문제를 조기에 파악할 수 있도록 설계되었습니다.
    간단한 몇 단계의 설문을 통해, 맞춤형 예비 진단 결과를 받아보세요.
    """)
    
    st.markdown("---")
    
    col_intro1, col_intro2, col_intro3 = st.columns(3)
    with col_intro1:
        st.info("**🚀 신속한 검사:** 짧은 시간 안에 주요 증상 확인")
    with col_intro2:
        st.info("**📊 직관적인 결과:** 시각적으로 이해하기 쉬운 진단 요약")
    with col_intro3:
        st.info("**📝 보고서 생성:** 개인 맞춤형 PDF 보고서 제공")

    st.markdown("---")

    with st.expander("시작하기 전에 꼭 읽어주세요!"):
        st.markdown("""
        * 본 시스템은 **의료 진단을 대체하지 않습니다.** 정확한 진단과 치료는 반드시 전문 의료기관을 방문하시기 바랍니다.
        * 제공된 모든 정보는 **익명으로 처리**되며, 개인 정보 보호를 최우선으로 합니다.
        * 솔직하게 답변해주시면 더욱 정확한 예비 진단 결과를 얻을 수 있습니다.
        """)
    
    st.markdown("---")
    if st.button("문진 시작하기 🚀", use_container_width=True):
        go_next() # Step 1로 이동 (기존 코드의 Step 0)

# STEP 1: 환자 정보 입력 (기존 코드의 STEP 0)
elif st.session_state.step == 1:
    st.header("📝 환자 기본 정보 입력")
    st.write("정확한 문진을 위해 필수 정보를 입력해주세요. (*표시는 필수 항목입니다.)")

    with st.container(border=True):
        col_name, col_birthdate = st.columns(2)
        with col_name:
            # key를 통해 세션 상태에 직접 접근하여 값 설정
            st.text_input("이름*", value=st.session_state.get('name', ''), key="name", placeholder="이름을 입력하세요")
            if 'name' in st.session_state.validation_errors:
                st.error(st.session_state.validation_errors['name'])
        with col_birthdate:
            # date_input은 datetime.date 객체를 반환하며, 초기값 설정
            # st.session_state.birthdate가 존재하지 않을 경우 오늘 날짜로 초기화
            st.date_input("생년월일*", value=st.session_state.get('birthdate', datetime.date(2000, 1, 1)), key="birthdate")
            # date_input은 기본적으로 항상 유효한 값을 가짐

        st.radio("성별*", ["남성", "여성", "기타", "선택 안 함"], index=["남성", "여성", "기타", "선택 안 함"].index(st.session_state.get('gender', '선택 안 함')), horizontal=True, key="gender")
        if 'gender' in st.session_state.validation_errors:
            st.error(st.session_state.validation_errors['gender'])

        col_email, col_phone = st.columns(2)
        with col_email:
            st.text_input("이메일*", value=st.session_state.get('email', ''), key="email", placeholder="예: user@example.com")
            if 'email' in st.session_state.validation_errors:
                st.error(st.session_state.validation_errors['email'])
        with col_phone:
            st.text_input("연락처 (선택 사항)", value=st.session_state.get('phone', ''), key="phone", placeholder="예: 010-1234-5678 (숫자만 입력)")
            # 연락처는 선택 사항이므로 유효성 검사에서 제외

        st.markdown("---") # 선택 사항 구분선
        st.text_input("주소 (선택 사항)", value=st.session_state.get('address', ''), key="address", placeholder="도로명 주소 또는 지번 주소")
        st.text_input("직업 (선택 사항)", value=st.session_state.get('occupation', ''), key="occupation", placeholder="직업을 입력하세요")
        st.text_area("내원 목적 (선택 사항)", value=st.session_state.get('visit_reason', ''), key="visit_reason", placeholder="예: 턱에서 소리가 나고 통증이 있어서 진료를 받고 싶습니다.")
    
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("이전 단계"):
            go_back()
    with col2:
        if st.button("다음 단계로 이동 👉"):
            st.session_state.validation_errors = {} 
            mandatory_fields_filled = True

            if not st.session_state.get('name'):
                st.session_state.validation_errors['name'] = "이름은 필수 입력 항목입니다."
                mandatory_fields_filled = False
            if st.session_state.get('gender') == '선택 안 함':
                st.session_state.validation_errors['gender'] = "성별은 필수 선택 항목입니다."
                mandatory_fields_filled = False
            if not st.session_state.get('email'):
                st.session_state.validation_errors['email'] = "이메일은 필수 입력 항목입니다."
                mandatory_fields_filled = False
            
            if mandatory_fields_filled:
                go_next()
            else:
                st.rerun()


# STEP 2: 주호소
elif st.session_state.step == 2:
    st.title("주 호소 (Chief Complaint)")
    st.markdown("---")

    with st.container(border=True):
        st.markdown("**이번에 병원을 방문한 주된 이유는 무엇인가요?**")
        st.radio(
            label="",
            options=[
                "턱 주변의 통증(턱 근육, 관자놀이, 귀 앞쪽)",
                "턱관절 소리/잠김",
                "턱 움직임 관련 두통",
                "기타 불편한 증상",
                "선택 안 함"
            ],
            key="chief_complaint",
            index=4,
            label_visibility="collapsed"
        )

        if st.session_state.get("chief_complaint") == "기타 불편한 증상":
            st.text_input(
                "기타 사유를 적어주세요:",
                value=st.session_state.get('chief_complaint_other', ''),
                key="chief_complaint_other"
            )
        else:
            st.session_state.chief_complaint_other = ""

        st.markdown("---")
        st.markdown("**문제가 처음 발생한 시기**")
        st.date_input(
            label="문제 발생 시기",
            value=st.session_state.get('onset', datetime.date.today()),
            key="onset",
            label_visibility="collapsed"
        )

    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("이전 단계"):
            go_back()

    with col2:
        if st.button("다음 단계로 이동 👉"):
            complaint = st.session_state.get("chief_complaint")

            if complaint == "선택 안 함":
                st.warning("주 호소 항목을 선택해주세요.")
            else:
                # 주 호소에 따라 분기
                if complaint in ["턱 주변의 통증(턱 근육, 관자놀이, 귀 앞쪽)", "턱 움직임 관련 두통"]:
                    st.session_state.step = 3  # 통증 양상
                elif complaint == "턱관절 소리/잠김":
                    st.session_state.step = 5  # 턱관절 관련
                elif complaint == "기타 불편한 증상":
                    st.session_state.step = 6  # 빈도 및 시기 등


# STEP 3: 통증 양상
elif st.session_state.step == 3:
    st.title("현재 증상 (통증 양상)")
    st.markdown("---")
    with st.container(border=True):
        st.markdown("**턱을 움직이거나 씹기, 말하기 등의 기능 또는 악습관(이갈이, 턱 괴기 등)으로 인해 통증이 악화되나요?**")
        st.radio(
            label="악화 여부",
            options=["예", "아니오","선택 안 함"],
            key="jaw_aggravation",
            index=2,
            label_visibility="collapsed"
        )
        st.markdown("---")
        st.markdown("**통증을 어떻게 표현하시겠습니까? (예: 둔함, 날카로움, 욱신거림 등)**")
        st.radio(
            label="통증 양상",
            options=["둔함", "날카로움", "욱신거림", "간헐적", "기타", "선택 안 함"],
            key="pain_quality",
            index=5,
            label_visibility="collapsed"
        )
        if st.session_state.get("pain_quality") == "기타":
            st.text_input("기타 통증 양상을 적어주세요:", value=st.session_state.get('pain_quality_other', ''), key="pain_quality_other")
        else:
            st.session_state.pain_quality_other = ""

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("이전 단계"):
            go_back()
    with col2:
        if st.button("다음 단계로 이동 👉"):
            if st.session_state.get("jaw_aggravation") == "선택 안 함":
                st.warning("악화 여부는 필수 항목입니다. 선택해주세요.")
            elif st.session_state.get("pain_quality") == "선택 안 함":
                st.warning("통증 양상 항목을 선택해주세요.")
            else:
                go_next()




# STEP 4: 통증 부위
elif st.session_state.step == 4:
    st.title("현재 증상 (통증 분류 및 검사)")
    st.markdown("---")
    with st.container(border=True):
        st.markdown("**아래 중 해당되는 통증 유형을 모두 선택해주세요.**")
        st.session_state.pain_types = st.multiselect(
            label="통증 유형 선택",
            options=["넓은 부위의 통증", "근육 통증", "턱관절 통증", "두통"],
            default=st.session_state.get("pain_types", []),
        )

        st.markdown("---")
        options = ["예", "아니오", "선택 안 함"]
        default_index = 2  # "선택 안 함"

        # 근육 또는 넓은 부위 통증 관련 질문
        if "넓은 부위의 통증" in st.session_state.pain_types or "근육 통증" in st.session_state.pain_types:
            st.markdown("#### 💬 근육/넓은 부위 관련")

            st.markdown("**입을 벌릴 때나 턱을 움직일 때 통증이 있나요?**")
            st.radio(
                label="입을 벌릴 때나 턱을 움직일 때 통증이 있나요?",
                options=options,
                index=default_index,
                key="muscle_movement_pain",
                label_visibility="collapsed"
            )

            st.markdown("**근육을 2초간 눌렀을 때 통증이 느껴지나요?**")
            st.radio(
                label="근육을 2초간 눌렀을 때 통증이 느껴지나요?",
                options=options,
                index=default_index,
                key="muscle_pressure_2s",
                label_visibility="collapsed"
            )

            if st.session_state.get("muscle_pressure_2s") == "예":
                st.markdown("**근육을 5초간 눌렀을 때, 통증이 다른 부위로 퍼지나요?**")
                st.radio(
                    label="근육을 5초간 눌렀을 때, 통증이 다른 부위로 퍼지나요?",
                    options=options,
                    index=default_index,
                    key="muscle_referred_pain",
                    label_visibility="collapsed"
                )
            st.markdown("---")

        # 턱관절 관련 질문
        if "턱관절 통증" in st.session_state.pain_types:
            st.markdown("#### 💬 턱관절 관련")

            st.markdown("**입을 벌릴 때나 움직일 때 턱관절에 통증이 있나요?**")
            st.radio(
                label="입을 벌릴 때나 움직일 때 턱관절에 통증이 있나요?",
                options=options,
                index=default_index,
                key="tmj_movement_pain",
                label_visibility="collapsed"
            )

            st.markdown("**턱관절 부위를 눌렀을 때 통증이 있나요?**")
            st.radio(
                label="턱관절 부위를 눌렀을 때 통증이 있습니까?",
                options=options,
                index=default_index,
                key="tmj_press_pain",
                label_visibility="collapsed"
            )
            st.markdown("---")

        # 두통 관련 질문
        if "두통" in st.session_state.pain_types:
            st.markdown("#### 💬 두통 관련")

            st.markdown("**두통이 관자놀이 부위에서 발생하나요까?**")
            st.radio(
                label="두통이 관자놀이 부위에서 발생하나요?",
                options=options,
                index=default_index,
                key="headache_temples",
                label_visibility="collapsed"
            )

            st.markdown("**턱을 움직일 때 두통이 심해지나요?**")
            st.radio(
                label="턱을 움직일 때 두통이 심해지나요?",
                options=options,
                index=default_index,
                key="headache_with_jaw",
                label_visibility="collapsed"
            )

            st.markdown("**관자놀이 근육을 눌렀을 때 기존 두통이 재현되나요?**")
            st.radio(
                label="관자놀이 근육을 눌렀을 때 기존 두통이 재현되나요?",
                options=options,
                index=default_index,
                key="headache_reproduce_by_pressure",
                label_visibility="collapsed"
            )

            st.markdown("**해당 두통이 다른 의학적 진단으로 설명되지 않나요?**")
            st.radio(
                label="해당 두통이 다른 의학적 진단으로 설명되지 않나요?",
                options=options,
                index=default_index,
                key="headache_not_elsewhere",
                label_visibility="collapsed"
            )

            st.markdown("---")


    # 네비게이션 버튼 영역
    col1, col2 = st.columns(2)
    with col1:
        if st.button("이전 단계"):
            go_back()

    with col2:
        if st.button("다음 단계로 이동 👉"):
            if not st.session_state.pain_types:
                st.warning("최소 하나의 통증 유형을 선택해주세요.")
            else:
                errors = []

                # 근육 관련 필수 확인
                if "넓은 부위의 통증" in st.session_state.pain_types or "근육 통증" in st.session_state.pain_types:
                    if st.session_state.get("muscle_movement_pain") == "선택 안 함":
                        errors.append("근육/넓은 부위: 입 벌릴 때 통증 여부를 선택해주세요.")
                    if st.session_state.get("muscle_pressure_2s") == "선택 안 함":
                        errors.append("근육/넓은 부위: 2초간 압통 여부를 선택해주세요.")
                    if st.session_state.get("muscle_pressure_2s") == "예" and st.session_state.get("muscle_referred_pain") == "선택 안 함":
                        errors.append("근육/넓은 부위: 5초간 통증 전이 여부를 선택해주세요.")

                # 턱관절 관련 필수 확인
                if "턱관절 통증" in st.session_state.pain_types:
                    if st.session_state.get("tmj_movement_pain") == "선택 안 함":
                        errors.append("턱관절: 움직일 때 통증 여부를 선택해주세요.")
                    if st.session_state.get("tmj_press_pain") == "선택 안 함":
                        errors.append("턱관절: 눌렀을 때 통증 여부를 선택해주세요.")

                # 두통 관련 필수 확인
                if "두통" in st.session_state.pain_types:
                    if st.session_state.get("headache_temples") == "선택 안 함":
                        errors.append("두통: 관자놀이 여부를 선택해주세요.")
                    if st.session_state.get("headache_with_jaw") == "선택 안 함":
                        errors.append("두통: 턱 움직임 시 두통 악화 여부를 선택해주세요.")
                    if st.session_state.get("headache_reproduce_by_pressure") == "선택 안 함":
                        errors.append("두통: 관자놀이 압통 시 두통 재현 여부를 선택해주세요.")
                    if st.session_state.get("headache_not_elsewhere") == "선택 안 함":
                        errors.append("두통: 다른 진단 여부를 선택해주세요.")

                if errors:
                    for err in errors:
                        st.warning(err)
                else:
                    st.session_state.step = 6


# STEP 5
elif st.session_state.step == 5:
    st.title("현재 증상 (턱관절 소리 및 잠김 증상)")
    st.markdown("---")

    with st.container(border=True):
        st.markdown("**턱에서 나는 소리가 있나요?**")
        joint_sound_options = ["딸깍소리", "사각사각소리(크레피투스)", "없음", "선택 안 함"]
        st.radio(
            label="턱 소리 종류",
            options=joint_sound_options,
            index=3,  # "선택 안 함" 기본 선택
            key="tmj_sound",
            label_visibility="collapsed"
        )

        if st.session_state.tmj_sound == "딸깍소리":
    st.markdown("**딸깍소리는 언제 발생하나요? (복수 선택 가능)**")

    all_options = ["입을 벌릴 때", "입을 닫을 때", "옆으로 움직일 때", "앞으로 움직일 때", "모두"]
    selected = st.session_state.get("tmj_click_context", [])

    updated_selected = []

    for option in all_options:
        # 각 항목을 체크박스로 표시
        checked = option in selected
        new_checked = st.checkbox(option, value=checked, key=f"click_{option}")

        if new_checked:
            updated_selected.append(option)

    # '모두'가 선택되면 나머지 자동 해제
    if "모두" in updated_selected:
        updated_selected = ["모두"]
        # 다른 checkbox들의 상태도 비활성화 필요
        for option in all_options:
            if option != "모두":
                st.session_state[f"click_{option}"] = False
    else:
        # '모두' 체크 해제
        st.session_state["click_모두"] = False

    st.session_state.tmj_click_context = updated_selected
else:
    st.session_state.tmj_click_context = []

        st.markdown("---")
        st.markdown("**현재 턱이 걸려서 입이 잘 안 벌어지는 증상이 있나요?**")
        lock_options = ["예", "아니오", "선택 안 함"]
        st.radio(
            label="턱이 현재 걸려있나요?",
            options=lock_options,
            index=2,
            key="jaw_locked_now",
            label_visibility="collapsed"
        )

        if st.session_state.get("jaw_locked_now") == "예":
            st.markdown("**해당 증상은 저절로 또는 조작으로 풀리나요?**")
            st.radio(
                label="잠김 해소 여부",
                options=["예", "아니오", "선택 안 함"],
                index=2,
                key="jaw_unlock_possible",
                label_visibility="collapsed"
            )
        elif st.session_state.get("jaw_locked_now") == "아니오":
            st.markdown("**과거에 턱 잠김 또는 개방성 잠김을 경험한 적이 있나요?**")
            st.radio(
                label="과거 잠김 경험 여부",
                options=["예", "아니오", "선택 안 함"],
                index=2,
                key="jaw_locked_past",
                label_visibility="collapsed"
            )

            if st.session_state.get("jaw_locked_past") == "예":
                st.markdown("**입을 최대한 벌렸을 때 (MAO), 손가락 3개(40mm)가 들어가나요?**")
                st.radio(
                    label="MAO 시 손가락 3개 가능 여부",
                    options=["예", "아니오", "선택 안 함"],
                    index=2,
                    key="mao_fits_3fingers",
                    label_visibility="collapsed"
                )

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("이전 단계"):
            go_back()

    with col2:
        if st.button("다음 단계로 이동 👉"):
            errors = []

            if st.session_state.tmj_sound == "선택 안 함":
                errors.append("턱관절 소리 여부를 선택해주세요.")
            if st.session_state.get("jaw_locked_now") == "선택 안 함":
                errors.append("현재 턱 잠김 여부를 선택해주세요.")

            if st.session_state.get("jaw_locked_now") == "예":
                if st.session_state.get("jaw_unlock_possible") == "선택 안 함":
                    errors.append("현재 턱 잠김이 풀리는지 여부를 선택해주세요.")
            elif st.session_state.get("jaw_locked_now") == "아니오":
                if st.session_state.get("jaw_locked_past") == "선택 안 함":
                    errors.append("과거 턱 잠김 경험 여부를 선택해주세요.")
                elif st.session_state.get("jaw_locked_past") == "예" and \
                     st.session_state.get("mao_fits_3fingers") == "선택 안 함":
                    errors.append("MAO 시 손가락 3개가 들어가는지 여부를 선택해주세요.")

            if errors:
                for err in errors:
                    st.warning(err)
            else:
                # STEP6으로 바로 이동하도록 보장
                st.session_state.step = 6


# STEP 6: 빈도 및 시기, 강도
elif st.session_state.step == 6:
    st.title("현재 증상 (빈도 및 시기)")
    st.markdown("---")

    with st.container(border=True):
        # 빈도
        st.markdown("**통증 또는 다른 증상이 얼마나 자주 발생하나요?**")
        st.checkbox("매일", value=st.session_state.get('frequency_매일', False), key="frequency_매일")
        st.checkbox("주 2~3회", value=st.session_state.get('frequency_주_2_3회', False), key="frequency_주_2_3회")
        st.checkbox("기타", value=st.session_state.get('frequency_기타', False), key="frequency_기타")

        if st.session_state.get('frequency_기타', False):
            st.text_input("기타 빈도:", value=st.session_state.get('frequency_other_text', ''), key="frequency_other_text")

        st.markdown("---")

        # 시간대
        st.markdown("**주로 어느 시간대에 발생하나요?**")
        st.checkbox("아침", value=st.session_state.get('time_morning', False), key="time_morning")
        st.checkbox("오후", value=st.session_state.get('time_afternoon', False), key="time_afternoon")
        st.checkbox("저녁", value=st.session_state.get('time_evening', False), key="time_evening")
        st.checkbox("기타 시간대", value=st.session_state.get('time_other', False), key="time_other")

        if st.session_state.get('time_other', False):
            st.text_input("기타 시간대:", value=st.session_state.get('time_other_text', ''), key="time_other_text")

        st.markdown("---")

        # 통증 정도
        st.markdown("**(통증이 있을 시)현재 통증 정도는 어느 정도인가요? (0=없음, 10=극심한 통증)**")
        st.slider("통증 정도 선택", 0, 10, value=st.session_state.get('pain_level', 0), key="pain_level")

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("이전 단계"):
            go_back()
    with col2:
        if st.button("다음 단계로 이동 👉"):
            freq_valid = st.session_state.get('frequency_매일', False) or \
                         st.session_state.get('frequency_주_2_3회', False) or \
                         (st.session_state.get('frequency_기타', False) and st.session_state.get('frequency_other_text', '').strip() != "")

            time_valid = st.session_state.get('time_morning', False) or \
                         st.session_state.get('time_afternoon', False) or \
                         st.session_state.get('time_evening', False) or \
                         (st.session_state.get('time_other', False) and st.session_state.get('time_other_text', '').strip() != "")

            if freq_valid and time_valid:
                go_next()
            else:
                if not freq_valid and not time_valid:
                    st.warning("빈도와 시간대 항목을 모두 입력하거나 선택해주세요.")
                elif not freq_valid:
                    st.warning("빈도 항목을 입력하거나 선택해주세요.")
                else:
                    st.warning("시간대 항목을 입력하거나 선택해주세요.")


# STEP 7: 습관
elif st.session_state.step == 7:
    st.title("습관 (Habits)")
    st.markdown("---")
    with st.container(border=True):
        st.markdown("**다음 중 해당되는 습관이 있다면 모두 선택해주세요.**")
        habits = [
            "이갈이 - 밤(수면 중)", "이 악물기 - 낮", "이 악물기 - 밤(수면 중)",
            "옆으로 자는 습관", "코골이", "껌 씹기",
            "단단한 음식 선호(예: 견과류, 딱딱한 사탕 등)", "한쪽으로만 씹기",
            "혀 내밀기 및 밀기(이를 밀거나 입술 사이로 내미는 습관)", "손톱/입술/볼 물기",
            "손가락 빨기", "턱 괴기", "거북목/머리 앞으로 빼기",
            "음주", "흡연", "카페인", "기타"
        ]
        
        if 'selected_habits' not in st.session_state:
            st.session_state.selected_habits = []

        # 기존 selected_habits 리스트를 기반으로 체크박스 상태 초기화
        for habit in habits:
            checkbox_key = f"habit_{habit.replace(' ', '_').replace('(', '').replace(')', '').replace('/', '_').replace('-', '_').replace('.', '_').replace(':', '')}"
            if st.checkbox(habit, value=(habit in st.session_state.selected_habits), key=checkbox_key):
                if habit not in st.session_state.selected_habits:
                    st.session_state.selected_habits.append(habit)
            else:
                if habit in st.session_state.selected_habits:
                    st.session_state.selected_habits.remove(habit)

        if "기타" in st.session_state.selected_habits:
            st.text_input("기타 습관을 입력해주세요:", value=st.session_state.get('habit_other_detail', ''), key="habit_other_detail")
        else: # '기타' 체크 해제 시 내용 초기화
            if 'habit_other_detail' in st.session_state:
                st.session_state.habit_other_detail = ""
    
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("이전 단계"):
            go_back()
    with col2:
        if st.button("다음 단계로 이동 👉"):
            if st.session_state.selected_habits:
                go_next()
            else:
                st.warning("한 가지 이상 선택해주세요.")



# STEP 8: 귀 관련 증상 (기존 코드의 STEP 7)
elif st.session_state.step == 8:
    st.title("귀 관련 증상")
    st.markdown("---")
    with st.container(border=True):
        st.markdown("**다음 중 귀와 관련된 증상이 있으신가요?**")
        ear_symptoms_list = [
            "이명 (귀울림)", "귀가 먹먹한 느낌", "귀 통증", "청력 저하", "기타", "없음"
        ]
        
        if 'selected_ear_symptoms' not in st.session_state:
            st.session_state.selected_ear_symptoms = []

        # "없음"이 선택되었는지 여부
        none_selected = st.checkbox("없음", value=("없음" in st.session_state.selected_ear_symptoms), key="ear_symptom_none_checkbox")
        if none_selected and "없음" not in st.session_state.selected_ear_symptoms:
            st.session_state.selected_ear_symptoms = ["없음"]
        elif not none_selected and "없음" in st.session_state.selected_ear_symptoms:
            st.session_state.selected_ear_symptoms.remove("없음")

        # "없음"이 선택되면 나머지 체크박스 비활성화
        disabled_others = "없음" in st.session_state.selected_ear_symptoms

        for symptom in ear_symptoms_list[:-1]: # "없음" 제외
            checkbox_key = f"ear_symptom_{symptom.replace(' ', '_').replace('(', '').replace(')', '')}"
            if st.checkbox(symptom, value=(symptom in st.session_state.selected_ear_symptoms), key=checkbox_key, disabled=disabled_others):
                if symptom not in st.session_state.selected_ear_symptoms and not disabled_others:
                    st.session_state.selected_ear_symptoms.append(symptom)
            else:
                if symptom in st.session_state.selected_ear_symptoms:
                    st.session_state.selected_ear_symptoms.remove(symptom)
        
        if "기타" in st.session_state.selected_ear_symptoms and not disabled_others:
            st.text_input("기타 귀 관련 증상을 입력해주세요:", value=st.session_state.get('ear_symptom_other', ''), key="ear_symptom_other")
        else:
            if 'ear_symptom_other' in st.session_state:
                st.session_state.ear_symptom_other = ""

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("이전 단계"):
            go_back()
    with col2:
        if st.button("다음 단계로 이동 👉"):
            # 최소 하나라도 선택되었는지 확인
            if not st.session_state.selected_ear_symptoms:
                st.warning("귀 관련 증상을 한 가지 이상 선택하거나 '없음'을 선택해주세요.")
            elif "없음" in st.session_state.selected_ear_symptoms and len(st.session_state.selected_ear_symptoms) > 1:
                st.warning("'없음'과 다른 증상을 동시에 선택할 수 없습니다. 다시 확인해주세요.")
            else:
                go_next()

# STEP 9: 경추/목/어깨 관련 증상 (기존 코드의 STEP 8)
elif st.session_state.step == 9:
    st.title("경추/목/어깨 관련 증상")
    st.markdown("---")
    with st.container(border=True):
        st.markdown("**다음 중의 증상이 있으신가요?**")
        
        none_selected_neck = st.checkbox("없음", value=st.session_state.get('neck_none', False), key="neck_none")
        
        disabled_others_neck = st.session_state.get('neck_none', False)

        st.checkbox("목 통증", value=st.session_state.get('neck_pain', False), key="neck_pain", disabled=disabled_others_neck)
        st.checkbox("어깨 통증", value=st.session_state.get('shoulder_pain', False), key="shoulder_pain", disabled=disabled_others_neck)
        st.checkbox("뻣뻣함(강직감)", value=st.session_state.get('stiffness', False), key="stiffness", disabled=disabled_others_neck)
        
        
        st.session_state.neck_shoulder_symptoms = {
            "목 통증": st.session_state.get('neck_pain', False),
            "어깨 통증": st.session_state.get('shoulder_pain', False),
            "뻣뻣함(강직감)": st.session_state.get('stiffness', False),
        }

        st.markdown("---")
        st.markdown("**목 외상 관련 이력이 있으신가요?**")
        st.radio(
            label="",
            options=["예", "아니오", "선택 안 함"],
            index=["예", "아니오", "선택 안 함"].index(st.session_state.get('neck_trauma_radio', '선택 안 함')) if 'neck_trauma_radio' in st.session_state else 2,
            key="neck_trauma_radio",
            label_visibility="collapsed"
        )
    
        if st.session_state.get('neck_trauma_radio') == "예":
            st.markdown("있다면 자세히 적어주세요:")
            st.text_input(label="", value=st.session_state.get('trauma_detail', ''), key="trauma_detail", label_visibility="collapsed")
        else:
            if 'trauma_detail' in st.session_state:
                st.session_state.trauma_detail = ""
        
        st.session_state.neck_trauma = st.session_state.get('neck_trauma_radio', '선택 안 함')

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("이전 단계"):
            go_back()
    with col2:
        if st.button("다음 단계로 이동 👉"):
            trauma_selected = st.session_state.get('neck_trauma_radio') in ["예", "아니오"]
            symptoms_selected = st.session_state.get('neck_none', False) or \
                                st.session_state.get('neck_pain', False) or \
                                st.session_state.get('shoulder_pain', False) or \
                                st.session_state.get('stiffness', False)
            
            # '없음'과 다른 증상이 동시에 선택되었는지 확인
            if st.session_state.get('neck_none', False) and (st.session_state.get('neck_pain', False) or st.session_state.get('shoulder_pain', False) or st.session_state.get('stiffness', False)):
                st.warning("'없음'과 다른 증상을 동시에 선택할 수 없습니다. 다시 확인해주세요.")
            elif not symptoms_selected:
                st.warning("증상에서 최소 하나를 선택하거나 '없음'을 체크해주세요.")
            elif not trauma_selected:
                st.warning("목 외상 여부를 선택해주세요.")
            else:
                go_next()

# STEP 10: 정서적 스트레스 이력 (기존 코드의 STEP 9)
elif st.session_state.step == 10:
    st.title("정서적 스트레스 이력")
    st.markdown("---")
    with st.container(border=True):
        st.markdown("**스트레스, 불안, 우울감 등을 많이 느끼시나요?**")
        st.radio(
            label="",
            options=["예", "아니오", "기타", "선택 안 함"],
            index=["예", "아니오", "기타", "선택 안 함"].index(st.session_state.get('stress_radio', '선택 안 함')) if 'stress_radio' in st.session_state else 3,
            key="stress_radio",
            label_visibility="collapsed"
        )
    
        if st.session_state.stress_radio == "기타":
            st.markdown("**기타 의견:**")
            st.text_input(label="", value=st.session_state.get('stress_other_input', ''), key="stress_other_input", label_visibility="collapsed")
            st.session_state.stress_other = st.session_state.stress_other_input
        else:
            if 'stress_other_input' in st.session_state:
                st.session_state.stress_other_input = ""
            st.session_state.stress_other = ""
    
        st.markdown("---")
        st.markdown("**있다면 간단히 기재해 주세요:**")
        st.text_area(
            label="",
            value=st.session_state.get('stress_detail', ''),
            key="stress_detail",
            placeholder="예: 최근 업무 스트레스, 가족 문제 등",
            label_visibility="collapsed"
        )
        st.session_state.stress = st.session_state.stress_radio

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("이전 단계"):
            go_back()
    with col2:
        if st.button("다음 단계로 이동 👉"):
            if st.session_state.stress_radio == '선택 안 함':
                st.warning("스트레스 여부를 선택해주세요.")
            else:
                go_next()

# STEP 11: 과거 의과적 이력 (Past Medical History) (기존 코드의 STEP 10)
elif st.session_state.step == 11:
    st.title("과거 의과적 이력 (Past Medical History)")
    st.markdown("---")
    with st.container(border=True):
        st.markdown("**과거에 앓았던 질환, 입원 등 주요 의학적 이력이 있다면 적어주세요:**")
        st.text_area(label="", value=st.session_state.get('past_history', ''), key="past_history", label_visibility="collapsed")
        st.markdown("---")
        st.markdown("**현재 복용 중인 약이 있다면 적어주세요:**")
        st.text_area(label="", value=st.session_state.get('current_medications', ''), key="current_medications", label_visibility="collapsed")
    
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("이전 단계"):
            go_back()
    with col2:
        if st.button("다음 단계로 이동 👉"):
            go_next()

# STEP 12: 과거 치과적 이력 (Past Dental History) (기존 코드의 STEP 11)
elif st.session_state.step == 12:
    st.title("과거 치과적 이력 (Past Dental History)")
    st.markdown("---")
    with st.container(border=True):
        # 교정치료
        st.markdown("**교정치료(치아 교정) 경험**")
        st.radio(
            label="",
            options=["예", "아니오", "기타", "선택 안 함"],
            index=["예", "아니오", "기타", "선택 안 함"].index(st.session_state.get('ortho_exp', '선택 안 함')) if 'ortho_exp' in st.session_state else 3,
            key="ortho_exp",
            label_visibility="collapsed"
        )
        if st.session_state.ortho_exp == "기타":
            st.markdown("**기타: 교정치료 관련 내용 입력**")
            st.text_input(label="", value=st.session_state.get('ortho_exp_other', ''), key="ortho_exp_other", label_visibility="collapsed")
        else:
            if 'ortho_exp_other' in st.session_state:
                st.session_state.ortho_exp_other = ""
        
        st.markdown("**예라면 언제, 얼마나 받았는지 적어주세요:**")
        st.text_input(label="", value=st.session_state.get('ortho_detail', ''), key="ortho_detail", label_visibility="collapsed")
    
        # 보철치료
        st.markdown("---")
        st.markdown("**보철치료(의치, 브리지, 임플란트 등) 경험**")
        st.radio(
            label="",
            options=["예", "아니오", "기타", "선택 안 함"],
            index=["예", "아니오", "기타", "선택 안 함"].index(st.session_state.get('prosth_exp', '선택 안 함')) if 'prosth_exp' in st.session_state else 3,
            key="prosth_exp",
            label_visibility="collapsed"
        )
        if st.session_state.prosth_exp == "기타":
            st.markdown("**기타: 보철치료 관련 내용 입력**")
            st.text_input(label="", value=st.session_state.get('prosth_exp_other', ''), key="prosth_exp_other", label_visibility="collapsed")
        else:
            if 'prosth_exp_other' in st.session_state:
                st.session_state.prosth_exp_other = ""
        
        st.markdown("**예라면 어떤 치료였는지 적어주세요:**")
        st.text_input(label="", value=st.session_state.get('prosth_detail', ''), key="prosth_detail", label_visibility="collapsed")
    
        # 기타 치과 치료
        st.markdown("---")
        st.markdown("**기타 치과 치료 이력 (주요 치과 시술, 수술 등)**")
        st.text_area(label="", value=st.session_state.get('other_dental', ''), key="other_dental", label_visibility="collapsed")
    
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("이전 단계"):
            go_back()
    with col2:
        if st.button("다음 단계로 이동 👉"):
            if st.session_state.ortho_exp == '선택 안 함' or st.session_state.prosth_exp == '선택 안 함':
                st.warning("교정치료 및 보철치료 항목을 모두 선택해주세요.")
            else:
                go_next()

# STEP 13: 턱 운동 범위 및 관찰1 (Range of Motion & Observations) (기존 코드의 STEP 12)
elif st.session_state.step == 13:
    st.title("턱 운동 범위 및 관찰 (Range of Motion & Observations)")
    st.markdown("---")
    st.markdown(
        "<span style='color:red;'>아래 항목은 실제 측정 및 검사가 필요할 수 있으며, 가능하신 부분만 기입해 주시면 됩니다. 나머지는 진료 중 확인할 수 있습니다.</span>",
        unsafe_allow_html=True
    )
    with st.container(border=True):
        # --- 자발적 개구 ---
        st.markdown("---")
        st.subheader("자발적 개구 (Active Opening)")
        st.markdown("**스스로 입을 크게 벌렸을 때 어느 정도까지 벌릴 수 있나요? (의료진이 측정 후 기록)**")
        st.text_input(label="", value=st.session_state.get('active_opening', ''), key="active_opening", label_visibility="collapsed")
        st.markdown("**통증이 있나요?**")
        st.radio(label="", options=["예", "아니오", "선택 안 함"], index=["예", "아니오", "선택 안 함"].index(st.session_state.get('active_pain', '선택 안 함')) if 'active_pain' in st.session_state else 2, key="active_pain", label_visibility="collapsed")
    
        # --- 수동적 개구 ---
        st.markdown("---")
        st.subheader("수동적 개구 (Passive Opening)")
        st.markdown("**타인이 도와서 벌렸을 때 어느 정도까지 벌릴 수 있나요? (의료진이 측정 후 기록)**")
        st.text_input(label="", value=st.session_state.get('passive_opening', ''), key="passive_opening", label_visibility="collapsed")
        st.markdown("**통증이 있나요?**")
        st.radio(label="", options=["예", "아니오", "선택 안 함"], index=["예", "아니오", "선택 안 함"].index(st.session_state.get('passive_pain', '선택 안 함')) if 'passive_pain' in st.session_state else 2, key="passive_pain", label_visibility="collapsed")
    
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("이전 단계"):
            go_back()
    with col2:
        if st.button("다음 단계로 이동 👉"):
            go_next()

# STEP 14: 턱 운동 범위 및 관찰2 (Range of Motion & Observations) (기존 코드의 STEP 13)
elif st.session_state.step == 14:
    st.title("턱 운동 범위 및 관찰 (Range of Motion & Observations)")
    st.markdown("---")
    st.markdown(
        "<span style='color:red;'>아래 항목은 실제 측정 및 검사가 필요할 수 있으며, 가능하신 부분만 기입해 주시면 됩니다. 나머지는 진료 중 확인할 수 있습니다.</span>",
        unsafe_allow_html=True
    )
    with st.container(border=True):
        # --- 턱 움직임 패턴 ---
        st.markdown("---")
        st.subheader("턱 움직임 패턴 (Mandibular Movement Pattern)")
        st.markdown("**입을 벌리고 닫을 때 턱이 한쪽으로 치우치는 것 같나요?**")
        st.radio(label="", options=["예", "아니오", "선택 안 함"], index=["예", "아니오", "선택 안 함"].index(st.session_state.get('deviation', '선택 안 함')) if 'deviation' in st.session_state else 2, key="deviation", label_visibility="collapsed")
        st.markdown("**편위(Deviation, 치우치지만 마지막에는 중앙으로 돌아옴)**")
        st.radio(label="", options=["예", "아니오", "선택 안 함"], index=["예", "아니오", "선택 안 함"].index(st.session_state.get('deviation2', '선택 안 함')) if 'deviation2' in st.session_state else 2, key="deviation2", label_visibility="collapsed")
        st.markdown("**편향(Deflection, 치우친 채 돌아오지 않음)**")
        st.radio(label="", options=["예", "아니오", "선택 안 함"], index=["예", "아니오", "선택 안 함"].index(st.session_state.get('deflection', '선택 안 함')) if 'deflection' in st.session_state else 2, key="deflection", label_visibility="collapsed")
    
        st.markdown("---")
        st.markdown("**앞으로 내밀기(Protrusion) ______ mm (의료진이 측정 후 기록)**")
        st.text_input(label="", value=st.session_state.get('protrusion', ''), key="protrusion", label_visibility="collapsed")
        st.radio("통증 여부", options=["예", "아니오", "선택 안 함"], index=["예", "아니오", "선택 안 함"].index(st.session_state.get('protrusion_pain', '선택 안 함')) if 'protrusion_pain' in st.session_state else 2, key="protrusion_pain", label_visibility="collapsed")
    
        st.markdown("---")
        st.markdown("**측방운동(Laterotrusion) 오른쪽: ______ mm (의료진이 측정 후 기록)**")
        st.text_input(label="", value=st.session_state.get('latero_right', ''), key="latero_right", label_visibility="collapsed")
        st.radio("오른쪽 통증 여부", options=["예", "아니오", "선택 안 함"], index=["예", "아니오", "선택 안 함"].index(st.session_state.get('latero_right_pain', '선택 안 함')) if 'latero_right_pain' in st.session_state else 2, key="latero_right_pain", label_visibility="collapsed")
    
        st.markdown("---")
        st.markdown("**측방운동(Laterotrusion) 왼쪽: ______ mm (의료진이 측정 후 기록)**")
        st.text_input(label="", value=st.session_state.get('latero_left', ''), key="latero_left", label_visibility="collapsed")
        st.radio("왼쪽 통증 여부", options=["예", "아니오", "선택 안 함"], index=["예", "아니오", "선택 안 함"].index(st.session_state.get('latero_left_pain', '선택 안 함')) if 'latero_left_pain' in st.session_state else 2, key="latero_left_pain", label_visibility="collapsed")
    
        st.markdown("---")
        st.markdown("**교합(Occlusion): 앞니(위, 아래)가 정중앙에서 잘 맞물리나요?**")
        st.radio(label="", options=["예", "아니오", "선택 안 함"], index=["예", "아니오", "선택 안 함"].index(st.session_state.get('occlusion', '선택 안 함')) if 'occlusion' in st.session_state else 2, key="occlusion", label_visibility="collapsed")
        if st.session_state.get("occlusion") == "아니오":
            st.markdown("**정중앙이 어느 쪽으로 어긋나는지:**")
            st.radio(label="", options=["오른쪽", "왼쪽", "선택 안 함"], index=["오른쪽", "왼쪽", "선택 안 함"].index(st.session_state.get('occlusion_shift', '선택 안 함')) if 'occlusion_shift' in st.session_state else 2, key="occlusion_shift", label_visibility="collapsed")
    
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("이전 단계"):
            go_back()
    with col2:
        if st.button("다음 단계로 이동 👉"):
            go_next()
  
# STEP 15: 턱 운동 범위 및 관찰3 (Range of Motion & Observations) (기존 코드의 STEP 14)
elif st.session_state.step == 15:
    st.title("턱 운동 범위 및 관찰 (Range of Motion & Observations)")
    st.markdown("---")
    st.markdown(
        "<span style='color:red;'>아래 항목은 실제 측정 및 검사가 필요할 수 있으며, 가능하신 부분만 기입해 주시면 됩니다. 나머지는 진료 중 확인할 수 있습니다.</span>",
        unsafe_allow_html=True
    )
    with st.container(border=True):
        # --- 턱관절 소리 ---
        st.markdown("---")
        st.subheader("턱관절 소리 (TMJ Noise)")
    
        st.markdown("**오른쪽 - 입 벌릴 때**")
        st.radio(label="", options=["딸깍/소리", "없음", "기타", "선택 안 함"], index=["딸깍/소리", "없음", "기타", "선택 안 함"].index(st.session_state.get('tmj_noise_right_open', '선택 안 함')) if 'tmj_noise_right_open' in st.session_state else 3, key="tmj_noise_right_open", label_visibility="collapsed")
        if st.session_state.tmj_noise_right_open == "기타":
            st.text_input("기타 내용 (오른쪽-벌릴 때):", value=st.session_state.get('tmj_noise_right_open_other', ''), key="tmj_noise_right_open_other")
        else:
            if 'tmj_noise_right_open_other' in st.session_state:
                st.session_state.tmj_noise_right_open_other = ""
    
        st.markdown("---")
        st.markdown("**왼쪽 - 입 벌릴 때**")
        st.radio(label="", options=["딸깍/소리", "없음", "기타", "선택 안 함"], index=["딸깍/소리", "없음", "기타", "선택 안 함"].index(st.session_state.get('tmj_noise_left_open', '선택 안 함')) if 'tmj_noise_left_open' in st.session_state else 3, key="tmj_noise_left_open", label_visibility="collapsed")
        if st.session_state.tmj_noise_left_open == "기타":
            st.text_input("기타 내용 (왼쪽-벌릴 때):", value=st.session_state.get('tmj_noise_left_open_other', ''), key="tmj_noise_left_open_other")
        else:
            if 'tmj_noise_left_open_other' in st.session_state:
                st.session_state.tmj_noise_left_open_other = ""
    
        st.markdown("---")
        st.markdown("**오른쪽 - 입 다물 때**")
        st.radio(label="", options=["딸깍/소리", "없음", "기타", "선택 안 함"], index=["딸깍/소리", "없음", "기타", "선택 안 함"].index(st.session_state.get('tmj_noise_right_close', '선택 안 함')) if 'tmj_noise_right_close' in st.session_state else 3, key="tmj_noise_right_close", label_visibility="collapsed")
        if st.session_state.tmj_noise_right_close == "기타":
            st.text_input("기타 내용 (오른쪽-다물 때):", value=st.session_state.get('tmj_noise_right_close_other', ''), key="tmj_noise_right_close_other")
        else:
            if 'tmj_noise_right_close_other' in st.session_state:
                st.session_state.tmj_noise_right_close_other = ""
    
        st.markdown("---")
        st.markdown("**왼쪽 - 입 다물 때**")
        st.radio(label="", options=["딸깍/소리", "없음", "기타", "선택 안 함"], index=["딸깍/소리", "없음", "기타", "선택 안 함"].index(st.session_state.get('tmj_noise_left_close', '선택 안 함')) if 'tmj_noise_left_close' in st.session_state else 3, key="tmj_noise_left_close", label_visibility="collapsed")
        if st.session_state.tmj_noise_left_close == "기타":
            st.text_input("기타 내용 (왼쪽-다물 때):", value=st.session_state.get('tmj_noise_left_close_other', ''), key="tmj_noise_left_close_other")
        else:
            if 'tmj_noise_left_close_other' in st.session_state:
                st.session_state.tmj_noise_left_close_other = ""
    
    st.markdown("---")    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("이전 단계"):
            go_back()
    with col2:
        if st.button("다음 단계로 이동 👉"):
            go_next()
  
# STEP 16: 자극 검사 (기존 코드의 STEP 15)
elif st.session_state.step == 16:
    st.title("자극 검사 (Provocation Tests)")
    st.markdown("---")
    with st.container(border=True):
        st.markdown("**오른쪽으로 어금니를 강하게 물 때:**")
        st.radio(label="", options=["통증", "통증 없음", "선택 안 함"], index=["통증", "통증 없음", "선택 안 함"].index(st.session_state.get('bite_right', '선택 안 함')) if 'bite_right' in st.session_state else 2, key="bite_right", label_visibility="collapsed")
    
        st.markdown("---")
        st.markdown("**왼쪽으로 어금니를 강하게 물 때:**")
        st.radio(label="", options=["통증", "통증 없음", "선택 안 함"], index=["통증", "통증 없음", "선택 안 함"].index(st.session_state.get('bite_left', '선택 안 함')) if 'bite_left' in st.session_state else 2, key="bite_left", label_visibility="collapsed")
    
        st.markdown("---")
        st.markdown("**압력 가하기 (Loading Test):**")
        st.radio(label="", options=["통증", "통증 없음", "선택 안 함"], index=["통증", "통증 없음", "선택 안 함"].index(st.session_state.get('loading_test', '선택 안 함')) if 'loading_test' in st.session_state else 2, key="loading_test", label_visibility="collapsed")
    
        st.markdown("---")
        st.markdown("**저항 검사 (Resistance Test, 턱 움직임 막기):**")
        st.radio(label="", options=["통증", "통증 없음", "선택 안 함"], index=["통증", "통증 없음", "선택 안 함"].index(st.session_state.get('resistance_test', '선택 안 함')) if 'resistance_test' in st.session_state else 2, key="resistance_test", label_visibility="collapsed")
    
        st.markdown("---")
        st.markdown("**치아 마모 (Attrition)**")
        st.radio(label="", options=["경미", "중간", "심함", "선택 안 함"], index=["경미", "중간", "심함", "선택 안 함"].index(st.session_state.get('attrition', '선택 안 함')) if 'attrition' in st.session_state else 3, key="attrition", label_visibility="collapsed")
    
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("이전 단계"):
            go_back()
    with col2:
        if st.button("다음 단계로 이동 👉"):
            go_next()

# STEP 17: 결과 (기존 코드의 STEP 16)
elif st.session_state.step == 17:
    st.title("📊 턱관절 질환 예비 진단 결과")
    st.markdown("---")

    try:
        results = compute_probability_scores(st.session_state)
    except Exception as e:
        st.error(f"진단 중 오류가 발생했습니다: {e}")
        st.stop()
    
    st.subheader("💡 당신의 턱관절 건강 상태:")
    # 진단 결과 메시지 및 색상 강조
    overall_diagnosis = "DC/TMD 기준상 명확한 진단 근거는 확인되지 않았습니다."
    highest_score = 0
    
    for diagnosis, score in results:
        if score > highest_score:
            highest_score = score
        if "Myalgia" == diagnosis and score > 50:
            overall_diagnosis = "근육성 턱관절 통증 가능성이 높습니다."
        elif "Arthralgia" == diagnosis and score > 50:
            overall_diagnosis = "턱관절 관절염(관절 통증) 가능성이 높습니다."
        elif "Headache attributed to TMD" == diagnosis and score > 50:
            overall_diagnosis = "턱관절 관련 두통 가능성이 높습니다."
        elif "Disc displacement with reduction" == diagnosis and score > 50:
            overall_diagnosis = "턱관절 디스크 재위치 이탈(딸깍 소리) 가능성이 높습니다."
        elif "Disc displacement without reduction" == diagnosis and score > 0: # 0%가 아니면 바로 표시
            overall_diagnosis = "턱관절 디스크 비환원성 전위(입 벌림 제한) 가능성이 높습니다."
            break # 이 경우 가장 심각한 것으로 간주하고 바로 표시
        elif "Degenerative joint disease" == diagnosis and score > 50:
            overall_diagnosis = "턱관절 퇴행성 관절 질환 가능성이 높습니다."

    if highest_score >= 80:
        st.error(f"## 🚨 {overall_diagnosis}")
        st.markdown("---")
        st.warning("🚨 **매우 높은 위험군입니다. 즉시 전문의와 상담할 것을 강력히 권장합니다.**")
    elif highest_score >= 50:
        st.warning(f"## ⚠️ {overall_diagnosis}")
        st.markdown("---")
        st.info("💡 **전문가와 상담을 고려해 볼 시기입니다.**")
    elif highest_score > 0:
        st.info(f"## 🌱 {overall_diagnosis}")
        st.markdown("---")
        st.success("👍 **경과를 관찰하며 관리하는 것이 좋습니다.**")
    else:
        st.success(f"## ✅ {overall_diagnosis}")
        st.markdown("---")
        st.success("👍 **현재 문진 상 턱관절 질환 가능성이 낮습니다.**")
        
    st.markdown("---")
    st.markdown("아래는 DC/TMD 기반 문진 결과를 바탕으로 예측된 질환 및 확률입니다.")
    st.markdown("---")
  
    shown_diagnosis_details = False
    for diagnosis, score in results:
        if score > 0:
            shown_diagnosis_details = True
            desc = dc_tmd_explanations.get(diagnosis, "설명 없음")
            st.markdown(f"### 🟠 {diagnosis}")
            st.progress(score / 100.0) # 진행 바는 0.0 ~ 1.0
            st.markdown(f"**예상 확률**: {score}%")
            st.markdown(f"📝 {desc}")
            st.markdown("---")
  
    if not shown_diagnosis_details:
        st.info("세부 진단 기준에 부합하는 항목이 없습니다. 전반적으로 턱관절 질환 가능성이 낮음을 시사합니다.")
  
    st.markdown("---")
    st.subheader("🏥 권장 사항")
    if highest_score >= 50: # 높은 가능성 또는 매우 높은 가능성
        st.markdown("""
        * **전문가 상담 필수:** 가까운 치과, 구강내과 또는 턱관절 전문 병원을 방문하여 정확한 진단과 치료 계획을 세우는 것이 매우 중요합니다.
        * **생활 습관 관리:** 턱관절에 부담을 줄 수 있는 딱딱하거나 질긴 음식 섭취를 피하고, 턱 괴는 습관, 이갈이/이 악물기 등을 의식적으로 줄이려 노력하세요.
        * **스트레스 관리:** 스트레스는 턱관절 증상을 악화시키는 주요 요인입니다. 명상, 요가, 취미 활동 등을 통해 스트레스를 효과적으로 관리하는 방법을 찾아보세요.
        * **온/냉찜질:** 턱 주변 근육 통증이 있을 경우 온찜질(근육 이완), 붓기가 있거나 급성 통증 시 냉찜질(염증 완화)이 도움이 될 수 있습니다.
        """)
    else: # 낮은 가능성 또는 정상 범위
        st.markdown("""
        * **정기적인 관찰:** 현재는 큰 문제가 없는 것으로 보이지만, 턱에서 소리가 나거나 통증이 느껴지는 등 새로운 증상이 나타나면 다시 문진을 시도하거나 전문가와 상담하세요.
        * **턱 건강 유지 습관:** 올바른 자세 유지, 충분한 수면, 균형 잡힌 식사 등 전반적인 건강 관리가 턱 건강에도 중요합니다.
        * **규칙적인 스트레칭:** 턱 주변 근육을 부드럽게 스트레칭하여 긴장을 완화하는 것이 좋습니다.
        """)

    st.markdown("---")
    st.subheader("보고서 다운로드")
    st.write("현재 문진 결과를 PDF 보고서로 다운로드할 수 있습니다.")

    pdf_file_path = generate_pdf_report(st.session_state, results)
    with open(pdf_file_path, "rb") as pdf_file:
        st.download_button(
            label="📄 PDF 보고서 다운로드",
            data=pdf_file,
            file_name=os.path.basename(pdf_file_path),
            mime="application/pdf"
        )
    
    st.markdown("---")
    st.info("본 시스템의 진단은 참고용이며, 의료 진단을 대체할 수 없습니다. 정확한 진단과 치료를 위해서는 반드시 전문 의료기관을 방문하여 의사와 상담하세요.")
    
    if st.button("처음으로 돌아가기", use_container_width=True):
        st.session_state.step = 0
        # 모든 세션 상태 초기화 (필수)
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.experimental_rerun()
