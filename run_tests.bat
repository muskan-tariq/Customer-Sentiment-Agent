@echo off
REM Test runner script for Windows

echo Running integration tests...
pytest tests/ -v

echo.
echo Tests completed!
pause

