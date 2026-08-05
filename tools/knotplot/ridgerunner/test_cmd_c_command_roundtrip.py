#!/usr/bin/env python3
"""Round-trip smoke for cmd_c_command → .cmd argv."""

from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

from run_ideal_knot import cmd_c_command


class TestCmdCCommandRoundtrip(unittest.TestCase):
    def test_ns_comma_list_stays_one_arg(self) -> None:
        d = Path(tempfile.mkdtemp())
        echo = d / "echo_args.cmd"
        echo.write_text(
            "@echo off\r\n"
            "echo ARG1=%~1\r\n"
            "echo ARG2=%~2\r\n"
            "echo ARG3=%~3\r\n"
            "echo ARG4=%~4\r\n",
            encoding="utf-8",
        )
        cmdline = cmd_c_command(
            echo, "p300.txt", "--ns=600,900", "--Threads=10"
        )
        proc = subprocess.run(cmdline, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stderr or proc.stdout)
        out = proc.stdout.replace("\r\n", "\n")
        self.assertIn("ARG1=p300.txt", out)
        self.assertIn("ARG2=--ns=600,900", out)
        self.assertIn("ARG3=--Threads=10", out)
        self.assertIn("ARG4=", out)


if __name__ == "__main__":
    unittest.main()
