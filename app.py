import streamlit as st
import pandas as pd

# 🌟 별자리 기호와 이름 매핑
ZODIAC_SIGNS = {
    "♈": "Aries", "♉": "Taurus", "♊": "Gemini", "♋": "Cancer",
    "♌": "Leo", "♍": "Virgo", "♎": "Libra", "♏": "Scorpio",
    "♐": "Sagittarius", "♑": "Capricorn", "♒": "Aquarius", "♓": "Pisces"
}
SIGN_KEYS = list(ZODIAC_SIGNS.values())

# 🌙 Aspect별 허용 오브 (단위: 분)
ORB_RANGES = {
    "Conjunction": 480, "Opposition": 480,
    "Trine1": 360, "Trine2": 360,
    "Square1": 360, "Square2": 360,
    "Quintile1": 120, "Quintile2": 120,
    "Bi-quintile1": 120, "Bi-quintile2": 120,
    "Sextile1": 240, "Sextile2": 240,
    "Septile1": 60, "Septile2": 60,
    "Bi-septile1": 60, "Bi-septile2": 60,
    "Tri-septile1": 60, "Tri-septile2": 60,
    "Octile1": 180, "Octile2": 180,
    "Sesquiquadrate1": 180, "Sesquiquadrate2": 180,
    "Novile1": 60, "Novile2": 60,
    "Bi-novile1": 60, "Bi-novile2": 60,
    "Decile1": 90, "Decile2": 90,
    "Tri-decile1": 90, "Tri-decile2": 90,
    "Undecile1": 30, "Undecile2": 30,
    "Bi-undecile1": 30, "Bi-undecile2": 30,
    "Tri-undecile1": 30, "Tri-undecile2": 30,
    "Quad-undecile1": 30, "Quad-undecile2": 30,
    "Quin-undecile1": 30, "Quin-undecile2": 30,
    "Semi-sextile1": 120, "Semi-sextile2": 120,
    "Quincunx1": 180, "Quincunx2": 180,
}

# 🧮 도수+분 문자열을 분 단위로 환산하는 함수
def parse_position(value):
    if not isinstance(value, str):
        return None
    try:
        parts = value.strip().split()
        sign_symbol = parts[0]
        degree_part, minute_part = parts[1].split("°")
        degree = int(degree_part)
        minute = int(minute_part.replace("'", "").replace("′", ""))
        sign_index = list(ZODIAC_SIGNS.keys()).index(sign_symbol)
        return sign_index * 1800 + degree * 60 + minute
    except Exception:
        return None

# 📚 Aspects 시트 불러오기
@st.cache_data
def load_aspects():
    df = pd.read_excel("Aspects.xlsx", sheet_name="Aspects")
    for col in df.columns[3:]:
        df[col] = df[col].apply(parse_position)
    return df

df_aspects = load_aspects()

# 🌞 입력값 → 전체 분(row index)로 변환
def to_row_index(sign: str, degree: int, minute: int):
    sign_index = SIGN_KEYS.index(sign)
    return sign_index * 1800 + degree * 60 + minute

# 🧩 UI 시작
st.title("🔮 Personal Aspect Mapper (Lookup Ver.)")
st.caption("엑셀의 물리적 row 기반으로 lookup하는 방식 (수학 계산 없음).")

# 세션 상태 초기화
if "points" not in st.session_state:
    st.session_state.points = []

# 🌠 포인트 추가 폼
with st.form("add_point_form", clear_on_submit=True):
    st.subheader("📍 포인트 추가")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        label = st.text_input("Label (예: Sun)", key="label")
    with col2:
        sign = st.selectbox("Sign", SIGN_KEYS, key="sign")
    with col3:
        degree = st.number_input("Degree", 0, 29, 0, step=1, key="degree")
    with col4:
        minute = st.number_input("Minute", 0, 59, 0, step=1, key="minute")
    submitted = st.form_submit_button("➕ 등록")

if submitted and label:
    row_index = to_row_index(sign, degree, minute)
    st.session_state.points.append((label, row_index))
    st.success(f"✅ {label} 등록 완료 ({sign} {degree}°{minute}′)")

# 현재 등록된 포인트 표시 + 개별 삭제
if st.session_state.points:
    st.markdown("📋 **현재 등록된 지표들:**")
    for i, (label, row) in enumerate(st.session_state.points):
        sign_index = row // 1800
        deg = (row % 1800) // 60
        min_ = row % 60
        cols = st.columns([4, 1])
        cols[0].markdown(f"- **{label}** — {SIGN_KEYS[sign_index]} {deg}°{min_}′")
        if cols[1].button("🗑️", key=f"del_{i}"):
            st.session_state.points.pop(i)
            st.rerun()

    st.caption("🗑️ 버튼을 누르면 개별 항목이 삭제됩니다.")

st.divider()


# ⚡ Aspect + Pattern 통합 계산 버튼
if st.button("🔍 Calculate Aspects & Patterns"):
    results = []
    n = len(st.session_state.points)

    for i in range(n):
        for j in range(i + 1, n):
            label1, row1 = st.session_state.points[i]
            label2, row2 = st.session_state.points[j]

            diff = abs(row1 - row2)
            diff = min(diff, 21600 - diff)  # 원형 구조 처리

            # Conjunction 별도 처리
            if diff <= ORB_RANGES["Conjunction"]:
                orb_val = diff / 60
                results.append({
                    "From": label1,
                    "To": label2,
                    "Aspect": "Conjunction",
                    "Orb": f"{orb_val:.2f}°"
                })
                continue

            # 나머지 lookup 기반
            for aspect, orb in ORB_RANGES.items():
                if aspect not in df_aspects.columns:
                    continue

                target_row = df_aspects.loc[row1, aspect]
                if pd.isna(target_row):
                    continue

                diff_to_target = abs(row2 - target_row)
                diff_to_target = min(diff_to_target, 21600 - diff_to_target)

                if diff_to_target <= orb:
                    orb_val = diff_to_target / 60
                    clean_aspect = ''.join([c for c in aspect if not c.isdigit()])
                    if any(r for r in results if {r['From'], r['To']} == {label1, label2} and r['Aspect'] == clean_aspect):
                        continue
                    results.append({
                        "From": label1,
                        "To": label2,
                        "Aspect": clean_aspect,
                        "Orb": f"{orb_val:.2f}°"
                    })

    # 결과가 없을 경우
    if not results:
        st.warning("⚠️ No valid aspects found.")
        st.stop()

    # ✅ Aspect 결과 표시
    st.success("✅ Aspect & Pattern analysis complete!")
    df_results = pd.DataFrame(results)
    st.dataframe(df_results, use_container_width=True)
    csv = df_results.to_csv(index=False, encoding="utf-8-sig")
    st.download_button("📥 Download CSV", csv, file_name="aspects_results.csv")

    # 🔮 패턴 분석 단계
    from detect_patterns import detect_patterns
    from pattern_keywords import PATTERN_KEYWORDS

    patterns = detect_patterns(df_results)

    major_results = {}
    minor_results = {}

    for name, combos in patterns.items():
        if not combos:
            continue
        meta = PATTERN_KEYWORDS.get(name, {})
        category = meta.get("category", "Minor")
        keyword = meta.get("keyword", "")

        if category == "Major":
            major_results[name] = (keyword, combos)
        else:
            minor_results[name] = (keyword, combos)

    st.divider()

    # 🌟 Major Patterns
    st.subheader("🌟 Major Patterns")
    if not major_results:
        st.info("No major patterns detected.")
    else:
        for name, (kw, combos) in major_results.items():
            st.markdown(f"**{name}** — {kw}")
            for c in combos:
                st.write(" • ", " – ".join(c))
            st.markdown("---")

    # ✴️ Minor Patterns
    st.subheader("✴️ Minor Patterns")
    if not minor_results:
        st.info("No minor patterns detected.")
    else:
        for name, (kw, combos) in minor_results.items():
            st.markdown(f"**{name}** — {kw}")
            for c in combos:
                st.write(" • ", " – ".join(c))
            st.markdown("---")
