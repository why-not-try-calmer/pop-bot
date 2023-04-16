from time import sleep
from timeit import default_timer

from app.io import safe_reply
from app.types import Cmd, Query


def to_error(cmd: str, service: str, allowed) -> str:
    return f"This {service} command or executable is not allowed: {cmd}. Allowed {service} commands are: {', '.join(allowed)}."


commands = {"r": Cmd(1), "run": Cmd(1), "help": Cmd(2), "start": Cmd(2)}


def slice_on_n(s: str, n=4096, acc=None) -> list[str]:
    if acc is None:
        acc = []

    if len(s) <= n:
        acc.append(s)
        return acc

    sli = s[:n]
    before_after = sli.rsplit("\n", 1)
    acc.append(before_after[0])

    return slice_on_n(
        (before_after[1] + s[n:] if len(before_after) == 2 else s[n:]),
        n,
        acc,
    )


def parse_query(update: dict) -> None | Query:
    chat_id = None
    text = None

    if message := update.get("message"):
        if any(
            k in message or k in update
            for k in ["reply_to_message", "callback_query", "edited_message"]
        ):
            return

        text = message.get("text")
        if chat := message.get("chat"):
            chat_id = chat.get("id")

    if not (chat_id and text):
        return

    splitted = text.split(" ", 1)
    head = splitted[0][1:]
    cmd = head.split("@")[0]

    if cmd in commands:

        match commands[cmd]:
            case Cmd.RUN:
                if len(splitted) == 1:
                    error = "Your command has no argument or parameter."
                    return Query(chat_id=chat_id, error=error, input=text)
                else:
                    return Query(
                        started=default_timer(),
                        input=splitted[1],
                        chat_id=chat_id,
                        cmd_type=commands[cmd],
                    )
            case Cmd.HELP:
                return Query(
                    started=default_timer(),
                    input=text,
                    chat_id=chat_id,
                    cmd_type=commands[cmd],
                )

            case _:
                return
    else:
        error = f"Unable to match your message with any command: {text}"
        return Query(chat_id=chat_id, error=error, input=text)


def as_block(text: str) -> str:
    return f"```\n{text.strip()}\n```"


def as_text(query) -> str:
    if "result" in query:
        return f"Command: `{query.input}`. Result:\n{query.result}"
    elif "error" in query:
        return f"Command: `{query.input}`. Error:\n{query.error}"
    else:
        return "Missing 'result' or 'error'"


def reply(query: Query):
    perf_report = (
        f"Handled and processed in {round(default_timer() - query.started,2)}s.\n"
        if "started" in query
        else ""
    )
    payload = {
        "chat_id": query.chat_id,
        "parse_mode": "Markdown",
        "text": perf_report,
    }
    slices = slice_on_n(as_text(query))

    match len(slices):
        case 0:
            raise ValueError(
                f"No message could be constructed from this command: {query.args}"
            )
        case 1:
            payload["text"] += as_block(slices[0])
            safe_reply(payload)
        case _:
            warning = "The response is too large. Trimming down to 2 or 3 messages..."
            payload["text"] += warning
            trimmed_down = slices[:3]
            safe_reply(payload)

            for i, sli in enumerate(trimmed_down):
                payload["text"] = f"{i+1}/{len(trimmed_down)}\n\n{as_block(sli)}"
                safe_reply(payload)
                sleep(0.2)
