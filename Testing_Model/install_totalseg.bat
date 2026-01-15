@echo off
echo ============================================================
echo Installing TotalSegmentator and Dependencies
echo ============================================================
echo.

echo [1/2] Installing TotalSegmentator...
pip install TotalSegmentator

echo.
echo [2/2] Verifying installation...
python -c "from totalsegmentator.python_api import totalsegmentator; print('[OK] TotalSegmentator installed successfully!')"

echo.
echo ============================================================
echo Installation Complete!
echo ============================================================
echo.
echo Next steps:
echo 1. cd Testing_Model
echo 2. python test_pancreas_detection_totalseg.py
echo.
echo Note: First run will download models (~1.5GB)
echo.
pause
