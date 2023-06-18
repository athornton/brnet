import subprocess
from typing import Optional, List
from logging import Logger

def run(args: List[str], logger: Optional[Logger] = None) -> None:
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
