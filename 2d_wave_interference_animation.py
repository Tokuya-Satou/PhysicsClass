import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Button

# --- 物理量の設定 ---
A = 1.0       # 波の振幅
lam = 2.0     # 波長 (Wavelength)
T = 1.0       # 周期 (Period)
v = lam / T   # 波の速さ (Wave speed)

k = 2 * np.pi / lam    # 波数
omega = 2 * np.pi / T  # 角振動数

# 波源の位置 (S1, S2)
source1 = (-3.0, 0.0)
source2 = (3.0, 0.0)

# --- 空間・時間の初期設定 ---
# パフォーマンスと画質のバランスを取るための解像度
N = 80 
x = np.linspace(-10, 10, N)
y = np.linspace(-10, 10, N)
X, Y = np.meshgrid(x, y)

R1 = np.sqrt((X - source1[0])**2 + (Y - source1[1])**2)
R2 = np.sqrt((X - source2[0])**2 + (Y - source2[1])**2)

dt = 0.05
t = 0.0

# --- 描画のセットアップ (3D) ---
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')
plt.subplots_adjust(bottom=0.20)  # ボタン用スペース

def get_wave_z(t):
    Z1 = np.where(R1 <= v * t, A * np.sin(k * R1 - omega * t), 0.0)
    Z2 = np.where(R2 <= v * t, A * np.sin(k * R2 - omega * t), 0.0)
    return Z1 + Z2

Z = get_wave_z(t)

# 初期の3Dプロット（線状の描画にするか、面を小さく分割すると軽くなります）
# rstride/cstrideを1に戻し、シェーディング(gouraud)を適用して滑らかに見せます
surf = ax.plot_surface(X, Y, Z, cmap='coolwarm', vmin=-2*A, vmax=2*A, rstride=1, cstride=1, linewidth=0, antialiased=True)

ax.set_title("3D Wave Interference (Optimized)")
ax.set_xlabel("Position x [m]")
ax.set_ylabel("Position y [m]")
ax.set_zlabel("Displacement z [m]")
ax.set_zlim(-2.5 * A, 2.5 * A)

ax.plot([source1[0]], [source1[1]], [0], 'ko', markersize=6, label="Source 1")
ax.plot([source2[0]], [source2[1]], [0], 'ko', markersize=6, label="Source 2")
ax.legend(loc="upper left")

time_text = fig.text(0.02, 0.95, '', fontsize=12, color='black', 
                    bbox=dict(facecolor='white', alpha=0.8, edgecolor='none'))

# --- アニメーションの制御変数 ---
is_playing = True

# --- アニメーション更新用関数 ---
def update(frame):
    global t, is_playing, surf
    if is_playing:
        t += dt
        Z = get_wave_z(t)
        
        # 3Dの高速な更新のコツ: remove()と再生成の負荷を抑えるために、
        # 面の生成に必要なデータポイントを更新するように試みますが、
        # Matplotlibの3D surfaceは完全にネイティブなデータ更新(set_data)を持たないため、
        # やはりremoveが必要ですが、解像度(N)とstrideを調整したことで大幅に改善されます。
        surf.remove()
        surf = ax.plot_surface(X, Y, Z, cmap='coolwarm', vmin=-2*A, vmax=2*A, rstride=1, cstride=1, linewidth=0, antialiased=True)
        time_text.set_text(f'Time = {t:.2f} s')
    return surf, time_text

ani = FuncAnimation(fig, update, frames=None, interval=30, blit=False, cache_frame_data=False)

# --- ボタンの作成と配置 ---
ax_play  = plt.axes([0.10, 0.05, 0.14, 0.05])
ax_stop  = plt.axes([0.26, 0.05, 0.14, 0.05])
ax_prev  = plt.axes([0.42, 0.05, 0.14, 0.05])
ax_next  = plt.axes([0.58, 0.05, 0.14, 0.05])
ax_reset = plt.axes([0.74, 0.05, 0.14, 0.05])

btn_play  = Button(ax_play, 'Play')
btn_stop  = Button(ax_stop, 'Stop')
btn_prev  = Button(ax_prev, '< Step')
btn_next  = Button(ax_next, 'Step >')
btn_reset = Button(ax_reset, 'Reset')

def play(event):
    global is_playing
    is_playing = True

def stop(event):
    global is_playing
    is_playing = False

def update_manual(new_t):
    global t, surf
    t = new_t
    if t < 0: t = 0
    Z = get_wave_z(t)
    surf.remove()
    surf = ax.plot_surface(X, Y, Z, cmap='coolwarm', vmin=-2*A, vmax=2*A, rstride=1, cstride=1, linewidth=0, antialiased=True)
    time_text.set_text(f'Time = {t:.2f} s')
    fig.canvas.draw_idle()

def prev_step(event):
    global is_playing
    is_playing = False
    update_manual(t - dt)

def next_step(event):
    global is_playing
    is_playing = False
    update_manual(t + dt)

def reset(event):
    global is_playing
    is_playing = False
    update_manual(0.0)

btn_play.on_clicked(play)
btn_stop.on_clicked(stop)
btn_prev.on_clicked(prev_step)
btn_next.on_clicked(next_step)
btn_reset.on_clicked(reset)

plt.show()
