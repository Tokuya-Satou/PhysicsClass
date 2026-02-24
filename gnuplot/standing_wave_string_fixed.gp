# 弦の振動
# x=0で波発生 + 固定端 & x=Lで固定端


lambda = 20.0/3
L = 10

f= 400/lambda
T=1/f
w=2*pi*f
k = 2*pi/lambda

set sample 1000
set xrange [-0.5:10.5]
set yrange [-4.5:4.5]
set zeroaxis

set term gif animate delay 10 
set output "genn01.gif"
do for [i=0:200] {
move = i*0.001
plot x<=L ? sin(w*move-k*x) : 0 lw 2 title "",\
x<=L ? -sin(w*move+k*x-2*k*L) : 0 lw 2 title "", \
x<=L ? sin(w*move-k*x-2*k*L) : 0 lw 2 title "", \
x<=L ? -sin(w*move+k*x-4*k*L) : 0 lw 2 title "", \
x<=L ? sin(w*move-k*x)-sin(w*move+k*x-2*k*L)+sin(w*move-k*x-2*k*L)-sin(w*move+k*x-4*k*L) : 0 lw 3 linecolor "red" title "" 
}
set output 
set terminal windows 

#plot sin(w*move-k*x), -sin(w*move+k*x-2*k*L), -sin(w*move-k*x-2*k*L), sin(w*move+k*x-4*k*L)
#replot sin(w*move-k*x)-sin(w*move+k*x-2*k*L)-sin(w*move-k*x-2*k*L)+sin(w*move+k*x-4*k*L)

