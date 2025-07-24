elif st.session_state.step == 5:
    st.title("현재 증상 (턱관절 소리 및 잠김 증상)")
    st.markdown("---")

    # 기본값 세팅
    st.session_state.setdefault("tmj_sound", "선택 안 함")
    st.session_state.setdefault("crepitus_confirmed", "선택 안 함")
    st.session_state.setdefault("tmj_click_context", [])
    st.session_state.setdefault("jaw_locked_now", "선택 안 함")
    st.session_state.setdefault("jaw_unlock_possible", "선택 안 함")
    st.session_state.setdefault("jaw_locked_past", "선택 안 함")
    st.session_state.setdefault("mao_fits_3fingers", "선택 안 함")

    joint_sound_options = ["딸깍소리", "사각사각소리(크레피투스)", "없음", "선택 안 함"]
    selected_sound = st.radio(
        "턱에서 나는 소리가 있나요?",
        options=joint_sound_options,
        index=joint_sound_options.index(st.session_state.tmj_sound),
        key="tmj_sound"
    )

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

    elif st.session_state.tmj_sound == "사각사각소리(크레피투스)":
        crepitus_options = ["예", "아니오", "선택 안 함"]
        st.radio(
            "사각사각소리 확실 여부",
            options=crepitus_options,
            index=crepitus_options.index(st.session_state.crepitus_confirmed),
            key="crepitus_confirmed"
        )

    show_lock_questions = (
        st.session_state.tmj_sound == "사각사각소리(크레피투스)" and
        st.session_state.crepitus_confirmed == "아니오"
    )

    if show_lock_questions:
        st.markdown("---")
        st.markdown("**현재 턱이 걸려서 입이 잘 안 벌어지는 증상이 있나요?**")
        st.radio(
            "턱이 현재 걸려있나요?",
            options=["예", "아니오", "선택 안 함"],
            index=["예", "아니오", "선택 안 함"].index(st.session_state.jaw_locked_now),
            key="jaw_locked_now"
        )

        if st.session_state.jaw_locked_now == "예":
            st.markdown("**해당 증상은 저절로 또는 조작으로 풀리나요?**")
            st.radio(
                "잠김 해소 여부",
                options=["예", "아니오", "선택 안 함"],
                index=["예", "아니오", "선택 안 함"].index(st.session_state.jaw_unlock_possible),
                key="jaw_unlock_possible"
            )

        elif st.session_state.jaw_locked_now == "아니오":
            st.markdown("**과거에 턱 잠김 또는 개방성 잠김을 경험한 적이 있나요?**")
            st.radio(
                "과거 잠김 경험 여부",
                options=["예", "아니오", "선택 안 함"],
                index=["예", "아니오", "선택 안 함"].index(st.session_state.jaw_locked_past),
                key="jaw_locked_past"
            )

            if st.session_state.jaw_locked_past == "예":
                st.markdown("**입을 최대한 벌렸을 때 (MAO), 손가락 3개(40mm)가 들어가나요?**")
                st.radio(
                    "MAO 시 손가락 3개 가능 여부",
                    options=["예", "아니오", "선택 안 함"],
                    index=["예", "아니오", "선택 안 함"].index(st.session_state.mao_fits_3fingers),
                    key="mao_fits_3fingers"
                )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("이전 단계"):
            st.session_state.step -= 1
            st.experimental_rerun()
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
                st.session_state.step += 1
                st.experimental_rerun()
