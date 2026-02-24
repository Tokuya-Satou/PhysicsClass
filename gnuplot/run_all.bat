@echo off
for %%f in (*.gp) do (
    echo Running %%f...
    gnuplot %%f
)
