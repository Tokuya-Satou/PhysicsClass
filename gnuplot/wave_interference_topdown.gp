# 波の干渉
# その2 波源を結ぶ線分のみみたい

s1=4
lambda = 2
flamerate = 50.0

f = 200/lambda
w=2*pi*f
k = 2*pi/lambda

set view 90,0, 1,1 

set size ratio 0.2

unset zeroaxis
set xrange [-10:10]
set yrange [0:0.1]
set zrange [-2:2]
set isosamples 100
set samples 1000
set pm3d depthorder
unset colorbox

set term gif animate delay 5 size 1280,960
set output "kansho03.gif"

#move=0
#splot sin(w*move-k*sqrt((x-s1)**2+y**2)) + sin(w*move-k*sqrt((x+s1)**2+y**2)) with pm3d title ""

do for [i=1:flamerate] {
move = i/(flamerate*f)
splot sin(w*move-k*sqrt((x-s1)**2+y**2)) - sin(w*move-k*sqrt((x+s1)**2+y**2)) with pm3d title ""
}

set output 
set terminal windows 
