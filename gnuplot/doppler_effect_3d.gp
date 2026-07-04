# ドップラー効果の3Dアニメーション (Doppler Effect, 3D surface)
# UTF-8
# 波源(x軸上を移動)から放出された波面を、半径方向のガウス型パルスの重ね合わせとして
# 3D曲面(splot)で表示する。進行方向前方でリング間隔が詰まり、後方で広がる様子が立体的に見える。

set term gif animate delay 10 size 900,700
set output "doppler_effect_3d.gif"

# 物理定数の設定
v_source = 1.5   # 波源の速度
v_wave = 1.0     # 波の速度
dt = 1.5         # 波の放出間隔
T_max = 20.0     # 全描画時間
N_frames = 60.0  # フレーム数

A = 0.4          # パルスの高さ
sigma = 0.35     # パルスの太さ(半径方向)

half_width = 10  # 表示窓の半幅(波源に追従させる)
set yrange [-10:10]
set zrange [-3:3]
set isosamples 150,150
set samples 150,150
unset key
unset xtics
unset ytics
unset ztics
unset border
unset colorbox
set hidden3d
set pm3d
set pm3d lighting primary 0.5 specular 0.4
set palette defined (-0.4 "#08306b", -0.16 "#4292c6", 0 "#f7f7f7", 0.16 "#fdae6b", 0.4 "#a50f15")
set view 35,320
set title "Doppler Effect (3D Wavefronts)"

do for [frame=0:N_frames] {
    t = frame * (T_max / N_frames)
    s_x = v_source * t

    # カメラ(表示窓)を波源に追従させる
    set xrange [s_x - half_width : s_x + half_width]

    # 波源位置を示す短い縦棒(z方向の点)
    set arrow 1 from s_x,0,0 to s_x,0,0.5 nohead lc rgb "black" lw 2 front

    # 各放出リングをガウス型パルスとして足し合わせる文字列を構築
    # (見やすさのため直近13個の波面のみを重ね合わせる)
    j_last = int(t/dt)
    j_first = (j_last - 12 > 0) ? j_last - 12 : 0
    expr = "0"
    do for [j=j_first:j_last] {
        t0 = j * dt
        r = v_wave * (t - t0)
        x0 = v_source * t0
        if (r > 0) {
            expr = expr . sprintf(" + %f*exp(-(sqrt((x-(%f))**2+y**2)-(%f))**2/(2*%f**2))", A, x0, r, sigma)
        }
    }
    cmd = "splot " . expr . " with pm3d"

    eval cmd

    unset arrow 1
}

set output
set terminal windows
