"""
熱力学の教材：鉛直シリンダー＋なめらかなピストンに閉じ込めた理想気体（単原子分子）

モデル
  - ピストンは常に力のつり合いの状態にある（準静的変化）。
        p S = p0 S + (m_p + M) g + f(x),   f(x) = f0 + a x   （f は下向き正）
    よって、ピストンが自由に動ける間は気体の状態は p-V 図の直線
        p = p_c + k V,   p_c = p0 + (m_p + M) g / S + f0 / S,   k = a / S^2
    の上にある。a < 0 なら右下がりの直線になる。
  - 加熱・放熱は「加熱パワー P [W]」で与える（P > 0 加熱、P < 0 放熱、P = 0 断熱）。
    直線上での熱量は  dQ = (5/2) p dV + (3/2) V dp  なので、ちょうど積分できる。
        Q(V1→V2) = F(V2) − F(V1),   F(V) = (5/2) p_c V + 2 k V^2
  - おもり・外力・大気圧・ストッパー位置を変えたときは、ゆっくり（準静的に）値が変わり、
    その間に加熱がなければ断熱変化（pV^γ 一定）で次のつり合いの位置へ移る。
  - ストッパーに当たっている間は定積変化になる。気体の圧力がつり合いの値を超えた（下回った）ら離れる。
  - a < 0 のとき、直線上には「吸熱→放熱の境目」V* = −5 p_c / (8k) がある。
    加熱してもこの点より先へは準静的には進めない。P < 0（放熱）にすると、同じ向きに体積変化を続ける。
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Slider, Button, CheckButtons, TextBox
from matplotlib.patches import Rectangle, FancyArrowPatch
from matplotlib import colors, font_manager

# 日本語フォント：使える環境のものを選ぶ
_installed = {f.name for f in font_manager.fontManager.ttflist}
for _name in ['Meiryo', 'Yu Gothic', 'MS Gothic', 'Hiragino Sans', 'Noto Sans CJK JP', 'IPAexGothic']:
    if _name in _installed:
        plt.rcParams['font.family'] = _name
        break
plt.rcParams['axes.unicode_minus'] = False

# --- 物理定数・固定パラメータ ---
R = 8.314          # 気体定数 [J/(mol K)]
G = 9.8            # 重力加速度 [m/s^2]
N_MOL = 1.0        # 物質量 [mol]
CV = 1.5 * R       # 単原子分子の定積モル比熱
GAMMA = 5.0 / 3.0  # 比熱比
S = 0.025          # ピストンの断面積 [m^2]
M_PISTON = 0.0     # ピストンの質量 [kg]
P_ATM = 1.0e5      # 大気圧 [Pa]
X_TOP = 3.0        # シリンダーの高さ [m]
T_INIT = 300.0     # 初期温度 [K]
T_FLOOR = 1.0      # これより低い温度にはしない [K]

# --- パラメータの初期値 ---
M_INIT = 0.0       # おもりの質量 [kg]
F0_INIT = 0.0      # 外力 f0 [N]（下向き正）
A_INIT = 0.0       # 外力の係数 a [N/m]
P_HEAT_INIT = 0.0  # 加熱パワー [W]
XMIN_INIT = 0.2    # 下のストッパーの高さ [m]
XMAX_INIT = 2.5    # 上のストッパーの高さ [m]
DT_ISO_INIT = 50.0 # 等温線の温度間隔 [K]
Q_BUDGET_INIT = 1000.0  # 「Qを加える」の初期値 [J]

# --- 時間の設定 ---
DT = 0.05          # 1コマあたりの時間 [s]
NSUB = 20          # 1コマあたりの分割数
# パラメータを変えたとき、1秒あたりに変化する量（準静的にゆっくり変える）
RATE = dict(M=200.0, f0=4000.0, a=8000.0, p0=1.0e5, xmin=0.5, xmax=0.5)

# --- 状態 ---
cur = dict(M=M_INIT, f0=F0_INIT, a=A_INIT, p0=P_ATM, xmin=XMIN_INIT, xmax=XMAX_INIT)
tgt = dict(cur)
gas = dict(V=0.0, T=T_INIT)
total = dict(Q=0.0, W=0.0, T_ref=T_INIT)
last_dir = 1.0      # 直前に体積が変化した向き（+1 膨張, −1 圧縮）
stuck = False       # 吸熱→放熱の境目で止まっているか
q_budget = None     # 「Qを加える」の残り [J]
message = ''
is_running = True
traj_V, traj_p = [], []


def p_c():
    return cur['p0'] + ((M_PISTON + cur['M']) * G + cur['f0']) / S


def k_coef():
    return cur['a'] / S**2


def p_eq(V):
    """ピストンがつり合うときの気体の圧力"""
    return p_c() + k_coef() * V


def v_min():
    return S * cur['xmin']


def v_max():
    return S * cur['xmax']


def p_gas():
    return N_MOL * R * gas['T'] / gas['V']


# --- 物理の計算 ---
def initial_volume(T):
    """温度 T でつり合う体積（ストッパーの範囲内で最も小さいもの）"""
    vs = np.linspace(v_min(), v_max(), 2000)
    g = N_MOL * R * T / vs - p_eq(vs)
    if g[0] <= 0:
        return vs[0]
    idx = np.nonzero(g <= 0)[0]
    if len(idx) == 0:
        return vs[-1]
    lo, hi = vs[idx[0] - 1], vs[idx[0]]
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if N_MOL * R * T / mid - p_eq(mid) > 0:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def adiabatic_to(V2):
    """断熱変化で体積 V2 へ"""
    V, T = gas['V'], gas['T']
    T2 = T * (V / V2) ** (GAMMA - 1)
    total['W'] += N_MOL * CV * (T - T2)
    gas['V'], gas['T'] = V2, T2


def relax():
    """パラメータ変化後、断熱的に次のつり合いの位置へ移る"""
    vmin, vmax = v_min(), v_max()
    if gas['V'] > vmax:
        adiabatic_to(vmax)
    elif gas['V'] < vmin:
        adiabatic_to(vmin)

    V0 = gas['V']
    pg0 = p_gas()

    def gf(v):  # 気体の圧力 − つり合いの圧力（正なら膨張する向き）
        return pg0 * (V0 / v) ** GAMMA - p_eq(v)

    g0 = gf(V0)
    if abs(g0) <= 1e-9 * pg0:
        return
    if g0 > 0:
        if V0 >= vmax * (1 - 1e-12):
            return  # 上のストッパーに押し付けられている
        bound = vmax
    else:
        if V0 <= vmin * (1 + 1e-12):
            return  # 下のストッパーに載っている
        bound = vmin
    vs = np.linspace(V0, bound, 400)[1:]
    idx = np.nonzero(np.sign(gf(vs)) != np.sign(g0))[0]
    if len(idx) == 0:
        adiabatic_to(bound)
        return
    lo = vs[idx[0] - 1] if idx[0] > 0 else V0
    hi = vs[idx[0]]
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if np.sign(gf(mid)) == np.sign(g0):
            lo = mid
        else:
            hi = mid
    adiabatic_to(0.5 * (lo + hi))


def apply_heat(q):
    """熱量 q を加える。実際に気体が受け取った熱量を返す"""
    global last_dir, stuck, message
    used = 0.0
    leaving = False  # ストッパーから離れた直後
    for _ in range(6):
        if abs(q) < 1e-12:
            break
        V, T = gas['V'], gas['T']
        pg, pe = p_gas(), p_eq(V)
        vmin, vmax = v_min(), v_max()
        ptol = 1e-7 * max(abs(pe), 1.0)
        at_max = V >= vmax * (1 - 1e-9) and pg >= pe - ptol
        at_min = V <= vmin * (1 + 1e-9) and pg <= pe + ptol

        if (at_max or at_min) and not leaving:
            # ストッパーに当たっている：定積変化
            T_eq = pe * V / (N_MOL * R)
            q_need = N_MOL * CV * (T_eq - T)  # ストッパーから離れるのに必要な熱量
            leaves = (at_max and q < 0 and T_eq > T_FLOOR and q < q_need) or \
                     (at_min and q > 0 and q > q_need)
            if leaves:
                gas['T'] = T_eq
                used += q_need
                q -= q_need
                leaving = True
                continue
            T2 = max(T + q / (N_MOL * CV), T_FLOOR)
            used += N_MOL * CV * (T2 - T)
            gas['T'] = T2
            break

        # ピストンが自由に動ける：つり合いの直線上を動く
        leaving = False
        if pe <= 0:
            break
        pc, k = p_c(), k_coef()

        def F(v):
            return 2.5 * pc * v + 2.0 * k * v * v

        target = F(V) + q
        stuck_now = False
        if abs(k) * vmax < 1e-6 * abs(pc):
            V2 = target / (2.5 * pc)
        else:
            Vs = -2.5 * pc / (4.0 * k)  # 吸熱⇔放熱の境目
            d2 = (target - F(Vs)) / (2.0 * k)
            side = np.sign(V - Vs) if abs(V - Vs) > 1e-12 else last_dir
            if side == 0:
                side = last_dir
            if d2 < 0:
                V2, stuck_now = Vs, True
            else:
                V2 = Vs + side * np.sqrt(d2)

        done = True
        if V2 > vmax:
            V2, stuck_now, done = vmax, False, False
        elif V2 < vmin:
            V2, stuck_now, done = vmin, False, False

        T2 = p_eq(V2) * V2 / (N_MOL * R)
        if T2 < T_FLOOR:
            message = '温度がほぼ 0 K になったので、これ以上放熱できません'
            break
        dq = F(V2) - F(V)
        total['W'] += pc * (V2 - V) + 0.5 * k * (V2**2 - V**2)
        if V2 != V:
            last_dir = np.sign(V2 - V)
        gas['V'], gas['T'] = V2, T2
        used += dq
        q -= dq
        if stuck_now:
            stuck = True
            break
        if done:
            break
    return used


def ramp(dt):
    """パラメータを目標値に向けて少しずつ変える。変化したら True"""
    changed = False
    for key, rate in RATE.items():
        diff = tgt[key] - cur[key]
        if diff != 0:
            step = rate * dt
            cur[key] = tgt[key] if abs(diff) <= step else cur[key] + np.sign(diff) * step
            changed = True
    return changed


def heater_power():
    if q_budget is not None:
        return np.sign(q_budget) * max(abs(s_P.val), 200.0)
    return s_P.val


def step_frame():
    global q_budget, stuck, message
    P = heater_power()
    q_frame = P * DT
    if q_budget is not None and abs(q_frame) > abs(q_budget):
        q_frame = q_budget
    if q_frame != 0:
        stuck = False
    used_frame = 0.0
    for _ in range(NSUB):
        if ramp(DT / NSUB):
            relax()
        if q_frame != 0:
            used_frame += apply_heat(q_frame / NSUB)
    total['Q'] += used_frame
    if q_budget is not None:
        q_budget -= used_frame
        if stuck:
            message = f'Q指定を中止しました（残り {q_budget:.0f} J）'
            q_budget = None
        elif abs(q_budget) < 1e-6:
            message = f'指定した熱量 {tb_Q.text} J を加え終わりました'
            q_budget = None


def reset_state():
    global last_dir, stuck, q_budget, message
    cur.update(tgt)
    gas['T'] = T_INIT
    gas['V'] = initial_volume(T_INIT)
    last_dir, stuck, q_budget, message = 1.0, False, None, ''
    clear_record()


def clear_record():
    total['Q'] = 0.0
    total['W'] = 0.0
    total['T_ref'] = gas['T']
    traj_V.clear()
    traj_p.clear()


# --- 描画のセットアップ ---
fig = plt.figure(figsize=(15, 9))
fig.canvas.manager.set_window_title('シリンダーとピストン（熱力学）')

# シリンダーのアニメーション
ax_cyl = fig.add_axes([0.055, 0.38, 0.22, 0.58])
ax_cyl.set_xlim(-0.75, 0.75)
ax_cyl.set_ylim(-0.4, X_TOP + 0.5)
ax_cyl.set_aspect('auto')
ax_cyl.set_xticks([])
ax_cyl.set_ylabel('高さ x [m]')
ax_cyl.spines[['top', 'right', 'bottom']].set_visible(False)

W_CYL = 0.4    # シリンダーの半幅（見た目のみ）
PT = 0.08      # ピストンの厚さ（見た目のみ）
ax_cyl.plot([-W_CYL, -W_CYL, W_CYL, W_CYL], [X_TOP, 0, 0, X_TOP], color='black', lw=4)
temp_cmap = plt.get_cmap('coolwarm')
temp_norm = colors.Normalize(vmin=0, vmax=600)
gas_patch = ax_cyl.add_patch(Rectangle((-W_CYL, 0), 2 * W_CYL, 1, color=temp_cmap(0.5), alpha=0.7))
piston_patch = ax_cyl.add_patch(Rectangle((-W_CYL, 1), 2 * W_CYL, PT, facecolor='dimgray', edgecolor='black'))
weight_patch = ax_cyl.add_patch(Rectangle((-0.25, 1), 0.5, 0.1, facecolor='saddlebrown', edgecolor='black'))
weight_text = ax_cyl.text(0, 1, '', ha='center', va='center', color='white', fontsize=9)
force_arrow = ax_cyl.add_patch(FancyArrowPatch((0, 0), (0, 0), arrowstyle='-|>', mutation_scale=20,
                                               lw=2.5, color='green'))
force_text = ax_cyl.text(0.08, 0, '', color='green', fontsize=9, va='center')
STOP_W, STOP_H = 0.07, 0.04
stoppers = [ax_cyl.add_patch(Rectangle((0, 0), STOP_W, STOP_H, color='black')) for _ in range(4)]
heater_patch = ax_cyl.add_patch(Rectangle((-0.5, -0.32), 1.0, 0.1, facecolor='lightgray', edgecolor='black'))
heater_text = ax_cyl.text(0, -0.39, '', ha='center', va='top', fontsize=10)
heat_arrows = [ax_cyl.add_patch(FancyArrowPatch((xa, -0.2), (xa, -0.03), arrowstyle='-|>',
                                                mutation_scale=14, lw=2)) for xa in (-0.25, 0, 0.25)]
atm_text = ax_cyl.text(0, X_TOP + 0.3, '', ha='center', va='center', fontsize=10)
stuck_text = ax_cyl.text(0, X_TOP + 0.1, '', ha='center', va='center', fontsize=8, color='crimson')

# p-V グラフ
ax_pv = fig.add_axes([0.33, 0.42, 0.42, 0.53])
ax_pv.set_xlabel('体積 V [×10⁻³ m³]')
ax_pv.set_ylabel('圧力 p [×10⁵ Pa]')
ax_pv.set_title('p-V グラフ')
ax_pv.grid(True, alpha=0.3)
traj_line, = ax_pv.plot([], [], color='crimson', lw=2, label='状態変化')
eq_line_dash, = ax_pv.plot([], [], color='seagreen', lw=1, ls='--', alpha=0.6)
eq_line, = ax_pv.plot([], [], color='seagreen', lw=1.5, alpha=0.8, label='つり合いの直線')
vmin_line = ax_pv.axvline(0, color='gray', lw=1, ls=':')
vmax_line = ax_pv.axvline(0, color='gray', lw=1, ls=':')
state_dot, = ax_pv.plot([], [], 'o', color='crimson', ms=8, zorder=5)
ax_pv.legend(loc='upper right', fontsize=9)
iso_artists = []
pv_lim = dict(V=1.0, p=1.0)

info_text = fig.text(0.775, 0.955, '', va='top', fontsize=10)


def to_plot(V, p):
    return np.asarray(V) * 1e3, np.asarray(p) / 1e5


def draw_isotherms():
    for a in iso_artists:
        a.remove()
    iso_artists.clear()
    if not chk.get_status()[1]:
        return
    dT = s_dT.val
    Vl, pl = pv_lim['V'] / 1e3, pv_lim['p'] * 1e5  # SI 単位
    T_max = pl * Vl / (N_MOL * R)
    Ts = np.arange(dT, T_max + dT, dT)[:80]
    every = 1 if len(Ts) <= 15 else int(np.ceil(len(Ts) / 15))
    for i, T in enumerate(Ts):
        V_start = N_MOL * R * T / pl
        vs = np.linspace(V_start, Vl, 200)
        xs, ys = to_plot(vs, N_MOL * R * T / vs)
        line, = ax_pv.plot(xs, ys, color='gray', lw=0.8, alpha=0.5, zorder=1)
        iso_artists.append(line)
        if i % every == 0:
            iso_artists.append(ax_pv.text(xs[-1], ys[-1], f'{T:.0f}K', fontsize=7, color='gray',
                                          ha='right', va='bottom', clip_on=True))


def update_pv_limits(force=False):
    Vs = traj_V + [gas['V'], v_max()]
    ps = traj_p + [p_gas(), max(p_eq(v_min()), p_eq(v_max()))]
    want_V = 1.15 * max(Vs) * 1e3
    want_p = max(1.2 * max(ps) / 1e5, 0.5)
    if force or want_V > pv_lim['V'] or want_p > pv_lim['p'] \
            or want_V < 0.6 * pv_lim['V'] or want_p < 0.6 * pv_lim['p']:
        pv_lim['V'], pv_lim['p'] = want_V, want_p
        ax_pv.set_xlim(0, want_V)
        ax_pv.set_ylim(0, want_p)
        draw_isotherms()


def draw():
    V, T = gas['V'], gas['T']
    x = V / S
    p = p_gas()

    # シリンダー
    gas_patch.set_height(x)
    gas_patch.set_color(temp_cmap(temp_norm(T)))
    piston_patch.set_y(x)
    top = x + PT
    if cur['M'] > 0.5:
        h = 0.08 + 0.35 * min(cur['M'] / 500.0, 1.0)
        weight_patch.set_visible(True)
        weight_patch.set_y(top)
        weight_patch.set_height(h)
        weight_text.set_position((0, top + h / 2))
        weight_text.set_text(f'{cur["M"]:.0f} kg')
        top += h
    else:
        weight_patch.set_visible(False)
        weight_text.set_text('')
    f = cur['f0'] + cur['a'] * x
    if abs(f) > 1.0:
        L = 0.15 + 0.45 * min(abs(f) / 10000.0, 1.0)
        if f > 0:
            force_arrow.set_positions((0, top + L), (0, top))
        else:
            force_arrow.set_positions((0, top), (0, top + L))
        force_arrow.set_visible(True)
        force_text.set_position((0.08, top + L / 2))
        force_text.set_text(f'f = {f:.0f} N\n({"下向き" if f > 0 else "上向き"})')
    else:
        force_arrow.set_visible(False)
        force_text.set_text('')
    xmin, xmax = cur['xmin'], cur['xmax']
    for i, (sx, sy) in enumerate([(-W_CYL, xmin - STOP_H), (W_CYL - STOP_W, xmin - STOP_H),
                                  (-W_CYL, xmax + PT), (W_CYL - STOP_W, xmax + PT)]):
        stoppers[i].set_xy((sx, sy))
    P = heater_power()
    if P > 0:
        heater_patch.set_facecolor('tomato')
        heater_text.set_text(f'加熱  P = {P:.0f} W')
        col, start, end = 'red', -0.2, -0.03
    elif P < 0:
        heater_patch.set_facecolor('cornflowerblue')
        heater_text.set_text(f'放熱（低温熱源）  P = {P:.0f} W')
        col, start, end = 'blue', -0.03, -0.2
    else:
        heater_patch.set_facecolor('lightgray')
        heater_text.set_text('断熱（P = 0）')
        col = None
    for xa, arr in zip((-0.25, 0, 0.25), heat_arrows):
        arr.set_visible(col is not None)
        if col is not None:
            arr.set_positions((xa, start), (xa, end))
            arr.set_color(col)
    atm_text.set_text(f'大気圧 p₀ = {cur["p0"] / 1e5:.2f}×10⁵ Pa' if cur['p0'] > 0 else '真空（大気圧なし）')
    if stuck:
        stuck_text.set_text('吸熱⇔放熱の境目：加熱ではこれ以上進めない\n（P < 0 で放熱すると体積変化を続ける）')
    else:
        stuck_text.set_text(message)

    # p-V グラフ
    if not traj_V or abs(traj_V[-1] - V) > 1e-9 or abs(traj_p[-1] - p) > 1e-3:
        traj_V.append(V)
        traj_p.append(p)
        if len(traj_V) > 20000:
            del traj_V[0], traj_p[0]
    update_pv_limits()
    traj_line.set_data(*to_plot(traj_V, traj_p))
    state_dot.set_data(*to_plot([V], [p]))
    show_eq = chk.get_status()[2]
    vs_all = np.linspace(1e-6, pv_lim['V'] / 1e3, 200)
    vs_in = np.linspace(v_min(), v_max(), 100)
    eq_line_dash.set_data(*to_plot(vs_all, p_eq(vs_all)))
    eq_line.set_data(*to_plot(vs_in, p_eq(vs_in)))
    eq_line_dash.set_visible(show_eq)
    eq_line.set_visible(show_eq)
    vmin_line.set_xdata([v_min() * 1e3] * 2)
    vmax_line.set_xdata([v_max() * 1e3] * 2)

    # 数値の表示
    if V >= v_max() * (1 - 1e-9) and p >= p_eq(V) - 1e-3:
        contact = '上のストッパーに接触'
    elif V <= v_min() * (1 + 1e-9) and p <= p_eq(V) + 1e-3:
        contact = '下のストッパーに接触'
    else:
        contact = 'ピストンは自由に動ける'
    dU = N_MOL * CV * (T - total['T_ref'])
    info_text.set_text(
        '【気体の状態】\n'
        f'  p = {p / 1e5:.3f} ×10⁵ Pa\n'
        f'  V = {V * 1e3:.2f} ×10⁻³ m³\n'
        f'  x = {x:.3f} m\n'
        f'  T = {T:.1f} K\n'
        f'  {contact}\n\n'
        '【グラフ消去からの合計】\n'
        f'  吸収した熱量  Q = {total["Q"]:8.1f} J\n'
        f'  気体がした仕事 W = {total["W"]:8.1f} J\n'
        f'  内部エネルギー変化 ΔU = {dU:8.1f} J\n'
        f'  （ΔU + W = {dU + total["W"]:8.1f} J）'
        + (f'\n\nQ指定：残り {q_budget:.0f} J' if q_budget is not None else '')
    )


# --- ウィジェット ---
SL_H = 0.03
def make_slider(rect, label, vmin, vmax, vinit, step, fmt):
    return Slider(fig.add_axes(rect), label, vmin, vmax, valinit=vinit, valstep=step, valfmt=fmt)

s_M = make_slider([0.13, 0.27, 0.30, SL_H], 'おもり M [kg]', 0, 500, M_INIT, 1, '%.0f')
s_f0 = make_slider([0.13, 0.22, 0.30, SL_H], '外力 f₀ [N]\n(下向き正)', -10000, 10000, F0_INIT, 50, '%.0f')
s_a = make_slider([0.13, 0.17, 0.30, SL_H], '外力の係数 a [N/m]', -10000, 10000, A_INIT, 100, '%.0f')
s_P = make_slider([0.13, 0.12, 0.30, SL_H], '加熱パワー P [W]\n(負は放熱)', -1000, 1000, P_HEAT_INIT, 10, '%.0f')
s_xmin = make_slider([0.60, 0.27, 0.25, SL_H], '下のストッパー [m]', 0.05, X_TOP, XMIN_INIT, 0.01, '%.2f')
s_xmax = make_slider([0.60, 0.22, 0.25, SL_H], '上のストッパー [m]', 0.05, X_TOP, XMAX_INIT, 0.01, '%.2f')
s_dT = make_slider([0.60, 0.17, 0.25, SL_H], '等温線の間隔 [K]', 10, 200, DT_ISO_INIT, 10, '%.0f')
fig.text(0.13, 0.075, '外力 f = f₀ + a x （x はピストンの高さ、下向きを正）', fontsize=9)


def on_param(_):
    global stuck
    tgt['M'] = s_M.val
    tgt['f0'] = s_f0.val
    tgt['a'] = s_a.val
    tgt['xmin'] = min(s_xmin.val, s_xmax.val - 0.05)
    tgt['xmax'] = max(s_xmax.val, tgt['xmin'] + 0.05)
    stuck = False


for s in (s_M, s_f0, s_a, s_xmin, s_xmax):
    s.on_changed(on_param)
s_dT.on_changed(lambda _: draw_isotherms())

chk = CheckButtons(fig.add_axes([0.80, 0.50, 0.17, 0.12]), ['大気圧あり', '等温線を表示', 'つり合いの直線'],
                   [True, True, True])


def on_check(label):
    if label == '大気圧あり':
        tgt['p0'] = P_ATM if chk.get_status()[0] else 0.0
    elif label == '等温線を表示':
        draw_isotherms()


chk.on_clicked(on_check)

tb_Q = TextBox(fig.add_axes([0.66, 0.08, 0.08, 0.04]), 'Q指定 [J] ', initial=str(Q_BUDGET_INIT))
btn_addQ = Button(fig.add_axes([0.75, 0.08, 0.10, 0.04]), 'このQを加える')
btn_stop = Button(fig.add_axes([0.80, 0.42, 0.17, 0.05]), '加熱・放熱を止める (P=0)')
btn_pause = Button(fig.add_axes([0.80, 0.36, 0.17, 0.05]), '一時停止')
btn_clear = Button(fig.add_axes([0.80, 0.30, 0.08, 0.05]), 'グラフ消去')
btn_reset = Button(fig.add_axes([0.89, 0.30, 0.08, 0.05]), 'リセット')
fig.text(0.60, 0.035, '「このQを加える」：P スライダーの大きさ（0 のときは 200 W）で、指定した熱量だけ加えて止まる',
         fontsize=8)


def on_addQ(_):
    global q_budget, message
    try:
        q = float(tb_Q.text)
    except ValueError:
        message = 'Q には数値を入力してください'
        return
    q_budget = q if q != 0 else None
    message = ''


def on_stop(_):
    global q_budget
    q_budget = None
    s_P.set_val(0)


def on_pause(_):
    global is_running
    is_running = not is_running
    btn_pause.label.set_text('一時停止' if is_running else '再開')


def on_clear(_):
    clear_record()
    update_pv_limits(force=True)


def on_reset(_):
    s_P.set_val(0)
    reset_state()
    update_pv_limits(force=True)


btn_addQ.on_clicked(on_addQ)
btn_stop.on_clicked(on_stop)
btn_pause.on_clicked(on_pause)
btn_clear.on_clicked(on_clear)
btn_reset.on_clicked(on_reset)


# --- アニメーション ---
def update(frame):
    if is_running:
        step_frame()
    draw()
    return []


reset_state()
update_pv_limits(force=True)
draw()
ani = FuncAnimation(fig, update, interval=int(DT * 1000), blit=False, cache_frame_data=False)
plt.show()
