# ドップラー効果のアニメーション (Doppler Effect)
# UTF-8

set term gif animate delay 10 size 800,600
set output "doppler_effect.gif"

# 物理定数の設定
v_source = 0.5   # 波源の速度
v_wave = 1.0     # 波の速度
dt = 0.5        # 波の放出間隔
T_max = 20      # 全描画時間
N_frames = 60   # フレーム数

set xrange [-5:15]
set yrange [-10:10]
set size ratio -1
set grid
unset key
set title "Doppler Effect (Moving Source)"

# 波面の円を描画するための関数
# x0, y0: 放出時の座標, t0: 放出時刻, t: 現在時刻
circle_x(theta, x0, t0, t) = x0 + v_wave * (t - t0) * cos(theta)
circle_y(theta, y0, t0, t) = y0 + v_wave * (t - t0) * sin(theta)

do for [frame=0:N_frames] {
    t = frame * (T_max / N_frames)
    
    # 現在の波源の位置
    s_x = v_source * t
    s_y = 0
    
    plot s_x, s_y with points pt 7 ps 2 lc "red"  # 波源を点で表示
    
    # 過去に放出された波面を描画
    do for [j=0:int(t/dt)] {
        t0 = j * dt
        r = v_wave * (t - t0)
        x0 = v_source * t0
        
        if (r > 0) {
            set object (j+1) circle at x0,0 size r arc [0:360] outline lc "blue" lw 1
        }
    }
    
    replot
    
    # オブジェクトのクリア（次のフレームのため）
    do for [j=0:int(t/dt)+1] { unset object (j+1) }
}

set output
set terminal windows
