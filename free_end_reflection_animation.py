import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Button, RadioButtons

# 日本語フォントの設定 (Windows用)
plt.rcParams['font.family'] = 'MS Gothic'

# --- 物理量の設定 ---
A = 1.0       # 振幅 (Amplitude)
lam = 4.0     # 波長 (Wavelength)
T = 2.0       # 周期 (Period)
v = lam / T   # 波の速さ (Wave speed)

k = 2 * np.pi / lam    # 波数
omega = 2 * np.pi / T  # 角振動数

L = 8.0       # 境界の位置 (Boundary position)

# --- 空間・時間の初期設定 ---
x = np.linspace(0, 10, 500)
dt = 0.05
t = 0.0

boundary_mode = '自由端 (Free End)'

# --- 波の関数 ---
def get_incident_y(x, t):
    if boundary_mode == '反射なし (No Boundary)':
        condition = (x <= v * t)
    else:
        condition = (x <= v * t) & (x <= L)
    return np.where(condition, -A * np.sin(k * x - omega * t), 0.0)

def get_reflected_y(x, t):
    if boundary_mode == '反射なし (No Boundary)':
        return np.zeros_like(x)
        
    condition = (x >= 2 * L - v * t) & (x <= L)
    if boundary_mode == '自由端 (Free End)':
        return np.where(condition, -A * np.sin(k * (2 * L - x) - omega * t), 0.0)
    elif boundary_mode == '固定端 (Fixed End)':
        # 固定端の場合は位相が反転するため符号を反転させる
        return np.where(condition, A * np.sin(k * (2 * L - x) - omega * t), 0.0)
    return np.zeros_like(x)

def get_composite_y(x, t):
    return get_incident_y(x, t) + get_reflected_y(x, t)

# --- 描画のセットアップ ---
fig, ax = plt.subplots(figsize=(10, 6))
plt.subplots_adjust(bottom=0.25, right=0.75)  # 右側にラジオボタン用のスペースを確保

# 各波のプロット初期化
line_in, = ax.plot(x, get_incident_y(x, t), lw=1.5, ls='--', color='green', label='Incident wave', alpha=0.7)
line_ref, = ax.plot(x, get_reflected_y(x, t), lw=1.5, ls='--', color='orange', label='Reflected wave (Free end)', alpha=0.7)
line_comp, = ax.plot(x, get_composite_y(x, t), lw=2.5, color='blue', label='Composite wave')

# 境界の壁（x=L）の描画
wall_line = ax.axvline(L, color='red', lw=2, label=f'Boundary (x={L})')

# グラフの装飾
ax.set_ylim(-2.5 * A, 2.5 * A)
ax.set_xlim(0, 10)
ax.set_title("Wave Reflection Animation")
ax.set_xlabel("Position x [m]")
ax.set_ylabel("Displacement y [m]")
ax.grid(True)
legend = ax.legend(loc='upper left')

# 時間を表示するテキスト
time_text = ax.text(0.02, 0.90, f'Time = {t:.2f} s', transform=ax.transAxes, fontsize=12)

# --- アニメーションの制御変数 ---
is_playing = True

# --- アニメーション更新用関数 ---
def update(frame):
    global t, is_playing
    if is_playing:
        t += dt
        update_lines()
    return line_in, line_ref, line_comp, time_text

def update_lines():
    line_in.set_ydata(get_incident_y(x, t))
    line_ref.set_ydata(get_reflected_y(x, t))
    line_comp.set_ydata(get_composite_y(x, t))
    time_text.set_text(f'Time = {t:.2f} s')

# アニメーションの作成
ani = FuncAnimation(fig, update, frames=None, interval=50, blit=False, cache_frame_data=False)

# --- ボタンとラジオボタンの作成と配置 ---
ax_play  = plt.axes([0.10, 0.05, 0.10, 0.075])
ax_stop  = plt.axes([0.22, 0.05, 0.10, 0.075])
ax_prev  = plt.axes([0.34, 0.05, 0.10, 0.075])
ax_next  = plt.axes([0.46, 0.05, 0.10, 0.075])
ax_reset = plt.axes([0.58, 0.05, 0.10, 0.075])

ax_radio = plt.axes([0.78, 0.4, 0.20, 0.25], facecolor='lightgray')

btn_play  = Button(ax_play, 'Play')
btn_stop  = Button(ax_stop, 'Stop')
btn_prev  = Button(ax_prev, '< Step')
btn_next  = Button(ax_next, 'Step >')
btn_reset = Button(ax_reset, 'Reset')

radio = RadioButtons(ax_radio, ('自由端 (Free End)', '固定端 (Fixed End)', '反射なし (No Boundary)'))

# --- コールバック関数 ---
def play(event):
    global is_playing
    is_playing = True

def stop(event):
    global is_playing
    is_playing = False

def prev_step(event):
    global t, is_playing
    is_playing = False
    t -= dt
    if t < 0:
        t = 0
    update_lines()
    fig.canvas.draw_idle()

def next_step(event):
    global t, is_playing
    is_playing = False
    t += dt
    update_lines()
    fig.canvas.draw_idle()

def reset(event):
    global t, is_playing
    is_playing = False
    t = 0.0
    update_lines()
    fig.canvas.draw_idle()

def mode_changed(label):
    global boundary_mode, legend
    boundary_mode = label
    
    if boundary_mode == '自由端 (Free End)':
        wall_line.set_visible(True)
        wall_line.set_color('red')
        line_ref.set_label('Reflected wave (Free end)')
    elif boundary_mode == '固定端 (Fixed End)':
        wall_line.set_visible(True)
        wall_line.set_color('black')
        line_ref.set_label('Reflected wave (Fixed end)')
    else:
        wall_line.set_visible(False)
        line_ref.set_label('Reflected wave (None)')
    
    # legendを更新（一旦古いものを消す）
    legend.remove()
    legend = ax.legend(loc='upper left')
    
    update_lines()
    fig.canvas.draw_idle()

# ボタンと関数を紐付け
btn_play.on_clicked(play)
btn_stop.on_clicked(stop)
btn_prev.on_clicked(prev_step)
btn_next.on_clicked(next_step)
btn_reset.on_clicked(reset)
radio.on_clicked(mode_changed)

plt.show()
