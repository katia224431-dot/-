@echo off
chcp 65001 > nul
echo ======================================================================
echo  🧭 KNU 혜택 나침반 : 강원대 장학·비교과 맞춤 추천 웹 애플리케이션
echo ======================================================================
echo.
echo [1/2] 가상환경 및 Python 환경 확인 중...

REM 1순위: Anaconda Python
if exist "C:\ProgramData\anaconda3\python.exe" (
    echo Anaconda Python 감지됨: C:\ProgramData\anaconda3\python.exe
    set PYTHON_EXE=C:\ProgramData\anaconda3\python.exe
    goto RUN
)

REM 2순위: 로컬 .venv
if exist ".venv\bin\python.exe" (
    echo 로컬 가상환경 감지됨: .venv\bin\python.exe
    set PYTHON_EXE=.venv\bin\python.exe
    goto RUN
)

REM 기본 시스템 python
set PYTHON_EXE=python

:RUN
echo [2/2] Streamlit 서버 구동 중... 브라우저가 자동으로 열립니다.
echo 서비스 접속 주소: http://localhost:8501
echo 종료하려면 창을 닫거나 Ctrl+C를 누르세요.
echo.

"%PYTHON_EXE%" -m streamlit run app.py

pause
