# wave animation 
# x=0で波発生 + 自由端 & x=Lで固定端

w=2*pi* 50
k = 2*pi/8
L = 10

set sample 500
set xrange [0:L]
set yrange [-4:4]
set zeroaxis

do for [i=0:200] {
move = i*0.001
plot sin(w*move-k*x), -sin(w*move+k*x-2*k*L), -sin(w*move-k*x-2*k*L), sin(w*move+k*x-4*k*L)
replot sin(w*move-k*x)-sin(w*move+k*x-2*k*L)-sin(w*move-k*x-2*k*L)+sin(w*move+k*x-4*k*L)

}

