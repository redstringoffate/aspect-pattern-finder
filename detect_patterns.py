import itertools
import pandas as pd

# 🧩 공통 헬퍼 함수
def _has_aspect(df, a, b, targets):
    """두 점 사이에 특정 aspect(또는 여러 개)가 있는지 검사"""
    mask = (
        ((df['From'] == a) & (df['To'] == b)) |
        ((df['From'] == b) & (df['To'] == a))
    )
    if isinstance(targets, str):
        targets = [targets]
    return any(df.loc[mask, 'Aspect'].isin(targets))


# 🌟 Major Patterns -------------------------------------------------------

def detect_grand_trine(df):
    """Grand Trine — 세 행성이 모두 Trine 관계"""
    found = []
    labels = list(set(df['From']).union(df['To']))
    for a, b, c in itertools.combinations(labels, 3):
        if all(_has_aspect(df, *pair, 'Trine') for pair in [(a,b), (a,c), (b,c)]):
            found.append((a, b, c))
    return found


def detect_yod(df):
    """Yod — 60° + 150° + 150°"""
    found = []
    labels = list(set(df['From']).union(df['To']))
    for a, b, c in itertools.combinations(labels, 3):
        if (
            _has_aspect(df, a, b, 'Sextile') and
            _has_aspect(df, a, c, 'Quincunx') and
            _has_aspect(df, b, c, 'Quincunx')
        ):
            found.append((a, b, c))
    return found


def detect_thors_hammer(df):
    """Thor’s Hammer — Square + Sesquiquadrate + Sesquiquadrate"""
    found = []
    labels = list(set(df['From']).union(df['To']))
    for a, b, c in itertools.combinations(labels, 3):
        if (
            _has_aspect(df, a, b, 'Square') and
            _has_aspect(df, a, c, 'Sesquiquadrate') and
            _has_aspect(df, b, c, 'Sesquiquadrate')
        ):
            found.append((a, b, c))
    return found


def detect_mystic_rectangle(df):
    """Mystic Rectangle — 2 Opposition + 2 Sextile + 2 Trine"""
    found = []
    labels = list(set(df['From']).union(df['To']))
    for quad in itertools.combinations(labels, 4):
        opps = trines = sexts = 0
        for x, y in itertools.combinations(quad, 2):
            if _has_aspect(df, x, y, 'Opposition'):
                opps += 1
            elif _has_aspect(df, x, y, 'Trine'):
                trines += 1
            elif _has_aspect(df, x, y, 'Sextile'):
                sexts += 1
        if opps == 2 and trines == 2 and sexts == 2:
            found.append(quad)
    return found


def detect_kite(df):
    """Kite — Grand Trine + Opposition"""
    found = []
    gtrines = detect_grand_trine(df)
    labels = list(set(df['From']).union(df['To']))
    for tri in gtrines:
        for d in labels:
            if d in tri: 
                continue
            if any(_has_aspect(df, d, x, 'Opposition') for x in tri):
                found.append((*tri, d))
    return found


def detect_grand_cross(df):
    """Grand Cross — 네 행성이 모두 90° 또는 180° 관계"""
    found = []
    labels = list(set(df['From']).union(df['To']))
    for quad in itertools.combinations(labels, 4):
        count = 0
        for x, y in itertools.combinations(quad, 2):
            if _has_aspect(df, x, y, ['Square', 'Opposition']):
                count += 1
        if count >= 6:
            found.append(quad)
    return found


# ✴️ Minor Patterns -------------------------------------------------------

def detect_golden_yod(df):
    """Golden Yod — 72°, 144°, 120°"""
    found = []
    labels = list(set(df['From']).union(df['To']))
    for a, b, c in itertools.combinations(labels, 3):
        if (
            _has_aspect(df, a, b, 'Quintile') and
            _has_aspect(df, a, c, 'Bi-quintile') and
            _has_aspect(df, b, c, 'Trine')
        ):
            found.append((a, b, c))
    return found


def detect_boomerang(df):
    """Boomerang — Yod + Apex Opposition"""
    found = []
    yods = detect_yod(df)
    labels = list(set(df['From']).union(df['To']))
    for a, b, c in yods:
        for d in labels:
            if d in (a,b,c): 
                continue
            if any(_has_aspect(df, d, x, 'Opposition') for x in (a,b,c)):
                found.append((a,b,c,d))
    return found


def detect_cradle(df):
    """Cradle — Trine + Sextile + Sextile + Opposition"""
    found = []
    labels = list(set(df['From']).union(df['To']))
    for quad in itertools.combinations(labels, 4):
        trines = sexts = opps = 0
        for x, y in itertools.combinations(quad, 2):
            if _has_aspect(df, x, y, 'Trine'): trines += 1
            if _has_aspect(df, x, y, 'Sextile'): sexts += 1
            if _has_aspect(df, x, y, 'Opposition'): opps += 1
        if trines == 1 and sexts == 2 and opps == 1:
            found.append(quad)
    return found


def detect_grand_sextile(df):
    """Grand Sextile — 6행성이 60°, 120° 구조 (육각형)"""
    found = []
    labels = list(set(df['From']).union(df['To']))
    for combo in itertools.combinations(labels, 6):
        ok = 0
        for x, y in itertools.combinations(combo, 2):
            if _has_aspect(df, x, y, ['Sextile', 'Trine']):
                ok += 1
        # 6행성 완전 조화 구조는 조합 중 많은 Trine/Sextile 관계로 판단
        if ok >= 12:
            found.append(combo)
    return found


def detect_minor_grand_trine(df):
    """Minor Grand Trine — 120° + 60° + 60°"""
    found = []
    labels = list(set(df['From']).union(df['To']))
    for a, b, c in itertools.combinations(labels, 3):
        if (
            _has_aspect(df, a, b, 'Trine') and
            _has_aspect(df, a, c, 'Sextile') and
            _has_aspect(df, b, c, 'Sextile')
        ):
            found.append((a, b, c))
    return found


def detect_wedge(df):
    """Wedge — Opposition + Sextile ×2"""
    found = []
    labels = list(set(df['From']).union(df['To']))
    for a, b, c in itertools.combinations(labels, 3):
        if (
            _has_aspect(df, a, b, 'Opposition') and
            _has_aspect(df, a, c, 'Sextile') and
            _has_aspect(df, b, c, 'Sextile')
        ):
            found.append((a, b, c))
    return found


# 🪄 통합 호출 함수 -------------------------------------------------------

def detect_patterns(df):
    """모든 도형 탐지 후 딕셔너리로 반환"""
    return {
        # Major
        "Grand Trine": detect_grand_trine(df),
        "Yod": detect_yod(df),
        "Thor's Hammer": detect_thors_hammer(df),
        "Mystic Rectangle": detect_mystic_rectangle(df),
        "Kite": detect_kite(df),
        "Grand Cross": detect_grand_cross(df),

        # Minor
        "Golden Yod": detect_golden_yod(df),
        "Boomerang": detect_boomerang(df),
        "Cradle": detect_cradle(df),
        "Grand Sextile": detect_grand_sextile(df),
        "Minor Grand Trine": detect_minor_grand_trine(df),
        "Wedge": detect_wedge(df),
    }
