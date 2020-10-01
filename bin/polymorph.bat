@echo off
REM Use Python to run the Polymorph script from the current directory, passing all parameters
title polymorph
"%~dp0..\python" "%~dp0\polymorph" %*
