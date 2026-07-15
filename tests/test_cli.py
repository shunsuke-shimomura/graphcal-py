"""Tests for the subprocess wrapper error handling."""
import subprocess
import unittest
from pathlib import Path
from unittest import mock

import graphcal
from graphcal import (
    GraphcalCheckError,
    GraphcalError,
    GraphcalEvaluationError,
    Override,
)


class EvalErrorWrappingTest(unittest.TestCase):
    def test_subprocess_failure_is_wrapped_with_context(self):
        failure = subprocess.CalledProcessError(
            returncode=1,
            cmd=["graphcal"],
            output="partial stdout",
            stderr="assertion failed: fuel_budget",
        )

        with mock.patch("graphcal.cli.subprocess.run", side_effect=failure):
            with self.assertRaises(GraphcalEvaluationError) as ctx:
                graphcal.eval(
                    "model.gcl",
                    overrides=[Override.time("isp", 320.0, "s")],
                )

        error = ctx.exception
        self.assertEqual(error.returncode, 1)
        self.assertEqual(error.stdout, "partial stdout")
        self.assertEqual(error.stderr, "assertion failed: fuel_budget")
        self.assertEqual(error.file, Path("model.gcl"))
        self.assertEqual(error.overrides, {"isp": "320.0 s"})
        self.assertEqual(
            list(error.command),
            [
                "graphcal",
                "eval",
                "--format",
                "json",
                "model.gcl",
                "--set",
                "isp=320.0 s",
            ],
        )

    def test_successful_eval_parses_json_stdout(self):
        completed = subprocess.CompletedProcess(
            args=["graphcal"],
            returncode=0,
            stdout='{"node": {"delta_v": {"si_value": 1.0, "unit": "m/s"}}}',
            stderr="",
        )

        with mock.patch(
            "graphcal.cli.subprocess.run", return_value=completed
        ) as run:
            result = graphcal.eval_file("model.gcl", overrides={"isp": "320.0 s"})

        self.assertEqual(result.node("delta_v").si_value, 1.0)
        self.assertEqual(
            run.call_args.args[0],
            [
                "graphcal",
                "eval",
                "--format",
                "json",
                "model.gcl",
                "--set",
                "isp=320.0 s",
            ],
        )


class InvalidJsonTest(unittest.TestCase):
    def test_non_json_stdout_raises_graphcal_error(self):
        completed = subprocess.CompletedProcess(
            args=["graphcal"], returncode=0, stdout="not json", stderr=""
        )

        with mock.patch("graphcal.cli.subprocess.run", return_value=completed):
            with self.assertRaises(GraphcalError):
                graphcal.eval_file("model.gcl")


class CheckErrorWrappingTest(unittest.TestCase):
    def test_check_failure_is_wrapped(self):
        failure = subprocess.CalledProcessError(
            returncode=1,
            cmd=["graphcal"],
            output="",
            stderr="dimension mismatch",
        )

        with mock.patch("graphcal.cli.subprocess.run", side_effect=failure):
            with self.assertRaises(GraphcalCheckError) as ctx:
                graphcal.check("model.gcl")

        error = ctx.exception
        self.assertEqual(error.returncode, 1)
        self.assertEqual(error.stderr, "dimension mismatch")
        self.assertEqual(list(error.command), ["graphcal", "check", "model.gcl"])


if __name__ == "__main__":
    unittest.main()
