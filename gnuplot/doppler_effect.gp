# ドップラー効果のアニメーション (Doppler Effect)
# UTF-8

set term gif animate delay 10 size 800,600
set output "doppler_effect.gif"

# 物理定数の設定
v_source = 0.5   # 波源の速度
v_wave = 1.0     # 波の速度
dt = 0.5         # 波の放出間隔
T_max = 20.0     # 全描画時間
N_frames = 60.0  # フレーム数

set xrange [-5:15]
set yrange [-10:10]
set size ratio -1
set grid
unset key
set title "Doppler Effect (Moving Source)"

# プロットのスタイル設定
set style fill empty

do for [frame=0:int(N_frames)] {
    t = frame * (T_max / N_frames)
    
    # 現在の波源の位置
    s_x = v_source * t
    s_y = 0
    
    # 波源と過去に放出された波面を一括でプロット
    # "+" はダミーデータ。every ::0::0 で1点だけプロットする。
    # ellipses の using は x:y:width:height
    plot "+" using (s_x):(s_y) every ::0::0 with points pt 7 ps 2 lc "red", \
         for [j=0:int(t/dt)] "+" using (v_source*j*dt):(0):(2*v_wave*(t-j*dt)):(2*v_wave*(t-j*dt)) every ::0::0 with ellipses lc "blue"
}

set output
set terminal windows
