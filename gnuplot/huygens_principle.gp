# ホイヘンスの原理のアニメーション (Huygens' Principle)
# UTF-8

set term gif animate delay 10 size 800,600
set output "huygens_principle.gp.gif" # ファイル名の重複を避けるため.gif付き

# 設定
num_sources = 11    # 素元波の源の数
spacing = 1.0       # 源の間隔
w = 2*pi * 1.0      # 角振動数
v = 1.0             # 速度
k = w / v

set xrange [-2:10]
set yrange [-10:10]
set isosamples 150
set samples 150
set pm3d map
set palette rgbformulae 33,13,10
unset colorbox
set size ratio -1
set title "Huygens' Principle (Superposition of Secondary Wavelets)"

# 各点波源 (0, y_s) からの合成波を計算する関数
# dist(x,y, ys) = sqrt(x**2 + (y-ys)**2)
# wave(x,y,t) = sum( sin(w*t - k*dist) / sqrt(dist) )

wave(x, y, t) = sum [i=0:num_sources-1] ( \
    ys = (i - (num_sources-1)/2.0) * spacing, \
    d = sqrt(x**2 + (y-ys)**2), \
    d < 0.1 ? 0 : sin(w*t - k*d) / sqrt(d) \
)

do for [frame=0:40] {
    t = frame * 0.1
    splot x >= 0 ? wave(x, y, t) : 0 notitle
}

set output
set terminal windows
