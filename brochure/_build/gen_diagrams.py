"""Generate the two brochure SVGs: ontology-relations.svg and assembly-arch.svg.

Run: python3 brochure/_build/gen_diagrams.py
AWS icons are embedded as data URIs (official Architecture Service Icons 07/31/2025).
"""
from __future__ import annotations

import base64
import math
import os
from pathlib import Path

OUT = Path(__file__).resolve().parents[1]
ICON_DIR = Path(os.environ.get(
    "AWS_ICON_DIR",
    Path.home() / ".claude/plugins/cache/oh-my-cloud-skills/aws-content-plugin/3.0.4"
    "/skills/reactive-presentation/icons/Architecture-Service-Icons_07312025",
))

# ── tokens (match brochure/index.html :root) ────────────────────────────────
PAPER, SURFACE, SUNKEN = "#FAF9F5", "#FFFFFF", "#F3F1EB"
INK, INK2, INK3 = "#1F1E1D", "#5F5A4D", "#6B665A"
LINE, LINE2 = "#E4E0D6", "#CFCABD"
ACCENT, ACCENT_INK, ACCENT_50 = "#1F5F8B", "#17476A", "#EAF1F7"   # real / ontology
EXT, EXT_50 = "#B7791F", "#FBF3E4"                                # external
SYN, SYN_50 = "#8A8474", "#F1EFE9"                                # synthetic
DERIVE = "#C2410C"                                                # derived edge
SANS = "Pretendard,'Apple SD Gothic Neo','Malgun Gothic','Noto Sans KR','Noto Sans CJK KR',sans-serif"
MONO = "'JetBrains Mono',ui-monospace,SFMono-Regular,Menlo,Consolas,'Apple SD Gothic Neo','Malgun Gothic','Noto Sans Mono CJK KR','Noto Sans CJK KR',monospace"


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def text(x, y, s, size=14, weight=400, fill=INK, anchor="start", family=SANS, extra=""):
    return (f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" '
            f'font-weight="{weight}" fill="{fill}" text-anchor="{anchor}" {extra}>{esc(s)}</text>')


def rect(x, y, w, h, fill=SURFACE, stroke=LINE, rx=12, sw=1, extra=""):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{sw}" {extra}/>')


def icon(name: str, x, y, size=44):
    hits = list(ICON_DIR.glob(f"**/48/Arch_{name}_48.svg"))
    if not hits:
        raise FileNotFoundError(name)
    data = base64.b64encode(hits[0].read_bytes()).decode()
    return (f'<image x="{x}" y="{y}" width="{size}" height="{size}" '
            f'href="data:image/svg+xml;base64,{data}"/>')


def defs():
    return f"""<defs>
  <marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
    <path d="M0,0 L10,5 L0,10 z" fill="{INK2}"/></marker>
  <marker id="arrA" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
    <path d="M0,0 L10,5 L0,10 z" fill="{ACCENT}"/></marker>
  <marker id="arrD" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
    <path d="M0,0 L10,5 L0,10 z" fill="{DERIVE}"/></marker>
</defs>"""


def label_pill(x, y, s, color=INK2, size=13, bg=PAPER):
    w = len(s) * size * 0.62 + 12
    return (rect(x - w / 2, y - size + 1, w, size + 7, fill=bg, stroke="none", rx=4)
            + text(x, y + 2, s, size=size, weight=600, fill=color, anchor="middle", family=MONO))


def edge(x1, y1, x2, y2, lab, color=INK2, marker="arr", dash="", r1=0, r2=0, lab_t=0.5, curve=0):
    """Straight/curved edge between node circles of radius r1/r2, with a label pill."""
    dx, dy = x2 - x1, y2 - y1
    d = math.hypot(dx, dy)
    ux, uy = dx / d, dy / d
    sx, sy = x1 + ux * r1, y1 + uy * r1
    ex, ey = x2 - ux * (r2 + 3), y2 - uy * (r2 + 3)
    da = f'stroke-dasharray="{dash}"' if dash else ""
    mk = f'marker-end="url(#{marker})"' if marker else ""
    if curve:
        mx, my = (sx + ex) / 2 - uy * curve, (sy + ey) / 2 + ux * curve
        path = f'<path d="M{sx:.1f},{sy:.1f} Q{mx:.1f},{my:.1f} {ex:.1f},{ey:.1f}" fill="none" stroke="{color}" stroke-width="2" {da} {mk}/>'
        lx, ly = 0.25 * sx + 0.5 * mx + 0.25 * ex, 0.25 * sy + 0.5 * my + 0.25 * ey
    else:
        path = f'<line x1="{sx:.1f}" y1="{sy:.1f}" x2="{ex:.1f}" y2="{ey:.1f}" stroke="{color}" stroke-width="2" {da} {mk}/>'
        lx, ly = sx + (ex - sx) * lab_t, sy + (ey - sy) * lab_t
    return path + label_pill(lx, ly, lab, color=color)


def node(x, y, cls, name, r=30, color=ACCENT, fill=ACCENT_50, below=True, size=13):
    ly = y + r + 18 if below else y - r - 10
    return (f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="{color}" stroke-width="2.2"/>'
            + text(x, y + 5, cls, size=size, weight=700, fill=color, anchor="middle")
            + text(x, ly, name, size=12, fill=INK2, anchor="middle"))


def graph_panel() -> list[str]:
    """Column-3 knowledge-graph panel (also reused as the hero figure)."""
    o: list[str] = []
    o.append(rect(1010, 100, 400, 568, fill=SURFACE, stroke=LINE))
    P = (1210, 172)     # Party
    A = (1092, 330)     # Person A
    B = (1330, 330)     # Person B
    BL = (1210, 520)    # Bill
    C = (1070, 610)     # Committee
    o.append(edge(*A, *P, "BELONGS_TO", r1=30, r2=30, lab_t=.5))
    o.append(edge(*B, *P, "BELONGS_TO", r1=30, r2=30, lab_t=.5))
    o.append(edge(*A, *B, "CO_PROPOSED_WITH", color=DERIVE, marker="arrD", dash="7 5", r1=30, r2=30))
    o.append(edge(*A, *BL, "PROPOSED", r1=30, r2=30, lab_t=.42))
    o.append(edge(*B, *BL, "CO_PROPOSED", r1=30, r2=30, lab_t=.36))
    o.append(edge(*B, *BL, "VOTED", r1=30, r2=30, curve=-58, color=ACCENT, marker="arrA"))
    o.append(edge(*A, *C, "MEMBER_OF", r1=30, r2=26, lab_t=.55, curve=40))
    o.append(edge(*BL, *C, "ASSIGNED_TO", r1=30, r2=26, lab_t=.5))
    o.append(node(*P, "Party", "정당", below=False))
    o.append(node(*A, "Person", "의원 A", below=False))
    o.append(node(*B, "Person", "의원 B", below=False))
    o.append(node(*BL, "Bill", "의안", below=True))
    o.append(node(*C, "Cmte", "위원회", r=26, below=True, size=12))
    o.append(text(1395, 652, "VOTED {value: yes|no|abstain|absent}", size=11.5, fill=ACCENT_INK, anchor="end", family=MONO))
    return o


# ════════════════════════════════════════════════════════════════════════════
# 1) ontology-relations.svg — "OpenAPI field → mapping rule → edge"
# ════════════════════════════════════════════════════════════════════════════
def ontology_svg() -> str:
    W, H = 1440, 820
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
         f'role="img" aria-labelledby="t d">',
         '<title id="t">국회 OpenAPI 필드가 지식그래프 관계가 되는 과정</title>',
         '<desc id="d">왼쪽 국회 OpenAPI 원천 필드, 가운데 8개 매핑 규칙, 오른쪽 Neptune 지식그래프의 '
         '7개 real 엣지 타입과 31 클래스 7 그룹.</desc>', defs(),
         rect(0, 0, W, H, fill=PAPER, stroke="none", rx=0)]

    # column headers
    for x, n, t, sub in [(40, "①", "원천 필드", "국회 열린데이터광장 OpenAPI"),
                         (480, "②", "매핑 규칙", "data/real/* 어댑터 → 적재"),
                         (1010, "③", "지식그래프", "Amazon Neptune · openCypher")]:
        o.append(text(x, 52, f"{n} {t}", size=22, weight=800))
        o.append(text(x, 76, sub, size=13, fill=INK3, family=MONO))

    # ── column 1: API cards with field rows; remember anchor y per field
    anchors: dict[str, tuple[float, float]] = {}
    cards = [
        ("member", "국회의원 정보", 100,
         [("MONA_CD", "의원 코드 · 조인 키", True), ("HG_NM", "이름", False),
          ("POLY_NM", "소속 정당", False), ("CMIT_NM", "소속 위원회", False)]),
        ("bill", "의원 발의법률안", 306,
         [("BILL_ID", "의안 ID · 조인 키", True), ("RST_MONA_CD", "대표발의자", False),
          ("PUBL_MONA_CD", "공동발의자 'A,B,C…'", False), ("COMMITTEE", "소관 위원회", False)]),
        ("vote", "본회의 표결정보 (의원 × 의안)", 512,
         [("BILL_ID", "의안 ID", True), ("MONA_CD", "의원 코드", True),
          ("(표결값)", "yes·no·abstain·absent", False)]),
    ]
    cx, cw = 40, 380
    for key, title, y, fields in cards:
        h = 52 + len(fields) * 34 + 10
        o.append(rect(cx, y, cw, h, extra='filter="none"'))
        o.append(f'<rect x="{cx}" y="{y}" width="6" height="{h}" rx="3" fill="{ACCENT}"/>')
        o.append(text(cx + 22, y + 32, title, size=16, weight=700))
        for i, (f, desc, is_key) in enumerate(fields):
            fy = y + 66 + i * 34
            o.append(rect(cx + 18, fy - 19, 170, 26, fill=ACCENT_50 if is_key else SUNKEN, stroke="none", rx=6))
            o.append(text(cx + 28, fy - 1, f, size=14, weight=700,
                          fill=ACCENT_INK if is_key else INK, family=MONO))
            o.append(text(cx + 200, fy - 1, desc, size=14, fill=INK2))
            anchors[f"{key}.{f}"] = (cx + cw, fy - 6)
            if f != "HG_NM":
                o.append(f'<circle cx="{cx + cw}" cy="{fy - 6}" r="4" fill="{ACCENT}"/>')

    # ── column 2: rules
    rules = [
        ("KEY", "MONA_CD · BILL_ID → 노드 키", "MERGE (:Person {assembly_id}) / (:Bill {bill_id})", ACCENT),
        ("DIRECT", "POLY_NM → BELONGS_TO", "Person → Party", ACCENT),
        ("DIRECT", "CMIT_NM → MEMBER_OF", "Person → Committee", ACCENT),
        ("LEAD", "RST_MONA_CD → PROPOSED", "대표발의자 Person → Bill", ACCENT),
        ("SPLIT", "PUBL_MONA_CD.split(',') → CO_PROPOSED", "공동발의자 N명 → N개 엣지", ACCENT),
        ("DIRECT", "COMMITTEE → ASSIGNED_TO", "Bill → Committee", ACCENT),
        ("JOIN", "(BILL_ID, MONA_CD) → VOTED {value}", "표결 row를 의원·의안에 조인", ACCENT),
        ("DERIVE", "같은 의안 발의자 쌍 → CO_PROPOSED_WITH", "대표+공동발의자 쌍마다 {count} 누적 · Person ↔ Person", DERIVE),
    ]
    rx0, rw, rh, ry0, rstep = 480, 470, 58, 100, 68
    rule_y = []
    for i, (tag, main, sub, col) in enumerate(rules):
        y = ry0 + i * rstep
        rule_y.append(y + rh / 2)
        derived = tag == "DERIVE"
        o.append(rect(rx0, y, rw, rh, fill="#FFF4EC" if derived else SURFACE,
                      stroke=DERIVE if derived else LINE2, rx=10,
                      extra='stroke-dasharray="6 4"' if derived else ""))
        tw = len(tag) * 9 + 16
        o.append(rect(rx0 + 12, y + 10, tw, 20, fill=col, stroke="none", rx=5))
        o.append(text(rx0 + 12 + tw / 2, y + 25, tag, size=13, weight=700, fill="#fff",
                      anchor="middle", family=MONO))
        o.append(text(rx0 + 20 + tw, y + 25, main, size=14.5, weight=700, family=MONO,
                      fill=DERIVE if derived else INK))
        o.append(text(rx0 + 14, y + 48, sub, size=13.5, fill=INK2))

    def link(a, ri, color=ACCENT, dash=""):
        x1, y1 = anchors[a]
        x2, y2 = rx0, rule_y[ri]
        da = f'stroke-dasharray="{dash}"' if dash else ""
        o.append(f'<path d="M{x1},{y1} C{x1 + 34},{y1} {x2 - 34},{y2} {x2 - 2},{y2}" fill="none" '
                 f'stroke="{color}" stroke-width="1.6" opacity=".75" {da}/>')

    link("member.MONA_CD", 0); link("bill.BILL_ID", 0)
    link("member.POLY_NM", 1); link("member.CMIT_NM", 2)
    link("bill.RST_MONA_CD", 3); link("bill.PUBL_MONA_CD", 4)
    link("bill.COMMITTEE", 5)
    link("vote.BILL_ID", 6); link("vote.MONA_CD", 6); link("vote.(표결값)", 6)
    link("bill.RST_MONA_CD", 7, color=DERIVE, dash="5 4"); link("bill.PUBL_MONA_CD", 7, color=DERIVE, dash="5 4")

    # rule → graph connector arrow
    o.append(f'<line x1="{rx0 + rw + 8}" y1="370" x2="1000" y2="370" stroke="{INK2}" stroke-width="2" marker-end="url(#arr)"/>')
    o.append(text((rx0 + rw + 1000) / 2, 360, "load", size=12, fill=INK3, anchor="middle", family=MONO))

    o.extend(graph_panel())

    # counts box
    by = 690
    o.append(rect(1010, by, 400, 104, fill=ACCENT_50, stroke="none"))
    o.append(text(1030, by + 32, "74,249", size=28, weight=800, fill=ACCENT_INK, family=MONO))
    o.append(text(1160, by + 31, "real edges · 7 types", size=14, weight=600, fill=ACCENT_INK))
    o.append(text(1030, by + 60, "VOTED 28,528 · CO_PROPOSED_WITH 19,191", size=12.5, fill=INK2, family=MONO))
    o.append(text(1030, by + 84, "Person 286 · Bill 2,098  (22대 국회)", size=12.5, fill=INK2, family=MONO))

    # legend (left/middle bottom of upper zone)
    ly = 690
    o.append(rect(40, ly, 910, 104, fill=SURFACE, stroke=LINE))
    o.append(text(60, ly + 30, "읽는 법", size=14, weight=800))
    o.append(f'<line x1="60" y1="{ly + 58}" x2="104" y2="{ly + 58}" stroke="{INK2}" stroke-width="2" marker-end="url(#arr)"/>')
    o.append(text(114, ly + 63, "원천 필드에서 직접 생성된 엣지", size=13, fill=INK2))
    o.append(f'<line x1="360" y1="{ly + 58}" x2="404" y2="{ly + 58}" stroke="{DERIVE}" stroke-width="2" stroke-dasharray="7 5" marker-end="url(#arrD)"/>')
    o.append(text(414, ly + 63, "다른 엣지에서 계산된 파생 엣지", size=13, fill=INK2))
    o.append(rect(650, ly + 46, 60, 22, fill=ACCENT_50, stroke="none", rx=6))
    o.append(text(680, ly + 62, "KEY", size=12, weight=700, fill=ACCENT_INK, anchor="middle", family=MONO))
    o.append(text(720, ly + 63, "API 간 조인 키 (MONA_CD)", size=13, fill=INK2))
    o.append(text(60, ly + 90, "같은 MONA_CD가 의원·발의·표결 API를 하나의 Person 노드로 묶는다 — 이것이 관계 형성의 출발점.",
                  size=13, weight=600, fill=ACCENT_INK))

    o.append("</svg>")
    return "\n".join(o)


# ════════════════════════════════════════════════════════════════════════════
# 2) assembly-arch.svg — AWS architecture with the ontology layer at its core
# ════════════════════════════════════════════════════════════════════════════
def svc(x, y, name, title, sub, w=190, sub2=""):
    """Icon card: icon left, two/three text lines right."""
    h = 74 if not sub2 else 90
    s = [rect(x, y, w, h, fill=SURFACE, stroke=LINE2, rx=10), icon(name, x + 12, y + 15, 44),
         text(x + 66, y + 30, title, size=15, weight=700),
         text(x + 66, y + 51, sub, size=13, fill=INK2)]
    if sub2:
        s.append(text(x + 66, y + 70, sub2, size=13, fill=INK2))
    return "".join(s)


def arrow(pts, color=INK2, marker="arr", dash="", sw=2):
    d = "M" + " L".join(f"{x},{y}" for x, y in pts)
    da = f'stroke-dasharray="{dash}"' if dash else ""
    return f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{sw}" {da} marker-end="url(#{marker})"/>'


def arch_svg() -> str:
    W, H = 1440, 860
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
         f'role="img" aria-labelledby="t d">',
         '<title id="t">ontology-for-assembly AWS 아키텍처</title>',
         '<desc id="d">사용자 → CloudFront → VPC origin → internal ALB → ECS Fargate(web, api). api는 Neptune 온톨로지 계층에 '
         'openCypher로 질의하고 OpenSearch Serverless, Bedrock(모델·Guardrails), DynamoDB를 사용한다. '
         '국회 OpenAPI 데이터는 one-shot 로더가 S3를 거쳐 Neptune과 OpenSearch에 적재한다.</desc>', defs(),
         rect(0, 0, W, H, fill=PAPER, stroke="none", rx=0)]

    # users (outside cloud)
    o.append(rect(20, 250, 160, 250, fill=SURFACE, stroke=LINE2))
    o.append(text(100, 280, "6 페르소나", size=15, weight=800, anchor="middle"))
    for i, p in enumerate(["편집국", "데이터·AI", "광고·세일즈", "일반 독자", "유료 구독자", "기업/B2B"]):
        o.append(rect(36, 296 + i * 32, 128, 24, fill=SUNKEN, stroke="none", rx=6))
        o.append(text(100, 313 + i * 32, p, size=12.5, fill=INK2, anchor="middle"))
    # external data sources
    o.append(rect(20, 640, 160, 170, fill=EXT_50, stroke=EXT, rx=12, extra='stroke-dasharray="5 4"'))
    o.append(text(100, 668, "외부 원천", size=14, weight=800, anchor="middle", fill="#7A4F0F"))
    for i, s in enumerate(["국회 열린데이터광장", "OpenAPI", "네이버 뉴스 API", "+ 합성 generator"]):
        o.append(text(100, 698 + i * 26, s, size=12.5, fill=INK2, anchor="middle"))

    # AWS cloud boundary
    o.append(rect(210, 24, 1214, 822, fill="none", stroke=INK3, rx=16, sw=1.4))
    o.append(text(232, 52, "AWS Cloud", size=14, weight=800, fill=INK2))

    # edge: CloudFront + Cognito
    o.append(svc(232, 340, "Amazon-CloudFront", "CloudFront", "웹·API 진입점", w=170))
    o.append(svc(232, 120, "Amazon-Cognito", "Cognito", "User Pool × 2", w=170, sub2="+ Guest Identity"))
    o.append(arrow([(180, 377), (228, 377)]))

    # managed band
    o.append(rect(440, 80, 970, 150, fill=SUNKEN, stroke="none", rx=12))
    o.append(text(458, 104, "Managed AI · Search (서비스 엔드포인트)", size=12.5, weight=700, fill=INK3))
    o.append(svc(458, 120, "Amazon-Bedrock", "Bedrock", "Claude Sonnet 4.6", w=212, sub2="Cohere embed-v4"))
    o.append(svc(686, 120, "Amazon-Bedrock", "Guardrails", "정치 중립성 정책", w=180, sub2="입력·출력 필터"))
    o.append(svc(882, 120, "Amazon-DynamoDB", "DynamoDB ×4", "B2B 키 · 광고 인벤토리", w=212, sub2="노출 · 독자 프로필"))
    o.append(svc(1110, 120, "Amazon-OpenSearch-Service", "OpenSearch", "Serverless · Nori BM25", w=284, sub2="+ KNN 1024d · hybrid query"))

    # VPC
    o.append(rect(440, 262, 970, 372, fill="none", stroke=ACCENT, rx=14, sw=1.6, extra='stroke-dasharray="8 5"'))
    o.append(text(458, 286, "VPC · private / isolated subnets · 2 AZ", size=12.5, weight=700, fill=ACCENT_INK))
    o.append(svc(458, 340, "Elastic-Load-Balancing", "ALB (internal)", "path routing", w=176))
    o.append(arrow([(402, 377), (454, 377)], color=ACCENT, marker="arrA"))
    o.append(label_pill(428, 326, "VPC origin", color=ACCENT_INK, size=12.5))
    o.append(svc(670, 296, "AWS-Fargate", "web · Next.js 14", "ARM64 × 2", w=196))
    o.append(svc(670, 440, "AWS-Fargate", "api · FastAPI", "ARM64 × 2", w=196))
    o.append(arrow([(634, 365), (666, 333)]))
    o.append(label_pill(640, 335, "/*", size=12.5))
    o.append(arrow([(634, 390), (666, 470)]))
    o.append(label_pill(642, 445, "/api/*", size=12.5))
    o.append(svc(670, 548, "AWS-Lambda", "Ad Matcher", "광고 매칭 Lambda", w=196))
    # api → managed bus
    o.append(f'<path d="M866,456 L896,456 L896,244 L1200,244" fill="none" stroke="{INK2}" stroke-width="2"/>')
    for bx in (564, 776, 988):
        o.append(arrow([(bx, 244), (bx, 214)]))
    o.append(f'<path d="M564,244 L896,244" fill="none" stroke="{INK2}" stroke-width="2"/>')
    o.append(arrow([(1200, 244), (1200, 214)]))
    o.append(label_pill(680, 244, "HTTPS · SigV4", size=12.5))

    # ontology layer (Neptune)
    ox, oy, ow, oh = 930, 296, 464, 322
    o.append(rect(ox, oy, ow, oh, fill=ACCENT_50, stroke=ACCENT, rx=14, sw=2))
    o.append(icon("Amazon-Neptune", ox + 14, oy + 14, 44))
    o.append(text(ox + 68, oy + 34, "Ontology layer · Amazon Neptune", size=15, weight=800, fill=ACCENT_INK))
    o.append(text(ox + 68, oy + 54, "31 클래스 · 7 real edge types · 74,249 edges", size=12, fill=ACCENT_INK, family=MONO))
    o.append(arrow([(866, 490), (926, 490)], color=ACCENT, marker="arrA"))
    o.append(label_pill(896, 510, "openCypher", color=ACCENT_INK, size=12.5))
    # mini graph
    gP, gA, gB, gBL, gC = (ox + 232, oy + 104), (ox + 96, oy + 186), (ox + 368, oy + 186), (ox + 232, oy + 278), (ox + 72, oy + 278)
    o.append(edge(*gA, *gP, "BELONGS_TO", r1=26, r2=26))
    o.append(edge(*gB, *gP, "BELONGS_TO", r1=26, r2=26))
    o.append(edge(*gA, *gB, "CO_PROPOSED_WITH", color=DERIVE, marker="arrD", dash="6 4", r1=26, r2=26))
    o.append(edge(*gA, *gBL, "PROPOSED", r1=26, r2=26, lab_t=.62))
    o.append(edge(*gB, *gBL, "VOTED", r1=26, r2=26, color=ACCENT, marker="arrA", lab_t=.45))
    o.append(edge(*gA, *gC, "MEMBER_OF", r1=26, r2=26, lab_t=.5))
    o.append(edge(*gBL, *gC, "ASSIGNED_TO", r1=26, r2=26, lab_t=.5))
    for (x, y), c in [(gP, "Party"), (gA, "Person"), (gB, "Person"), (gBL, "Bill"), (gC, "Cmte")]:
        o.append(f'<circle cx="{x}" cy="{y}" r="26" fill="{SURFACE}" stroke="{ACCENT}" stroke-width="2"/>')
        o.append(text(x, y + 4.5, c, size=12.5, weight=700, fill=ACCENT_INK, anchor="middle"))
    # OpenSearch ↔ Neptune domain-key link
    o.append(f'<path d="M1330,214 L1330,292" fill="none" stroke="{ACCENT}" stroke-width="1.8" stroke-dasharray="4 4"/>')
    o.append(label_pill(1330, 240, "assembly_id · bill_id", color=ACCENT_INK, size=12))

    # ingestion lane
    o.append(rect(232, 660, 1178, 170, fill=SURFACE, stroke=LINE, rx=12))
    o.append(text(250, 686, "적재 파이프라인 (one-shot)", size=13, weight=800, fill=INK2))
    o.append(arrow([(180, 740), (246, 740)], color=EXT))
    o.append(svc(250, 700, "Amazon-Elastic-Container-Service", "ECS one-shot task", "python -m data.load", w=230, sub2="data/real/* 어댑터"))
    o.append(arrow([(480, 745), (526, 745)]))
    o.append(svc(530, 708, "Amazon-Simple-Storage-Service", "S3", "클래스별 NDJSON", w=176))
    o.append(arrow([(706, 745), (752, 745)]))
    o.append(rect(756, 700, 330, 90, fill=SUNKEN, stroke="none", rx=10))
    o.append(text(772, 726, "UNWIND $items MERGE (n:Label {key})", size=12, weight=700, family=MONO, fill=ACCENT_INK))
    o.append(text(772, 748, "→ Neptune 노드 · 7 real edge 타입", size=12, fill=INK2))
    o.append(text(772, 770, "→ OpenSearch 기사 + 벡터 인덱스", size=12, fill=INK2))
    o.append(arrow([(1086, 745), (1162, 745), (1162, 622)], color=ACCENT, marker="arrA"))
    o.append(svc(1190, 708, "Amazon-CloudWatch", "CloudWatch", "대시보드 · 알람", w=204))
    o.append("</svg>")
    return "\n".join(o)


def hero_svg() -> str:
    """Illustrative CO_PROPOSED_WITH network (anonymous, deterministic) for the hero."""
    import random
    rnd = random.Random(22)
    W, H = 520, 520
    centers = [(160, 170), (370, 190), (260, 390)]
    # one hue only — clusters must not read as party colours
    fills = [ACCENT_50, "#DCE8F2", "#F4F8FB"]
    strokes = [ACCENT, "#4F86AD", "#7FA6C4"]
    nodes = []
    for gi, (cx, cy) in enumerate(centers):
        for k in range(7):
            ang = k / 7 * 2 * math.pi + rnd.uniform(-.25, .25)
            rad = 52 + rnd.uniform(0, 46)
            nodes.append((cx + rad * math.cos(ang), cy + rad * math.sin(ang), gi))
    edges = []
    for i in range(len(nodes)):
        for j in range(i + 1, len(nodes)):
            same = nodes[i][2] == nodes[j][2]
            if rnd.random() < (0.42 if same else 0.05):
                edges.append((i, j, rnd.randint(1, 9) if same else rnd.randint(1, 3), same))
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 56 {W} {H - 56}" width="{W}" height="{H - 56}" '
         'role="img" aria-labelledby="ht"><title id="ht">공동발의 네트워크 개념도 (예시)</title>',
         rect(0, 0, W, H, fill=SURFACE, stroke="none", rx=0)]
    for i, j, w, same in edges:
        (x1, y1, _), (x2, y2, _) = nodes[i], nodes[j]
        col = INK3 if same else DERIVE
        da = "" if same else 'stroke-dasharray="5 4"'
        o.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{col}" '
                 f'stroke-width="{0.8 + w * 0.45:.2f}" opacity="{0.35 + w * 0.05:.2f}" {da}/>')
    deg = [0] * len(nodes)
    for i, j, w, _ in edges:
        deg[i] += w; deg[j] += w
    for (x, y, g), d in zip(nodes, deg):
        r = 7 + d * 0.45
        o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{fills[g]}" stroke="{strokes[g]}" stroke-width="2"/>')
    o.append(text(20, 494, "CO_PROPOSED_WITH {count}", size=15, weight=700, fill=DERIVE, family=MONO))
    o.append(text(W - 20, 494, "예시 · 익명", size=14, fill=INK3, anchor="end"))
    o.append("</svg>")
    return "\n".join(o)


if __name__ == "__main__":
    (OUT / "ontology-relations.svg").write_text(ontology_svg(), encoding="utf-8")
    (OUT / "assembly-arch.svg").write_text(arch_svg(), encoding="utf-8")
    (OUT / "hero-graph.svg").write_text(hero_svg(), encoding="utf-8")
    print("wrote 3 SVGs to", OUT)
