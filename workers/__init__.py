"""
Workers - Automation Pipeline
"""

import subprocess
import sys
import os


def run_automation_pipeline():
    """
    Run full automation pipeline in a SEPARATE Python process.
    This avoids Playwright's incompatibility with Streamlit's event loop on Windows.
    """
    script = """
import sys
import os
sys.path.insert(0, {base_dir!r})

from workers.booking_automation import automation_step_1_bookings, automation_step_2_teams, automation_step_3_merge

try:
    automation_step_1_bookings()
    automation_step_2_teams()
    automation_step_3_merge()
    print("[SUCCESS] All 3 steps completed.")
except Exception as e:
    print(f"[ERROR] {{type(e).__name__}}: {{e}}")
    import traceback
    traceback.print_exc()
""".format(base_dir=os.getcwd())

    try:
        result = subprocess.run(
            [sys.executable, "-c", script],
            capture_output=True,
            text=True,
            timeout=600,
            cwd=os.getcwd(),
        )
        stdout = result.stdout
        stderr = result.stderr

        if result.returncode == 0 and "SUCCESS" in stdout:
            return {"ok": True, "stdout": stdout, "stderr": stderr}

        return {"ok": False, "stdout": stdout, "stderr": stderr or stdout}

    except subprocess.TimeoutExpired:
        return {"ok": False, "stdout": "", "stderr": "⏰ Pipeline timed out after 10 minutes."}
    except Exception as e:
        return {"ok": False, "stdout": "", "stderr": str(e)}