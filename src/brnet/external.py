import json
import subprocess
from logging import Logger
from typing import Any, List, Optional


def run(
    args: List[str], logger: Optional[Logger] = None
) -> subprocess.CompletedProcess:
    argstr = " ".join(args)
    if logger:
        logger.info(f"Running command '{argstr}'")
    proc = subprocess.run(args, capture_output=True)
    if proc.returncode != 0:
        if logger:
            logger.warning(
                f"Command '{argstr}' failed: rc {proc.returncode}\n"
                + f" -> stdout: {proc.stdout.decode()}\n"
                f" -> stderr: {proc.stderr.decode()}"
            )
    else:
        if logger:
            logger.debug(
                f"Command '{argstr}' succeeded\n"
                + f" -> stdout: {proc.stdout.decode()}\n"
                f" -> stderr: {proc.stderr.decode()}"
            )
    return proc


def run_and_decode(args: List[str], logger: Optional[Logger] = None) -> Any:
    proc = run(args, logger)
    if proc.returncode != 0:
        raise RuntimeError(f"cmd {args} returned {proc.returncode}")
    std = proc.stdout.decode()
    return json.loads(std)
