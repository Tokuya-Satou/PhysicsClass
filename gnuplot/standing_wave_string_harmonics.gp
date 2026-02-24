# 弦の振動
# x=0で波発生 + 固定端 & x=Lで固定端

L = 10

lambda1 = 20.0/1
f1= 400/lambda1
w1=2*pi*f1
k1 = 2*pi/lambda1

lambda2 = 20.0/2
f2= 400/lambda2
w2=2*pi*f2
k2 = 2*pi/lambda2

lambda2 = 20.0/2
f2= 400/lambda2
w2=2*pi*f2
k2 = 2*pi/lambda2

lambda3 = 20.0/3
f3= 400/lambda3
w3=2*pi*f3
k3 = 2*pi/lambda3


set sample 1000
set xrange [-0.5:10.5]
set yrange [-4.5:4.5]
set zeroaxis

#set term gif animate delay 10 
#set output "genn01.gif"
do for [i=0:200] {
move = i*0.001
plot x<=L ? cos(w1*move-k1*L)*sin(-k1*x+k1*L)+cos(w2*move-k2*L)*sin(-k2*x+k2*L)+cos(w3*move-k3*L)*sin(-k3*x+k3*L) : 0 linecolor "red" title "" #,\
#x<=L ? cos(w1*move-k1*L)*sin(-k1*x+k1*L) : 0  title "" ,\
#x<=L ? cos(w2*move-k2*L)*sin(-k2*x+k2*L) : 0  title "" ,\
#x<=L ? cos(w3*move-k3*L)*sin(-k3*x+k3*L) : 0  title ""
}
#set output 
#set terminal windows 

#plot sin(w*move-k*x), -sin(w*move+k*x-2*k*L), -sin(w*move-k*x-2*k*L), sin(w*move+k*x-4*k*L)
#replot sin(w*move-k*x)-sin(w*move+k*x-2*k*L)-sin(w*move-k*x-2*k*L)+sin(w*move+k*x-4*k*L)

