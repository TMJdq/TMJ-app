elif st.session_state.step == 5:
    st.title("현재 증상 (턱관절 소리 및 잠김 증상)")
    st.markdown("---")

    # 세션 기본값 설정 (초기화 방지용)
    if "tmj_sound" not in st.session_state:
        st.session_state.tmj_sound = "선택 안 함"
    if "crepitus_confirmed" not in st.session_state:
        st.session_state.crepitus_confirmed = "선택 안 함"
    st.session_state.setdefault("tmj_click_context", [])
    st.session_state.setdefault("jaw_locked_now", "선택 안 함")
    st.session_state.setdefault("jaw_unlock_possible", "선택 안 함")
    st.session_state.setdefault("jaw_locked_past", "선택 안 함")
    st.session_state.setdefault("mao_fits_3fingers", "선택 안 함")

    # 턱 소리 질문
    joint_sound_options = ["딸깍소리", "사각사각소리(크레피투스)", "없음", "선택 안 함"]
    try:
        tmj_sound_index = joint_sound_options.index(st.session_state.tmj_sound)
    except ValueError:
        tmj_sound_index = 3  # "선택 안 함" 기본 인덱스

    selected_sound = st.radio(
        "턱에서 나는 소리가 있나요?",
        options=joint_sound_options,
        index=tmj_sound_index,
        key="tmj_sound"
    )

    # 딸깍소리 선택 시 상황 선택
    if st.session_state.tmj_sound == "딸깍소리":
        st.markdown("**딸깍 소리가 나는 상황을 모두 선택하세요**")
        click_options = ["입 벌릴 때", "입 다물 때", "음식 씹을 때", "기타"]
        updated_context = []
        for option in click_options:
            key = f"click_{option}"
            is_checked = option in st.session_state.tmj_click_context
            if st.checkbox(f"- {option}", value=is_checked, key=key):
                updated_context.append(option)
        st.session_state.tmj_click_context = updated_context

    # 사각사각소리(크레피투스) 선택 시 확실 여부 질문
    elif st.session_state.tmj_sound == "사각사각소리(크레피투스)":
        crepitus_options = ["예", "아니오", "선택 안 함"]
        try:
            crepitus_index = crepitus_options.index(st.session_state.crepitus_confirmed)
        except ValueError:
            crepitus_index = 2  # 기본 "선택 안 함"

        st.radio(
            "사각사각소리 확실 여부",
            options=crepitus_options,
            index=crepitus_index,
            key="crepitus_confirmed"
        )

    # 턱 잠김 조건 질문 노출 여부 판단
    show_lock_questions = (
        st.session_state.tmj_sound == "사각사각소리(크레피투스)" and
        st.session_state.crepitus_confirmed == "아니오"
    )

    if show_lock_questions:
        st.markdown("---")
        # 턱 잠김 현재 여부
        lock_now_options = ["예", "아니오", "선택 안 함"]
        try:
            jaw_locked_now_index = lock_now_options.index(st.session_state.jaw_locked_now)
        except ValueError:
            jaw_locked_now_index = 2

        st.radio(
            "**현재 턱이 걸려서 입이 잘 안 벌어지는 증상이 있나요?**",
            options=lock_now_options,
            index=jaw_locked_now_index,
            key="jaw_locked_now"
        )

        # 잠김 여부에 따른 추가 질문
        if st.session_state.jaw_locked_now == "예":
            try:
                jaw_unlock_possible_index = lock_now_options.index(st.session_state.jaw_unlock_possible)
            except ValueError:
                jaw_unlock_possible_index = 2

            st.radio(
                "**해당 증상은 저절로 또는 조작으로 풀리나요?**",
                options=lock_now_options,
                index=jaw_unlock_possible_index,
                key="jaw_unlock_possible"
            )

        elif st.session_state.jaw_locked_now == "아니오":
            try:
                jaw_locked_past_index = lock_now_options.index(st.session_state.jaw_locked_past)
            except ValueError:
                jaw_locked_past_index = 2

            st.radio(
                "**과거에 턱 잠김 또는 개방성 잠김을 경험한 적이 있나요?**",
                options=lock_now_options,
                index=jaw_locked_past_index,
                key="jaw_locked_past"
            )

            if st.session_state.jaw_locked_past == "예":
                try:
                    mao_fits_3fingers_index = lock_now_options.index(st.session_state.mao_fits_3fingers)
                except ValueError:
                    mao_fits_3fingers_index = 2

                st.radio(
                    "**입을 최대한 벌렸을 때 (MAO), 손가락 3개(40mm)가 들어가나요?**",
                    options=lock_now_options,
                    index=mao_fits_3fingers_index,
                    key="mao_fits_3fingers"
                )

    # 디버그용 세션 상태 표시 (필요 없으면 삭제 가능)
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

            if st.session_state.tmj_sound == "선택 안 함":
                errors.append("턱관절 소리 여부를 선택해주세요.")

            if st.session_state.tmj_sound == "딸깍소리" and not st.session_state.tmj_click_context:
                errors.append("딸깍소리가 언제 나는지 최소 1개 이상 선택해주세요.")

            if st.session_state.tmj_sound == "사각사각소리(크레피투스)" and st.session_state.crepitus_confirmed == "선택 안 함":
                errors.append("사각사각소리가 확실한지 여부를 선택해주세요.")

            if show_lock_questions:
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
