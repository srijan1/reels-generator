"""
Utility to configure FFMPEG path for the current Python process.
"""
import os
import shutil

FFMPEG_CUSTOM_BIN_PATH = r"C:\ffmpeg\bin"  # Raw string for Windows paths

def ensure_ffmpeg_in_path():
    """
    Checks for FFMPEG in a predefined custom path and adds it to os.environ["PATH"]
    for the current Python process if not already present.
    Also verifies if ffmpeg is then findable by shutil.which.
    """
    if os.path.isdir(FFMPEG_CUSTOM_BIN_PATH):
        current_paths = os.environ.get("PATH", "").split(os.pathsep)
        if FFMPEG_CUSTOM_BIN_PATH not in current_paths:
            os.environ["PATH"] = FFMPEG_CUSTOM_BIN_PATH + os.pathsep + os.environ.get("PATH", "")
            print(f"INFO: Added '{FFMPEG_CUSTOM_BIN_PATH}' to the beginning of PATH for this session.")
        else:
            print(f"INFO: '{FFMPEG_CUSTOM_BIN_PATH}' is already in PATH.")
    else:
        print(f"WARNING: Custom FFMPEG directory '{FFMPEG_CUSTOM_BIN_PATH}' not found.")

    ffmpeg_exe = shutil.which("ffmpeg")
    if ffmpeg_exe:
        print(f"INFO: ffmpeg executable found by shutil.which: {ffmpeg_exe}")
    else:
        print(f"WARNING: ffmpeg executable NOT found by shutil.which. Ensure FFMPEG is installed and correctly added to system PATH or the custom path above is correct.")