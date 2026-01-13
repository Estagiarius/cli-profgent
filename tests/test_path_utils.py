
import pytest
import os
import sys
import platform
import subprocess
from pathlib import Path
from unittest.mock import patch, MagicMock
from app.utils.path_utils import open_file_in_os, get_resource_path

# --- Tests for open_file_in_os ---

def test_open_file_in_os_windows():
    """Test opening a file on Windows calls os.startfile."""
    with patch("platform.system", return_value="Windows"):
        # create=True is needed because os.startfile doesn't exist on Linux
        with patch("os.startfile", create=True) as mock_startfile:
            open_file_in_os("C:\\path\\to\\file.txt")
            mock_startfile.assert_called_once_with("C:\\path\\to\\file.txt")

def test_open_file_in_os_macos():
    """Test opening a file on MacOS calls open."""
    with patch("platform.system", return_value="Darwin"):
        with patch("subprocess.Popen") as mock_popen:
            open_file_in_os("/path/to/file.txt")
            mock_popen.assert_called_once_with(['open', '/path/to/file.txt'])

def test_open_file_in_os_linux():
    """Test opening a file on Linux calls xdg-open."""
    with patch("platform.system", return_value="Linux"):
        with patch("subprocess.Popen") as mock_popen:
            open_file_in_os("/path/to/file.txt")
            mock_popen.assert_called_once_with(['xdg-open', '/path/to/file.txt'])

# --- Tests for get_resource_path ---

def test_get_resource_path_dev_mode():
    """Test resolution in development mode (no _MEIPASS, no frozen)."""
    # Simulate standard environment
    if hasattr(sys, "_MEIPASS"):
        del sys._MEIPASS
    if hasattr(sys, "frozen"):
        del sys.frozen

    with patch("os.getcwd", return_value="/app"):
        result = get_resource_path("data/file.json")
        assert result == "/app/data/file.json"

def test_get_resource_path_pyinstaller_onefile():
    """Test resolution in PyInstaller --onefile mode."""
    with patch.object(sys, "_MEIPASS", "/tmp/_MEI12345", create=True):
         result = get_resource_path("data/file.json")
         assert result == "/tmp/_MEI12345/data/file.json"

def test_get_resource_path_pyinstaller_onedir():
    """Test resolution in PyInstaller --onedir mode."""
    # Ensure _MEIPASS is not set for this test
    if hasattr(sys, "_MEIPASS"):
        del sys._MEIPASS

    with patch.object(sys, "frozen", True, create=True):
        with patch.object(sys, "executable", "/app/dist/myapp/myapp.exe", create=True):
             # Parent of executable is /app/dist/myapp
             result = get_resource_path("data/file.json")
             # Use Path to handle separators correctly if we were on Windows vs Linux,
             # but here we are mocking strings mainly.
             # The function does: Path(sys.executable).parent / relative_path
             expected = str(Path("/app/dist/myapp/data/file.json"))
             assert result == expected
