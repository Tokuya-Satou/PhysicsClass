# 屈折とスネルの法則のアニメーション (Refraction and Snell's Law)
# UTF-8

set term gif animate delay 10 size 800,600
set output "refraction_snell.gif"

# 設定
v1 = 1.0        # 媒質1の速度
v2 = 0.6        # 媒質2の速度
theta1 = 45.0 * pi/180.0  # 入射角
w = 2*pi * 1.5  # 角振動数

k1 = w / v1
# スネルの法則: sin(theta1)/v1 = sin(theta2)/v2
sin_theta2 = (v2/v1) * sin(theta1)
theta2 = asin(sin_theta2)
k2 = w / v2

# 入射・屈折波の位相関数
# 境界は y = 0
# 進行方向ベクトル: n1 = (sin1, -cos1), n2 = (sin2, -cos2)
phase1(x, y, t) = w*t - k1*(x*sin(theta1) - y*cos(theta1))
phase2(x, y, t) = w*t - k2*(x*sin_theta2 - y*cos(theta2))

set xrange [-10:10]
set yrange [-10:10]
set isosamples 100
set samples 100
set pm3d map
set palette grey
unset colorbox
set size ratio 1
set title "Refraction and Snell's Law"

do for [frame=0:50] {
    t = frame * 0.1
    splot y > 0 ? sin(phase1(x, y, t)) : sin(phase2(x, y, t)) notitle
}

set output
set terminal windows
