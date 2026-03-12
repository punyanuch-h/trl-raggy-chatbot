@echo off
set "timestamp=%date:/=-%_%time::=-%"
set "timestamp=%timestamp: =0%"
set "timestamp=%timestamp:.=-%"
set "logfile=SI\05_Test_Reports\test_log_%timestamp%.txt"

echo [DoD Script] Running pytest strictly enforced by ISO 29110 Protocol...
call .\.venv\Scripts\pytest.exe tests\ > "%logfile%" 2>&1
echo [DoD Script] Tests completed. 
echo [DoD Script] Execution output exported to: %logfile%

