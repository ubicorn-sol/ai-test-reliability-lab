import subprocess
import sys
import xml.etree.ElementTree as ET

import pytest


@pytest.mark.parametrize(
    ("assertion", "exit_code", "failures"),
    [("assert True", 0, "0"), ("assert False", 1, "1")],
    ids=["successful-run", "failed-run"],
)
def test_runner_exit_status_and_report(tmp_path, assertion, exit_code, failures):
    test_file = tmp_path / "test_example.py"
    test_file.write_text(f"def test_example():\n    {assertion}\n", encoding="utf-8")
    report = tmp_path / "results.xml"

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "-q",
            "--junitxml",
            str(report),
            str(test_file),
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        timeout=30,
    )

    assert result.returncode == exit_code, result.stdout + result.stderr
    suite = ET.parse(report).getroot().find("testsuite")
    assert suite is not None
    assert suite.attrib["tests"] == "1"
    assert suite.attrib["failures"] == failures
