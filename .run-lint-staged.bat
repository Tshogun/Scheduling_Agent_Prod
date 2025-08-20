@echo off
cd frontend || exit /b 1
npm exec lint-staged
