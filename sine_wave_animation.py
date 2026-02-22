import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Button

# --- 物理量の設定 ---
A = 1.0       # 振幅 (Amplitude)
lam = 2.0     # 波長 (Wavelength)
T = 2.0       # 周期 (Period)
v = lam / T   # 波の速さ (Wave speed)

k = 2 * np.pi / lam    # 波数
omega = 2 * np.pi / T  # 角振動数

# --- 空間・時間の初期設定 ---
x = np.linspace(0, 10, 500)
dt = 0.05  # 1コマあたりの時間変化
t = 0.0

# --- 描画のセットアップ ---
fig, ax = plt.subplots(figsize=(8, 5))
plt.subplots_adjust(bottom=0.25)  # ボタン用のスペースを確保

# 初期状態の波のプロット
line, = ax.plot(x, A * np.sin(k * x - omega * t), lw=2, color='blue')
ax.set_ylim(-1.5 * A, 1.5 * A)
ax.set_xlim(0, 10)
ax.set_title("1D Sine Wave Animation")
ax.set_xlabel("Position x [m]")
ax.set_ylabel("Displacement y [m]")
ax.grid(True)

# 時間を表示するテキスト
time_text = ax.text(0.02, 0.90, '', transform=ax.transAxes, fontsize=12)

# --- アニメーションの制御変数 ---
is_playing = True

# --- アニメーション更新用関数 ---
def update(frame):
    global t, is_playing
    if is_playing:
        t += dt
        # グラフデータの更新
        line.set_ydata(A * np.sin(k * x - omega * t))
        time_text.set_text(f'Time = {t:.2f} s')
    return line, time_text

# アニメーションの作成（intervalはミリ秒単位で更新間隔を指定）
ani = FuncAnimation(fig, update, frames=None, interval=50, blit=False, cache_frame_data=False)

# --- ボタンの作成と配置 ---
# 左から順に [left, bottom, width, height] で指定
ax_play = plt.axes([0.15, 0.05, 0.15, 0.075])
ax_stop = plt.axes([0.31, 0.05, 0.15, 0.075])
ax_prev = plt.axes([0.47, 0.05, 0.15, 0.075])
ax_next = plt.axes([0.63, 0.05, 0.15, 0.075])

btn_play = Button(ax_play, 'Play')
btn_stop = Button(ax_stop, 'Stop')
btn_prev = Button(ax_prev, '< Step')
btn_next = Button(ax_next, 'Step >')

# --- ボタンクリック時のコールバック関数 ---
def play(event):
    global is_playing
    is_playing = True

def stop(event):
    global is_playing
    is_playing = False

def prev_step(event):
    global t, is_playing
    is_playing = False  # コマ送り時は自動再生を停止
    t -= dt
    line.set_ydata(A * np.sin(k * x - omega * t))
    time_text.set_text(f'Time = {t:.2f} s')
    fig.canvas.draw_idle()

def next_step(event):
    global t, is_playing
    is_playing = False  # コマ送り時は自動再生を停止
    t += dt
    line.set_ydata(A * np.sin(k * x - omega * t))
    time_text.set_text(f'Time = {t:.2f} s')
    fig.canvas.draw_idle()

# ボタンと関数を紐付け
btn_play.on_clicked(play)
btn_stop.on_clicked(stop)
btn_prev.on_clicked(prev_step)
btn_next.on_clicked(next_step)

plt.show()
