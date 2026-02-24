# うなりのアニメーション (Beats)
# UTF-8

set term gif animate delay 10 size 800,400
set output "beats.gif"

f1 = 1.05
f2 = 0.95
w1 = 2*pi*f1
w2 = 2*pi*f2

set xrange [0:10]
set yrange [-2.5:2.5]
set samples 1000
set grid
set title "Beats (Superposition of two waves with slightly different frequencies)"

do for [i=0:100] {
    t_off = i * 0.1
    # 合成波: sin(w1*t) + sin(w2*t) = 2 * sin((w1+w2)/2 * t) * cos((w1-w2)/2 * t)
    plot sin(w1*(x+t_off)) + sin(w2*(x+t_off)) lw 2 lc "red" title "Superposed Wave", \
         2*cos((w1-w2)/2*(x+t_off)) lw 1 lt 2 lc "blue" title "Envelope", \
         -2*cos((w1-w2)/2*(x+t_off)) lw 1 lt 2 lc "blue" notitle
}

set output
set terminal windows
