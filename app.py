import streamlit as st
from fpdf import FPDF
import datetime
import os
from PIL import Image


if 'step' not in st.session_state:
    st.session_state.step = 0
    st.session_state.validation_errors = {}

    # ✅ 진단 관련 키를 항상 세션에 포함되도록 기본값 설정
    diagnosis_keys = {
    "muscle_pressure_2s": "선택 안 함",
    "muscle_referred_pain": "선택 안 함",
    "tmj_press_pain": "선택 안 함",
    "headache_temples": "선택 안 함",
    "headache_with_jaw": "선택 안 함",
    "headache_reproduce_by_pressure": "선택 안 함",
    "headache_not_elsewhere": "선택 안 함",
    "crepitus_confirmed": "선택 안 함",
    "mao_fits_3fingers": "선택 안 함",
    "jaw_locked_now": "선택 안 함",
    "tmj_sound": "선택 안 함"
    }

    for key, default in diagnosis_keys.items():
        st.session_state.setdefault(key, default)


        
# --- 페이지 설정 ---
st.set_page_config(
    page_title="턱관절 자가 문진 시스템 | 스마트 헬스케어",
    layout="wide", 
    initial_sidebar_state="collapsed",
    menu_items={
        'About': '이 앱은 턱관절 자가 문진을 위한 도구입니다.'
    }
)


# --- 헬퍼 함수 ---
def go_next():
    st.session_state.step += 1
    st.session_state.validation_errors = {} # 다음 단계로 넘어갈 때 에러 초기화

def go_back():
    st.session_state.step -= 1
    st.session_state.validation_errors = {} # 이전 단계로 돌아갈 때 에러 초기화

st.write("세션 상태 전체 확인:", st.session_state)


# 진단 함수
def compute_diagnoses(state):
    diagnoses = []

    def is_yes(val): return val == "예"
    def is_no(val): return val == "아니오"

    # 1~3. 근육통 관련
    if is_no(state.get("muscle_pressure_2s")):
        diagnoses.append("근육통 (Myalgia)")
    elif is_yes(state.get("muscle_pressure_2s")):
        if is_yes(state.get("muscle_referred_pain")):
            diagnoses.append("방사성 근막통 (Myofascial Pain with Referral)")
        elif is_no(state.get("muscle_referred_pain")):
            diagnoses.append("근육통 (Myalgia)")
            diagnoses.append("국소 근육통 (Local Myalgia)")

    # 4. 관절통
    if is_yes(state.get("tmj_press_pain")):
        diagnoses.append("관절통 (Arthralgia)")

    # 5. TMD에 기인한 두통 (모든 조건이 "예"인 경우만)
    keys = [
        "headache_temples",
        "headache_with_jaw",
        "headache_reproduce_by_pressure",
        "headache_not_elsewhere"
    ]
    if all(is_yes(state.get(k)) for k in keys):
        diagnoses.append("TMD에 기인한 두통 (Headache attributed to TMD)")

    # 6. 퇴행성 관절 질환
    if is_yes(state.get("crepitus_confirmed_value")):
        diagnoses.append("퇴행성 관절 질환 (Degenerative Joint Disease)")

    # 7~8. 디스크 변위 (감소 없음)
    if is_yes(state.get("mao_fits_3fingers")):
        diagnoses.append("감소 없는 디스크 변위 (Disc Displacement without Reduction)")
    elif is_no(state.get("mao_fits_3fingers")):
        diagnoses.append("감소 없는 디스크 변위 - 개구 제한 동반 (Disc Displacement without Reduction with Limitation)")

    # 9. 간헐적 잠금 디스크 변위
    if is_yes(state.get("jaw_locked_now")):
        diagnoses.append("감소 동반 간헐적 잠금 디스크 변위 (Disc Displacement with reduction, with intermittent locking)")

    # 10. 딸깍소리 → 감소 동반 디스크 변위
    if state.get("tmj_sound") and "딸깍" in state.get("tmj_sound"):
        diagnoses.append("감소 동반 디스크 변위 (Disc Displacement with Reduction)")

    return diagnoses


# 총 단계 수 (0부터 시작)
total_steps = 20 

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
            st.text_input("연락처 (선택 사항)", value=st.session_state.get('phone', ''), key="phone", placeholder="예: 01012345678 (숫자만 입력)")
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

    pain_type_options = ["선택 안 함", "넓은 부위의 통증", "근육 통증", "턱관절 통증", "두통"]
    yes_no_options = ["예", "아니오", "선택 안 함"]

    def get_selectbox_index(key):
        val = st.session_state.get(key, "선택 안 함")
        try:
            return pain_type_options.index(val)
        except ValueError:
            return 0

    def get_radio_index(key):
        val = st.session_state.get(key, "선택 안 함")
        try:
            return yes_no_options.index(val)
        except ValueError:
            return 2  # "선택 안 함" 기본 인덱스

    with st.container(border=True):
        st.markdown("**아래 중 해당되는 통증 유형을 선택해주세요.**")
        st.selectbox(
            label="통증 유형 선택",
            options=pain_type_options,
            index=get_selectbox_index("pain_types"),
            key="pain_types"
        )

        st.markdown("---")

        pain_type = st.session_state.get("pain_types", "선택 안 함")

        if pain_type in ["넓은 부위의 통증", "근육 통증"]:
            st.markdown("#### 💬 근육/넓은 부위 관련")

            st.markdown("**입을 벌릴 때나 턱을 움직일 때 통증이 있나요?**")
            st.radio(
                label="",
                options=yes_no_options,
                index=get_radio_index("muscle_movement_pain"),
                key="muscle_movement_pain"
            )

            st.markdown("**근육을 2초간 눌렀을 때 통증이 느껴지나요?**")
            muscle_2s_choice = st.radio(
                label="",
                options=yes_no_options,
                index=get_radio_index("muscle_pressure_2s"),
                key="muscle_pressure_2s"
            )

            # "예"를 선택한 경우에만 5초 질문 보여주기
            if muscle_2s_choice == "예":
                st.markdown("**근육을 5초간 눌렀을 때, 통증이 다른 부위로 퍼지나요?**")
                st.radio(
                    label="",
                    options=yes_no_options,
                    index=get_radio_index("muscle_referred_pain"),
                    key="muscle_referred_pain"
                )
            else:
                # 5초 질문 답변 초기화 (선택 안 함)
                st.session_state["muscle_referred_pain"] = "선택 안 함"

        elif pain_type == "턱관절 통증":
            st.markdown("#### 💬 턱관절 관련")

            st.markdown("**입을 벌릴 때나 움직일 때 통증이 있나요?**")
            st.radio(
                label="",
                options=yes_no_options,
                index=get_radio_index("tmj_movement_pain"),
                key="tmj_movement_pain"
            )

            st.markdown("**턱관절 부위를 눌렀을 때 기존 통증이 재현되나요?**")
            st.radio(
                label="",
                options=yes_no_options,
                index=get_radio_index("tmj_press_pain"),
                key="tmj_press_pain"
            )

        elif pain_type == "두통":
            st.markdown("#### 💬 두통 관련")

            st.markdown("**두통이 관자놀이 부위에서 발생하나요?**")
            st.radio(
                label="",
                options=yes_no_options,
                index=get_radio_index("headache_temples"),
                key="headache_temples"
            )

            st.markdown("**턱을 움직일 때 두통이 심해지나요?**")
            st.radio(
                label="",
                options=yes_no_options,
                index=get_radio_index("headache_with_jaw"),
                key="headache_with_jaw"
            )

            st.markdown("**관자놀이 근육을 눌렀을 때 기존 두통이 재현되나요?**")
            st.radio(
                label="",
                options=yes_no_options,
                index=get_radio_index("headache_reproduce_by_pressure"),
                key="headache_reproduce_by_pressure"
            )

            st.markdown("**해당 두통이 다른 의학적 진단으로 설명되지 않나요?**")
            st.radio(
                label="",
                options=yes_no_options,
                index=get_radio_index("headache_not_elsewhere"),
                key="headache_not_elsewhere"
            )

    # 선택된 통증 유형에 따라 필요 없는 항목들은 '선택 안 함'으로 초기화
    if pain_type not in ["넓은 부위의 통증", "근육 통증"]:
        st.session_state["muscle_movement_pain"] = "선택 안 함"
        st.session_state["muscle_pressure_2s"] = "선택 안 함"
        st.session_state["muscle_referred_pain"] = "선택 안 함"

    if pain_type != "턱관절 통증":
        st.session_state["tmj_movement_pain"] = "선택 안 함"
        st.session_state["tmj_press_pain"] = "선택 안 함"

    if pain_type != "두통":
        st.session_state["headache_temples"] = "선택 안 함"
        st.session_state["headache_with_jaw"] = "선택 안 함"
        st.session_state["headache_reproduce_by_pressure"] = "선택 안 함"
        st.session_state["headache_not_elsewhere"] = "선택 안 함"

    col1, col2 = st.columns(2)
    with col1:
        if st.button("이전 단계"):
            go_back()

    with col2:
        if st.button("다음 단계로 이동 👉"):
            errors = []
            if pain_type == "선택 안 함":
                errors.append("통증 유형을 선택해주세요.")

            if pain_type in ["넓은 부위의 통증", "근육 통증"]:
                if st.session_state.get("muscle_movement_pain") == "선택 안 함":
                    errors.append("근육: 입 벌릴 때 통증 여부를 선택해주세요.")
                if st.session_state.get("muscle_pressure_2s") == "선택 안 함":
                    errors.append("근육: 2초간 압통 여부를 선택해주세요.")
                if st.session_state.get("muscle_pressure_2s") == "예" and st.session_state.get("muscle_referred_pain") == "선택 안 함":
                    errors.append("근육: 5초간 통증 전이 여부를 선택해주세요.")

            if pain_type == "턱관절 통증":
                if st.session_state.get("tmj_movement_pain") == "선택 안 함":
                    errors.append("턱관절: 움직일 때 통증 여부를 선택해주세요.")
                if st.session_state.get("tmj_press_pain") == "선택 안 함":
                    errors.append("턱관절: 눌렀을 때 통증 여부를 선택해주세요.")

            if pain_type == "두통":
                for key, msg in [
                    ("headache_temples", "두통: 관자놀이 여부를 선택해주세요."),
                    ("headache_with_jaw", "두통: 턱 움직임 시 두통 악화 여부를 선택해주세요."),
                    ("headache_reproduce_by_pressure", "두통: 관자놀이 압통 시 두통 재현 여부를 선택해주세요."),
                    ("headache_not_elsewhere", "두통: 다른 진단 여부를 선택해주세요.")
                ]:
                    if st.session_state.get(key) == "선택 안 함":
                        errors.append(msg)

            if errors:
                for err in errors:
                    st.warning(err)
            else:
                st.session_state.step = 6 if pain_type in ["넓은 부위의 통증", "근육 통증", "두통"] else 5

# STEP 5: 턱관절 소리 및 잠김
elif st.session_state.step == 5:
    st.title("현재 증상 (턱관절 소리 및 잠김 증상)")
    st.markdown("---")

    # 세션 기본값 설정 (최초 1회만)
    # 실제 데이터를 저장할 변수들은 여기서 초기화하고, 위젯 키와는 다르게 이름을 지정
    if "tmj_sound_value" not in st.session_state:
        st.session_state.tmj_sound_value = "선택 안 함"
    if "crepitus_confirmed_value" not in st.session_state:
        st.session_state.crepitus_confirmed_value = "선택 안 함"

    st.session_state.setdefault("tmj_click_context", [])
    st.session_state.setdefault("jaw_locked_now", "선택 안 함")
    st.session_state.setdefault("jaw_unlock_possible", "선택 안 함")
    st.session_state.setdefault("jaw_locked_past", "선택 안 함")
    st.session_state.setdefault("mao_fits_3fingers", "선택 안 함")

    # --- 턱 소리 라디오 질문 ---
    joint_sound_options = ["딸깍소리", "사각사각소리(크레피투스)", "없음", "선택 안 함"]
    
    # 위젯 키는 임시적인 용도로 사용하고, on_change 콜백을 통해 실제 데이터 변수에 저장
    selected_sound_temp = st.radio(
        "턱에서 나는 소리가 있나요?",
        options=joint_sound_options,
        key="tmj_sound_widget_key", # 위젯을 위한 별도 키
        index=joint_sound_options.index(st.session_state.tmj_sound_value), # 저장된 값으로 초기화
        on_change=lambda: setattr(st.session_state, "tmj_sound_value", st.session_state.tmj_sound_widget_key)
    )

    # st.session_state.tmj_sound_value 값을 사용하여 로직 제어
    if st.session_state.tmj_sound_value == "딸깍소리":
        st.markdown("**딸깍 소리가 나는 상황을 모두 선택하세요**")
        click_options = ["입 벌릴 때", "입 다물 때", "음식 씹을 때", "기타"]
        updated_context = []
        for option in click_options:
            key = f"click_{option}"
            is_checked = option in st.session_state.tmj_click_context
            if st.checkbox(f"- {option}", value=is_checked, key=key):
                updated_context.append(option)
        st.session_state.tmj_click_context = updated_context

    # --- 사각사각소리(크레피투스) 선택 시 ---
    elif st.session_state.tmj_sound_value == "사각사각소리(크레피투스)":
        crepitus_options = ["예", "아니오", "선택 안 함"]
        
        # 마찬가지로 위젯 키는 임시, on_change 콜백으로 실제 데이터 변수에 저장
        st.radio(
            "사각사각소리 확실 여부",
            options=crepitus_options,
            key="crepitus_confirmed_widget_key", # 위젯을 위한 별도 키
            index=crepitus_options.index(st.session_state.crepitus_confirmed_value), # 저장된 값으로 초기화
            on_change=lambda: setattr(st.session_state, "crepitus_confirmed_value", st.session_state.crepitus_confirmed_widget_key)
        )

    # 턱 잠김 조건 질문 보여줄지 판단 (이제 tmj_sound_value와 crepitus_confirmed_value 사용)
    show_lock_questions = (
        st.session_state.tmj_sound_value == "사각사각소리(크레피투스)" and
        st.session_state.crepitus_confirmed_value == "아니오"
    )

    if show_lock_questions:
        st.markdown("---")
        st.markdown("**현재 턱이 걸려서 입이 잘 안 벌어지는 증상이 있나요?**")
        st.radio(
            "턱이 현재 걸려있나요?",
            options=["예", "아니오", "선택 안 함"],
            key="jaw_locked_now"
        )

        if st.session_state.jaw_locked_now == "예":
            st.markdown("**해당 증상은 저절로 또는 조작으로 풀리나요?**")
            st.radio(
                "잠김 해소 여부",
                options=["예", "아니오", "선택 안 함"],
                key="jaw_unlock_possible"
            )

        elif st.session_state.jaw_locked_now == "아니오":
            st.markdown("**과거에 턱 잠김 또는 개방성 잠김을 경험한 적이 있나요?**")
            st.radio(
                "과거 잠김 경험 여부",
                options=["예", "아니오", "선택 안 함"],
                key="jaw_locked_past"
            )

            if st.session_state.jaw_locked_past == "예":
                st.markdown("**입을 최대한 벌렸을 때 (MAO), 손가락 3개(40mm)가 들어가나요?**")
                st.radio(
                    "MAO 시 손가락 3개 가능 여부",
                    options=["예", "아니오", "선택 안 함"],
                    key="mao_fits_3fingers"
                )

    # 세션 확인용 (디버깅 목적)
    with st.expander("🧪 세션 상태 확인"):
        st.json(st.session_state)

    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("이전 단계"):
            go_back()

    with col2:
        if st.button("다음 단계로 이동 👉"):
            errors = []

            # 이제 실제 데이터를 저장하는 변수를 검사
            if st.session_state.tmj_sound_value == "선택 안 함":
                errors.append("턱관절 소리 여부를 선택해주세요.")

            if st.session_state.tmj_sound_value == "딸깍소리" and not st.session_state.tmj_click_context:
                errors.append("딸깍소리가 언제 나는지 최소 1개 이상 선택해주세요.")

            if st.session_state.tmj_sound_value == "사각사각소리(크레피투스)" and st.session_state.crepitus_confirmed_value == "선택 안 함":
                errors.append("사각사각소리가 확실한지 여부를 선택해주세요.")

            if show_lock_questions: # show_lock_questions는 변경된 변수 이름을 사용합니다.
                if st.session_state.jaw_locked_now == "선택 안 함":
                    errors.append("현재 턱 잠김 여부를 선택해주세요.")
                if st.session_state.jaw_locked_now == "예" and st.session_state.jaw_unlock_possible == "선택 안 함":
                    errors.append("현재 턱 잠김이 풀리는지 여부를 선택해주세요.")
                if st.session_state.jaw_locked_now == "아니오":
                    if st.session_state.jaw_locked_past == "선택 안 함":
                        errors.append("과거 턱 잠김 경험 여부를 선택해주세요.")
                    elif st.session_state.jaw_locked_past == "예" and st.session_state.mao_fits_3fingers == "선택 안 함":
                        errors.append("MAO 시 손가락 3개가 들어가는지 여부를 선택해주세요.")

            if errors:
                for err in errors:
                    st.warning(err)
            else:
                st.session_state.step = 6
                
# STEP 6: 빈도 및 시기, 강도
elif st.session_state.step == 6:
    st.title("현재 증상 (빈도 및 시기)")
    st.markdown("---")

    with st.container(border=True):
        st.markdown("**통증 또는 다른 증상이 얼마나 자주 발생하나요?**")
        freq_opts = ["주 1~2회", "주 3~4회", "주 5~6회", "매일", "기타", "선택 안 함"]
        freq = st.radio("", freq_opts, index=5, key="frequency_choice")

        if freq == "기타":
            st.text_input("기타 빈도:", key="frequency_other_text")
        else:
            st.session_state.frequency_other_text = ""

        st.markdown("---")
        st.markdown("**주로 어느 시간대에 발생하나요?**")
        st.checkbox("아침", value=st.session_state.get("time_morning", False), key="time_morning")
        st.checkbox("오후", value=st.session_state.get("time_afternoon", False), key="time_afternoon")
        st.checkbox("저녁", value=st.session_state.get("time_evening", False), key="time_evening")
        st.checkbox("기타 시간대", value=st.session_state.get("time_other", False), key="time_other")

        if st.session_state.get("time_other"):
            st.text_input("기타 시간대:", key="time_other_text")
        else:
            st.session_state.time_other_text = ""

        st.markdown("---")
        st.markdown("**(통증이 있을 시) 현재 통증 정도는 어느 정도인가요? (0=없음, 10=극심한 통증)**")
        st.slider("통증 정도 선택", 0, 10, value=st.session_state.get("pain_level", 0), key="pain_level")

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("이전 단계"):
            go_back()

    with col2:
        if st.button("다음 단계로 이동 👉"):
            freq_valid = (
                freq not in ["선택 안 함", "기타"]
                or (freq == "기타" and st.session_state.frequency_other_text.strip() != "")
            )

            time_valid = (
                st.session_state.time_morning or
                st.session_state.time_afternoon or
                st.session_state.time_evening or
                (st.session_state.time_other and st.session_state.time_other_text.strip() != "")
            )

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
        st.markdown("**다음 중 해당되는 습관이 있나요?**")

        # 첫 번째 질문 보기 목록
        first_habits = {
            "이갈이 - 밤(수면 중)": "habit_bruxism_night",
            "이 악물기 - 낮": "habit_clenching_day",
            "이 악물기 - 밤(수면 중)": "habit_clenching_night",
        }

        # '없음' 체크박스
        habit_none_checked = st.checkbox(
            "없음",
            value=st.session_state.get("habit_none", False),
            key="habit_none"
        )

        # 나머지 보기 항목 체크박스
        for label, key in first_habits.items():
            st.checkbox(
                label,
                value=st.session_state.get(key, False),
                key=key,
                disabled=habit_none_checked
            )

        # '없음' 해제되면 나머지 항목 선택 해제
        if not habit_none_checked:
            for key in first_habits.values():
                if key not in st.session_state:
                    st.session_state[key] = False

        st.markdown("---")
        st.markdown("**다음 중 해당되는 습관이 있다면 모두 선택해주세요.**")

        additional_habits = [
            "옆으로 자는 습관", "코골이", "껌 씹기",
            "단단한 음식 선호(예: 견과류, 딱딱한 사탕 등)", "한쪽으로만 씹기",
            "혀 내밀기 및 밀기(이를 밀거나 입술 사이로 내미는 습관)", "손톱/입술/볼 물기",
            "손가락 빨기", "턱 괴기", "거북목/머리 앞으로 빼기",
            "음주", "흡연", "카페인", "기타"
        ]

        if 'selected_habits' not in st.session_state:
            st.session_state.selected_habits = []

        for habit in additional_habits:
            checkbox_key = f"habit_{habit.replace(' ', '_').replace('(', '').replace(')', '').replace('/', '_').replace('-', '_').replace('.', '_').replace(':', '')}"
            checked = st.checkbox(habit, value=(habit in st.session_state.selected_habits), key=checkbox_key)
            if checked and habit not in st.session_state.selected_habits:
                st.session_state.selected_habits.append(habit)
            elif not checked and habit in st.session_state.selected_habits:
                st.session_state.selected_habits.remove(habit)

        if "기타" in st.session_state.selected_habits:
            st.text_input("기타 습관을 입력해주세요:", value=st.session_state.get('habit_other_detail', ''), key="habit_other_detail")
        else:
            if 'habit_other_detail' in st.session_state:
                st.session_state.habit_other_detail = ""

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("이전 단계"):
            go_back()

    with col2:
        if st.button("다음 단계로 이동 👉"):
            has_first = any([
                st.session_state.get("habit_bruxism_night", False),
                st.session_state.get("habit_clenching_day", False),
                st.session_state.get("habit_clenching_night", False),
                st.session_state.get("habit_none", False)
            ])
            if has_first:
                go_next()
            else:
                st.warning("‘이갈이/이 악물기/없음’ 중에서 최소 한 가지를 선택해주세요.")


# STEP 8: 턱 운동 범위 및 관찰1 (Range of Motion & Observations)
elif st.session_state.step == 8:
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


# STEP 9: 턱 운동 범위 및 관찰2 (Range of Motion & Observations)
elif st.session_state.step == 9:
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

  
# STEP 10: 턱 운동 범위 및 관찰3 (Range of Motion & Observations)
elif st.session_state.step == 10:
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


# STEP 11: 근육 촉진 평가
elif st.session_state.step == 11:
    st.title("근육 촉진 평가")
    st.markdown("---")

    with st.container(border=True):
        st.markdown(
            "<span style='color:red;'>아래 항목은 검사가 필요한 항목으로, 진료 중 확인할 수 있습니다.</span>",
            unsafe_allow_html=True
        )

        st.markdown("### 의료진 촉진 소견")

        st.markdown("**측두근 촉진 소견**")
        st.text_area(
            label="측두근 촉진 소견",
            key="palpation_temporalis",
            label_visibility="collapsed",
            placeholder="검사가 필요한 항목입니다."
        )

        st.markdown("**내측 익돌근 촉진 소견**")
        st.text_area(
            label="내측 익돌근 촉진 소견",
            key="palpation_medial_pterygoid",
            label_visibility="collapsed",
            placeholder="검사가 필요한 항목입니다."
        )

        st.markdown("**외측 익돌근 촉진 소견**")
        st.text_area(
            label="외측 익돌근 촉진 소견",
            key="palpation_lateral_pterygoid",
            label_visibility="collapsed",
            placeholder="검사가 필요한 항목입니다."
        )

        st.markdown("**통증 위치 매핑 (지도 또는 상세 설명)**")
        st.text_area(
            label="통증 위치 매핑",
            key="pain_mapping",
            label_visibility="collapsed",
            placeholder="검사가 필요한 항목입니다."
        )

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("이전 단계"):
            go_back()
    with col2:
        if st.button("다음 단계로 이동 👉"):
            go_next()


# STEP 12: 귀 관련 증상
elif st.session_state.step == 12:
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
                

# STEP 13: 경추/목/어깨 관련 증상
elif st.session_state.step == 13:
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
    with st.container(border=True):
        st.markdown("**다음 중 해당되는 증상이 있다면 모두 선택해주세요. (복수 선택 가능)**")
        st.session_state.additional_symptoms = {
            "등 상부 통증": st.checkbox("등 상부 통증", key="upper_back_pain"),
            "두개저 통증 (머리 뒤통수 밑)": st.checkbox("두개저 통증", key="occipital_pain"),
            "측두부 통증 (관자놀이)": st.checkbox("측두부 통증", key="temple_pain"),
            "턱 아래 통증 (설골 주변)": st.checkbox("턱 아래 통증", key="under_jaw_pain"),
        }

    st.markdown("---")
    with st.container(border=True):
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
            
            if st.session_state.get('neck_none', False) and (st.session_state.get('neck_pain', False) or st.session_state.get('shoulder_pain', False) or st.session_state.get('stiffness', False)):
                st.warning("'없음'과 다른 증상을 동시에 선택할 수 없습니다. 다시 확인해주세요.")
            elif not symptoms_selected:
                st.warning("증상에서 최소 하나를 선택하거나 '없음'을 체크해주세요.")
            elif not trauma_selected:
                st.warning("목 외상 여부를 선택해주세요.")
            else:
                go_next()


# STEP 14: 정서적 스트레스 이력
elif st.session_state.step == 14:
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


# STEP 15: 과거 치과적 이력 (Past Dental History)
elif st.session_state.step == 15:
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

        # 추가 질문: 턱관절 질환 치료 이력
        st.markdown("---")
        st.markdown("**이전에 턱관절 질환 치료를 받은 적 있나요?**")
        st.radio(
            label="",
            options=["예", "아니오", "선택 안 함"],
            index=["예", "아니오", "선택 안 함"].index(st.session_state.get('tmd_treatment_history', '선택 안 함')) if 'tmd_treatment_history' in st.session_state else 2,
            key="tmd_treatment_history",
            label_visibility="collapsed"
        )

        if st.session_state.tmd_treatment_history == "예":
            st.text_input(
                "어떤 치료를 받으셨나요?",
                value=st.session_state.get('tmd_treatment_detail', ''),
                key="tmd_treatment_detail",
                placeholder=" "
            )

            st.text_input(
                "해당 치료에 대한 반응(효과나 문제점 등):",
                value=st.session_state.get('tmd_treatment_response', ''),
                key="tmd_treatment_response",
                placeholder=" "
            )

            st.text_input(
                "현재 복용 중인 턱관절 관련 약물이 있다면 입력해주세요:",
                value=st.session_state.get('tmd_current_medications', ''),
                key="tmd_current_medications",
                placeholder=" "
            )
        else:
            st.session_state.tmd_treatment_detail = ""
            st.session_state.tmd_treatment_response = ""
            st.session_state.tmd_current_medications = ""

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



# STEP 16: 과거 의과적 이력 (Past Medical History)
elif st.session_state.step == 16:
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


  
# STEP 17: 자극 검사
elif st.session_state.step == 17:
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


# STEP 18: 기능 평가
elif st.session_state.step == 18:
    st.title("기능 평가 (Functional Impact)")
    st.markdown("---")

    with st.container(border=True):
        st.markdown("**턱관절 증상으로 인해 일상생활(음식 섭취, 말하기, 하품 등)에 불편함을 느끼시나요?**")
        st.radio(
            label="일상생활 영향",
            options=["전혀 불편하지 않다", "약간 불편하다", "자주 불편하다", "매우 불편하다", "선택 안 함"],
            index=["전혀 불편하지 않다", "약간 불편하다", "자주 불편하다", "매우 불편하다", "선택 안 함"].index(
                st.session_state.get("impact_daily", "선택 안 함")
            ),
            key="impact_daily",
            label_visibility="collapsed"
        )

        st.markdown("---")

        st.markdown("**턱관절 증상으로 인해 직장 업무나 학업 성과에 영향을 받은 적이 있나요?**")
        st.radio(
            label="직장/학교 영향",
            options=[
                "전혀 영향 없음",
                "약간 집중에 어려움 있음",
                "자주 집중이 힘들고 성과 저하 경험",
                "매우 큰 영향으로 일/학업 중단 고려한 적 있음",
                "선택 안 함"
            ],
            index=[
                "전혀 영향 없음",
                "약간 집중에 어려움 있음",
                "자주 집중이 힘들고 성과 저하 경험",
                "매우 큰 영향으로 일/학업 중단 고려한 적 있음",
                "선택 안 함"
            ].index(st.session_state.get("impact_work", "선택 안 함")),
            key="impact_work",
            label_visibility="collapsed"
        )

        st.markdown("---")

        st.markdown("**턱관절 증상이 귀하의 전반적인 삶의 질에 얼마나 영향을 미치고 있다고 느끼시나요?**")
        st.radio(
            label="삶의 질 영향",
            options=[
                "전혀 영향을 미치지 않음",
                "약간 영향을 미침",
                "영향을 많이 받음",
                "심각하게 삶의 질 저하",
                "선택 안 함"
            ],
            index=[
                "전혀 영향을 미치지 않음",
                "약간 영향을 미침",
                "영향을 많이 받음",
                "심각하게 삶의 질 저하",
                "선택 안 함"
            ].index(st.session_state.get("impact_quality_of_life", "선택 안 함")),
            key="impact_quality_of_life",
            label_visibility="collapsed"
        )

        st.markdown("---")

        st.markdown("**최근 2주간 수면의 질은 어떠셨나요?**")
        st.radio(
            label="수면 질",
            options=["매우 좋음", "보통", "나쁨", "매우 나쁨", "선택 안 함"],
            index=["매우 좋음", "보통", "나쁨", "매우 나쁨", "선택 안 함"].index(
                st.session_state.get("sleep_quality", "선택 안 함")
            ),
            key="sleep_quality",
            label_visibility="collapsed"
        )

        st.markdown("**수면의 질이 턱관절 증상(통증, 근육 경직 등)에 영향을 준다고 느끼시나요?**")
        st.radio(
            label="수면과 턱관절 질환 연관성",
            options=["그렇다", "아니다", "잘 모르겠다", "선택 안 함"],
            index=["그렇다", "아니다", "잘 모르겠다", "선택 안 함"].index(
                st.session_state.get("sleep_tmd_relation", "선택 안 함")
            ),
            key="sleep_tmd_relation",
            label_visibility="collapsed"
        )

    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("이전 단계"):
            go_back()

    with col2:
        if st.button("제출 👉"):
            errors = []

            if st.session_state.get("impact_daily") == "선택 안 함":
                errors.append("일상생활 영향 여부를 선택해주세요.")
            if st.session_state.get("impact_work") == "해당 없음 / 선택 안 함":
                errors.append("직장/학교 영향 여부를 선택해주세요.")
            if st.session_state.get("impact_quality_of_life") == "선택 안 함":
                errors.append("삶의 질 영향 여부를 선택해주세요.")
            if st.session_state.get("sleep_quality") == "선택 안 함":
                errors.append("수면의 질을 선택해주세요.")
            if st.session_state.get("sleep_tmd_relation") == "선택 안 함":
                errors.append("수면과 턱관절 연관성 여부를 선택해주세요.")

            if errors:
                for err in errors:
                    st.warning(err)
            else:
                go_next()



# STEP 19: 결과
elif st.session_state.step == 19:
    st.title("📊 턱관절 질환 예비 진단 결과")
    st.markdown("---")

    results = compute_diagnoses(st.session_state)

    dc_tmd_explanations = {
        "근육통 (Myalgia)": "→ 턱 주변 근육에서 발생하는 통증으로, 움직임이나 압박 시 통증이 심해지는 증상입니다.",
        "국소 근육통 (Local Myalgia)": "→ 통증이 특정 근육 부위에만 국한되어 있고, 다른 부위로 퍼지지 않는 증상입니다.",
        "방사성 근막통 (Myofascial Pain with Referral)": "→ 특정 근육을 눌렀을 때 통증이 다른 부위로 방사되어 퍼지는 증상입니다.",
        "관절통 (Arthralgia)": "→ 턱관절 자체에 발생하는 통증으로, 움직이거나 누를 때 통증이 유발되는 상태입니다.",
        "퇴행성 관절 질환 (Degenerative Joint Disease)": "→ 턱관절의 연골이나 뼈가 마모되거나 손상되어 통증과 기능 제한이 동반되는 상태입니다.",
        "감소 없는 디스크 변위 (Disc Displacement without Reduction)": "→ 턱관절 디스크가 비정상 위치에 있으며, 입을 벌려도 제자리로 돌아오지 않는 상태입니다.",
        "감소 없는 디스크 변위 - 개구 제한 동반 (Disc Displacement without Reduction with Limitation)": "→ 디스크가 제자리로 돌아오지 않으며, 입 벌리기가 제한되는 상태입니다.",
        "감소 동반 간헐적 잠금 디스크 변위 (Disc Displacement with reduction, with intermittent locking)": "→ 디스크가 움직일 때 딸깍소리가 나며, 일시적인 입 벌리기 장애가 간헐적으로 나타나는 상태입니다.",
        "감소 동반 디스크 변위 (Disc Displacement with Reduction)": "→ 입을 벌릴 때 디스크가 제자리로 돌아오며 딸깍소리가 나는 상태이며, 기능 제한은 없는 경우입니다.",
        "TMD에 기인한 두통 (Headache attributed to TMD)": "→ 턱관절 또는 턱 주변 근육 문제로 인해 발생하는 두통으로, 턱을 움직이거나 근육을 누르면 증상이 악화되는 경우입니다."
    }

    st.write("디버그용 진단 결과:", results)

    if not results:
        st.success("✅ DC/TMD 기준상 명확한 진단 근거는 확인되지 않았습니다.\n\n다른 질환 가능성에 대한 조사가 필요합니다.")
    else:
        if len(results) == 1:
            st.error(f"**{results[0]}**이(가) 의심됩니다.")
        else:
            st.error(f"**{', '.join(results)}**이(가) 의심됩니다.")

        st.markdown("---")
        for diagnosis in results:
            st.markdown(f"### 🔹 {diagnosis}")
            st.info(dc_tmd_explanations.get(diagnosis, "설명 없음"))
            st.markdown("---")

    st.info("※ 본 결과는 예비 진단이며, 전문의 상담을 반드시 권장합니다.")

    if st.button("처음으로 돌아가기", use_container_width=True):
        st.session_state.step = 0
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()




