# 縦波の表示と横波表示の比較 (Longitudinal and Transverse Waves)
# UTF-8

set term gif animate delay 5 size 800,600
set output "longitudinal_wave.gif"

L = 10.0
A = 0.5
k = 2*pi/4.0
w = 2*pi*1.0
num_particles = 41

set multiplot layout 2,1 title "Longitudinal Wave (Top) vs. Transverse Representation (Bottom)"

do for [t_idx=0:40] {
    t = t_idx * 0.05
    
    # 上段: 縦波（実際の粒子の動き）
    set origin 0, 0.5
    set size 1, 0.5
    set xrange [-0.5:L+0.5]
    set yrange [-1:1]
    unset ytics
    set title "Physical Particle Displacement (Longitudinal)"
    plot for [i=0:num_particles-1] \
        "+" using (i*L/(num_particles-1) + A*sin(w*t - k*(i*L/(num_particles-1)))):(0) \
        every 1:1:1:1 with points pt 7 ps 1.5 lc "blue" notitle
    
    # 下段: 横波表示（y-xグラフ）
    set origin 0, 0
    set size 1, 0.5
    set ytics
    set grid
    set title "Standard y-x Graph Representation"
    set xrange [0:L]
    set yrange [-1.2:1.2]
    plot A*sin(w*t - k*x) lw 2 lc "red" title "Displacement"
    
    unset multiplot
    set multiplot layout 2,1
}

unset multiplot
set output
set terminal windows
