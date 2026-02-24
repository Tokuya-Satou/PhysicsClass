# 波の干渉
# 

s1=4
lambda = 2
flamerate = 50.0

f = 200/lambda
w=2*pi*f
k = 2*pi/lambda

set view 5,25, 1,1 

unset zeroaxis
set xrange [-10:10]
set yrange [-10:10]
set isosamples 1000
set samples 1000
set pm3d depthorder
unset colorbox

set term gif animate delay 5 size 1280,960
set output "kansho02-2.gif"

#move=0
#splot sin(w*move-k*sqrt((x-s1)**2+y**2)) + sin(w*move-k*sqrt((x+s1)**2+y**2)) with pm3d title ""

do for [i=1:flamerate] {
move = i/(flamerate*f)
splot sin(w*move-k*sqrt((x-s1)**2+y**2)) - sin(w*move-k*sqrt((x+s1)**2+y**2)) with pm3d title ""
}

set output 
set terminal windows 
