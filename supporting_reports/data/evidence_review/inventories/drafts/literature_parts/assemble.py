import re, os
D = os.path.dirname(os.path.abspath(__file__))
S = os.path.dirname(os.path.dirname(os.path.dirname(D)))  # scratchpad
R = lambda f: open(f if os.path.isabs(f) else os.path.join(D, f)).read()

def chunks(text):
    return re.split(r'(?m)^(?=#{1,3} )', text)

def ids_of(sec):
    head = sec.split('\n- **Method', 1)[0]
    m = re.search(r'arXiv:\s*([A-Za-z\-]+/\d{7}|\d{4}\.\d{4,5})', head)
    if m: return m.group(1)
    m = re.search(r'DOI:?\s*(10\.\S+?)[;,)\s]', head)
    return m.group(1).lower().rstrip('.') if m else None

def title_of(sec):
    return sec.splitlines()[0].lstrip('#').strip()

def key_of(sec):
    return title_of(sec).split(' — ')[0].strip()

# ---------------- Parts A, B
header = R('00_header.md')
A = R('warp_classic.md').replace('## Part A. Warp-drive design literature, 1994–2012', '# Part A. Warp drives and shortcut corridors, 1994–2012', 1)
B = R('warp_modern.md').replace('## Part B. Warp-drive design literature, 2020–2026', '# Part B. Warp drives, 2020–2026', 1)
AB_ids = {ids_of(c) for c in chunks(A + '\n' + B) if c.startswith('### ')} - {None}

# ---------------- Part C (QI helper)
qi = R('qi_anec_causality.md')
body, _, tail = qi.partition('\n## 1. Synthesis table')
syn_qi, _, rest = ('## 1. Synthesis table' + tail).partition('\n## 2. Open disputes')
disp_qi, _, rest = ('## 2. Open disputes' + rest).partition('\n## 3. UNVERIFIED items')
unv_qi, _, assess = ('## 3. UNVERIFIED items' + rest).partition('\n## 4. Assessment of project claim (g)')
assess = ('## 4. Assessment of project claim (g)' + assess).split('\n## E. Chronology')[0]

c_pointers = {
    'ER97': 'Part A, EverettRoman1997 (QI and network-orientation details merged there)',
    'SS24': 'Part B, ShoshanySnodgrass2024 (lapse identities and chronology details merged there)',
    'SSV22': 'Part B, SSV2022 (NEC monotonicity proof merged there)',
    'Le26': 'Part B, Le2026b (QI threshold and ANEC normalization identity merged there)',
    'JL26': 'Part B, JusufiLobo2026',
    'GZ25': 'Part B, GarattiniZatrimaylov2024_2025',
    'LV04': 'Part A, LoboVisser2004',
    'FR96': 'Part D, FordRoman1996 (field-number scaling and the redshift escape route merged there)',
    'FSW93': 'Part D, FriedmanSchleichWitt1993 (full text read there: the theorem assumes ANEC)',
}
outC = []
for ch in chunks(body):
    m = re.match(r'### (\S+) — ', ch)
    if m and m.group(1) in c_pointers:
        outC.append(f'### {title_of(ch)}\n- See {c_pointers[m.group(1)]}.\n\n'); continue
    outC.append(ch)
C = ''.join(outC)
C = C.replace('# Theorems and constraints that bind superluminal and shortcut designs',
              '# Part C. Quantum inequalities, averaged null energy, superluminal censorship and chronology', 1)
C = re.sub(r'(?m)^## ([A-F])\. ', lambda m: f'## C.{"ABCDEF".index(m.group(1))+1} ', C)
C = C.replace('(ER97, the two-tube time machine, appears in Part A.)\n', '')
C_full_ids = {}
for ch in chunks(C):
    if ch.startswith('### ') and '- See Part' not in ch[:400]:
        i = ids_of(ch)
        if i: C_full_ids[i] = key_of(ch)
assess = assess.replace('## 4. Assessment of project claim (g)', '## C.7 Assessment of project claim (g)')

# ---------------- Part D (two wormhole files)
def split_tail(txt):
    m = re.search(r'(?m)^## [^\n]*(Synthesis)', txt)
    return (txt[:m.start()], txt[m.start():]) if m else (txt, '')
def grab(tail, key):
    mm = re.search(r'(?m)^## [^\n]*' + key + r'[^\n]*\n', tail, re.I)
    if not mm: return ''
    nxt = re.search(r'(?m)^## ', tail[mm.end():])
    return (tail[mm.end(): mm.end() + nxt.start()] if nxt else tail[mm.end():]).strip()

whA = R('wormholes.md')
whB_path = os.path.join(S, 'wh', 'wormholes_agentB.md')
whB = R(whB_path) if os.path.exists(whB_path) else ''
bodyA, tailA = split_tail(whA)
bodyB, tailB = split_tail(whB)

keep_bullet = re.compile(r'(?m)^  - .*(Counterexample|long wormhole|connecting a region to itself).*$', re.I)
seen = set(AB_ids)
outD = []
_chA = chunks(bodyA)
_last = {}
for _k, _c in enumerate(_chA):
    if _c.startswith('### '):
        _i = ids_of(_c)
        if _i: _last[_i] = _k
for _k, ch in enumerate(_chA):
    if ch.startswith('### '):
        _i = ids_of(ch)
        if _i and _last.get(_i) != _k and _i not in C_full_ids:
            continue
    if ch.startswith('# '):
        outD.append('# Part D. Traversable wormholes\n\n' + ch.split('\n', 1)[1] if '\n' in ch else '# Part D. Traversable wormholes\n'); continue
    if ch.startswith('## Part W'):
        outD.append('# Part D. Traversable wormholes\n\n' + (ch.split('\n', 1)[1] if '\n' in ch else '')); continue
    if ch.startswith('## '):
        ch = re.sub(r'^## ([A-Z])\. ', lambda m: f'## D.{ord(m.group(1))-64} ', ch); outD.append(ch); continue
    if ch.startswith('### '):
        i = ids_of(ch)
        if i in C_full_ids:
            if i in seen:
                continue
            extra = '\n'.join(keep_bullet.findall(ch) and [l for l in ch.splitlines() if keep_bullet.match(l)])
            outD.append(f'### {title_of(ch)}\n- See Part C, {C_full_ids[i]}.' + (f' Wormhole-specific point from this cluster\'s reading:\n{extra}\n\n' if extra else '\n\n'))
            seen.add(i); continue
        if i in seen and i is not None:
            continue
        if i: seen.add(i)
        ch = ch.replace('a₀ ≲ 8f⁴(r₀/l_p)^{1/3} l_p (eq. 69)', 'a₀ ≲ (r₀/(8f⁴ l_p))^{1/3} l_p (eq. 69)')
        if key_of(ch) == 'FordRoman1996' and '10⁶² fields' not in ch:
            anchor = '\n- **Method / verification standard:**'
            add = ('\n  - N independent fields relax the bound only as √N; a 1 m throat needs about 10⁶² fields (Conclusions) [derivation].'
                   '\n  - Compliance is possible only with geometries involving "large redshifts (or blueshifts)" or extreme length-scale discrepancies (Conclusions) [claim].')
            ch = ch.replace(anchor, add + anchor, 1)
        outD.append(ch); continue
    outD.append(ch)
extraB = []
for ch in chunks(bodyB):
    if not ch.startswith('### ') or ' — ' not in ch.splitlines()[0]: continue
    i = ids_of(ch)
    if i in C_full_ids or (i is not None and i in seen):
        continue
    if i: seen.add(i)
    extraB.append(ch)
D_text = ''.join(outD).rstrip().replace('## Cross-paper design findings', '## D.13 Cross-paper design findings') + '\n\n'
if extraB:
    D_text += ('## D.14 Further wormhole entries (second reading of the cluster)\n\n'
               'Entries below come from a second, independent verification pass over the same downloaded sources; papers already covered above are omitted.\n\n'
               + ''.join(extraB))

synA, synB = grab(tailA, 'Synthesis'), grab(tailB, 'Synthesis')
dA, dB = grab(tailA, 'disput'), grab(tailB, 'disput')
uA, uB = grab(tailA, 'UNVERIFIED'), grab(tailB, 'UNVERIFIED')

strip_head = lambda s: s.split('\n', 1)[1] if s.startswith('## ') else s
cross = R('crossread_unverified_warp.md')
E = ('# Part E. Synthesis table: knob/part × physics relation × papers × status\n\n'
     'Status vocabulary: identity/theorem, derivation, numerical, claim, conjecture, disputed. The last column of E.1 and the table E.4 compare with the project identities.\n\n'
     + R('synth_warp.md').strip() + '\n\n'
     + '### E.2 Quantum inequalities, ANEC and causality\n\n' + strip_head(syn_qi).strip() + '\n\n'
     + '### E.3 Traversable wormholes\n\n' + synA + ('\n\nAdditional rows from the second reading:\n\n' + synB if synB else '') + '\n\n'
     + cross.split('### G.1')[0].strip() + '\n'
     + ('\n' + R('lapse_only_nec.md').strip() + '\n' if os.path.exists(os.path.join(D, 'lapse_only_nec.md')) else ''))
F = ('# Part F. Open disputes\n\n' + R('disputes_warp.md').strip() + '\n\n'
     + '### F.2 Quantum inequalities, ANEC and causality\n\n' + strip_head(disp_qi).strip() + '\n\n'
     + '### F.3 Traversable wormholes\n\n' + dA + ('\n\nFrom the second reading:\n\n' + dB if dB else '') + '\n')
G = ('# Part G. UNVERIFIED items\n\n### G.1' + cross.split('### G.1', 1)[1].rstrip() + '\n\n'
     + '### G.2 Quantum inequalities, ANEC and causality\n\n' + strip_head(unv_qi).strip() + '\n\n'
     + '### G.3 Traversable wormholes\n\n' + uA + ('\n\nFrom the second reading:\n\n' + uB if uB else '') + '\n')

G = G.rstrip() + ('\n\nFrom the second, independent reading of the wormhole cluster: Hawking 1992 and Kim–Thorne 1991 beyond their abstracts; '
     'OCR-limited prefactors in Morris–Thorne and MTY; the volume and pages of Rubakov\'s Theor. Math. Phys. paper (seen only in a search snippet); '
     'the Azad et al. Phys. Rev. D 109, 124051 (2024) follow-up, known only through a citation in Azad et al. 2025; '
     'the Graham–Olum abstract wording differs between the arXiv abstract page ("sufficient to rule out wormholes and closed timelike curves") '
     'and the pinned v2 PDF ("sufficient to rule out closed timelike curves and wormholes connecting different asymptotically flat regions"); '
     'the PDF wording matches Theorem 1\'s simple-connectedness restriction.\n')
doc = '\n\n'.join(x.strip() for x in [header, A, B, C, assess, D_text, E, F, G]) + '\n'
doc = doc.replace('a₀ ≲ 8f⁴(r₀/l_p)^{1/3} l_p', 'a₀ ≲ (r₀/(8f⁴ l_p))^{1/3} l_p')
_fx = [
 ("  - [derivation] Validity requires ℓ ≪ q³ l_p (Eq. 5.43).",
  "  - [derivation] Validity requires ℓ ≪ q³ l_p (Eq. 5.43); Sec. 5.5 (added in v2, kept in v3) restricts the classical derivation further, after averaging throat fluctuations over a time of order d, to d ≪ q^{5/2} (Eq. 5.49), \"which is smaller than our previous estimate q³ in (5.43)\"."),
 ("validity ℓ ≪ q³ l_p;", "validity ℓ ≪ q³ l_p, tightened to d ≪ q^{5/2} by Sec. 5.5;"),
 ("(b)/(g) Stress-only (lapse-carried) NEC violation with ρ = 0 escapes energy-density QIs. It is caught only by null-contracted bounds. Any QI audit of a lapse-supported rail source therefore has to use T_ab k^a k^b, not ρ.",
  "(b)/(g) Stress-only (lapse-carried) NEC violation with ρ = 0 in the static frame is bounded by the usual energy-density QIs only after boosting to a radially moving geodesic observer (Sec. 6.1, citing Ford–Roman 1996); the null-contracted bound removes the need for the boost. A QI audit of a lapse-supported rail source therefore uses boosted observers or T_ab k^a k^b; the static-frame ρ alone misses it."),
 ("Fewster–Roman 2005 show that such stress-only violation is caught by null-contracted quantum inequalities, not by energy-density ones.",
  "Fewster–Roman 2005 bound such stress-only violation with a null-contracted quantum inequality; the usual energy-density QIs reach it only after a boost to a radially moving geodesic observer (their Sec. 6.1)."),
 ("The jump in the lapse gradient across the shell is thus what sources ϑ.",
  "From eq. (3.7), σ = −κ^θ_θ/4π and ϑ = −(κ^τ_τ + κ^θ_θ)/8π: the lapse-gradient jump κ^τ_τ enters the tension ϑ together with the areal jump, while the surface energy σ contains no lapse term — the thin-shell form of (b), the lapse carrying stress without energy."),
 ("The two are opposite sides of one diagnostic.",
  "The two are opposite sides of one diagnostic [claim: analogy introduced in this inventory; neither paper states it]."),
 ("5. **Rotation as stabiliser.** Second-order slow-rotation results indicate stabilisation of the Ellis–Bronnikov radial mode. Full non-perturbative radial stability and the quadrupole sector are not yet settled.",
  "5. **Rotation as stabiliser.** Second-order slow-rotation results indicate stabilisation of the Ellis–Bronnikov radial mode. Full non-perturbative radial stability and the quadrupole sector are not yet settled. The full text of Azad et al. 2025 (arXiv:2509.22118v1) reports, from a cited 2024 follow-up (Phys. Rev. D 109, 124051; UNVERIFIED here), that J_c decreases with the asymmetry parameter only up to C ≈ 0.5 and grows beyond it, and that a second unstable branch emerges from a zero mode; \"the radial instability is conjectured to disappear.\""),
]
for _a, _b in _fx:
    if _a in doc: doc = doc.replace(_a, _b)
    else: print('FIX NOT APPLIED:', _a[:70])

dst = os.path.join(os.path.dirname(D), 'lit_design_strategy.md')
open(dst, 'w').write(doc)
print(dst, len(doc), 'chars;', len(re.findall(r'(?m)^### ', doc)), 'level-3 sections; extraB', len(extraB),
      '| synA', len(synA), 'synB', len(synB), 'dA', len(dA), 'dB', len(dB), 'uA', len(uA), 'uB', len(uB))
