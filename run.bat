@echo off
:: Executa o módulo uvicorn diretamente usando o Python da VENV
.\.venv\Scripts\python.exe -m uvicorn main:app --reload
pause