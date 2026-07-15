"""Tests for the subprocess wrapper error handling."""
import subprocess
from pathlib import Path
from unittest import mock

import pytest

import graphcal
from graphcal import (
    GraphcalCheckError,
    GraphcalError,
    GraphcalEvaluationError,
    Override,
)


class TestEvalErrorWrapping:
    def test_subprocess_failure_is_wrapped_with_context(self):
        failure = subprocess.CalledProcessError(
            returncode=1,
            cmd=["graphcal"],
            output="partial stdout",
            stderr="assertion failed: fuel_budget",
        )

        with mock.patch("graphcal.cli.subprocess.run", side_effect=failure):
            with pytest.raises(GraphcalEvaluationError) as excinfo:
                graphcal.eval(
                    "model.gcl",
                    overrides=[Override.time("isp", 320.0, "s")],
                )

        error = excinfo.value
        assert error.returncode == 1
        assert error.stdout == "partial stdout"
        assert error.stderr == "assertion failed: fuel_budget"
        assert error.file == Path("model.gcl")
        assert error.overrides == {"isp": "320.0 s"}
        assert list(error.command) == [
            "graphcal",
            "eval",
            "--format",
            "json",
            "model.gcl",
            "--set",
            "isp=320.0 s",
        ]

    def test_successful_eval_parses_json_stdout(self):
        completed = subprocess.CompletedProcess(
            args=["graphcal"],
            returncode=0,
            stdout='{"node": {"delta_v": {"si_value": 1.0, "unit": "m/s"}}}',
            stderr="",
        )

        with mock.patch("graphcal.cli.subprocess.run", return_value=completed) as run:
            result = graphcal.eval_file("model.gcl", overrides={"isp": "320.0 s"})

        assert result.node("delta_v").si_value == 1.0
        assert run.call_args.args[0] == [
            "graphcal",
            "eval",
            "--format",
            "json",
            "model.gcl",
            "--set",
            "isp=320.0 s",
        ]


class TestInvalidJson:
    def test_non_json_stdout_raises_graphcal_error(self):
        completed = subprocess.CompletedProcess(
            args=["graphcal"], returncode=0, stdout="not json", stderr=""
        )

        with mock.patch("graphcal.cli.subprocess.run", return_value=completed):
            with pytest.raises(GraphcalError):
                graphcal.eval_file("model.gcl")


class TestCheckErrorWrapping:
    def test_check_failure_is_wrapped(self):
        failure = subprocess.CalledProcessError(
            returncode=1,
            cmd=["graphcal"],
            output="",
            stderr="dimension mismatch",
        )

        with mock.patch("graphcal.cli.subprocess.run", side_effect=failure):
            with pytest.raises(GraphcalCheckError) as excinfo:
                graphcal.check("model.gcl")

        error = excinfo.value
        assert error.returncode == 1
        assert error.stderr == "dimension mismatch"
        assert list(error.command) == ["graphcal", "check", "model.gcl"]
