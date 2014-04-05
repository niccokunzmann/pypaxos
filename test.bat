@echo off

py.test-3.3 %* > test.out
edit test.out