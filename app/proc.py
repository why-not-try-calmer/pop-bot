import subprocess

allowed_0 = [
    "apt",
    "cat",
    "cd",
    "ls",
    "echo",
    "find",
    "grep",
    "head",
    "history",
    "info",
    "less",
    "locate",
    "man",
    "more",
    "tail",
    "wc",
    "whereis",
    "which",
]

allowed_apt_1 = ["info", "list", "search", "show"]


def parse_validate(cmd: str) -> list[str]:
    args = cmd.split(" ")

    if not args[0] in allowed_0:
        raise ValueError(
            f"This BASH command is not allowed: {args[0]}. Allowed BASH commands are: {','.join(allowed_0)}"
        )

    if args[0] == "apt":
        if not args[1] in allowed_apt_1:
            raise ValueError(
                f"This APT command is not allowed: {args[1]}. Allowed APT commands are: {','.join(allowed_apt_1)}"
            )

    return args


def run_in_sub(cmd: str, args: list[str]) -> str:
    try:
        res = subprocess.run(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=3,
            universal_newlines=True,
        )
        if res.returncode != 0:
            raise Exception(f"Failed! Errors: {res.stderr}, Output: {res.stdout}")
        else:
            return res.stdout
    except TimeoutError:
        return f"Timed out: {cmd}"
