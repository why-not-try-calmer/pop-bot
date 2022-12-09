from app import config


def raise_error(cmd: str, service: str, allowed: list[str]) -> str:
    raise ValueError(
        f"This {service.upper()} command is not allowed: {cmd}. Allowed {service} commands are: {', '.join(allowed)}"
    )


commands = ["r", "run"]


def slice_on_4096(_input: list[str] | str, last="", acc=[]) -> list[str]:
    too_long = lambda s: len(s) > 4096

    if isinstance(_input, str):
        if too_long(_input):
            _input = _input.split("\n")
        else:
            return [_input]

    if not _input:
        acc.append(last)
        return acc

    head, tail = _input[0], _input[1:]
    joined = "\n".join([last, head])

    if too_long(joined):
        acc.append(last)
        return slice_on_4096(tail, head, acc)
    else:
        return slice_on_4096(tail, joined, acc)


def get_cmd(update: dict) -> None | str:
    if message := update.get("message"):
        if text := message.get("text"):
            splitted = text.split(" ", 1)
            if len(splitted) < 2:
                raise ValueError(
                    "Your command to the bot lacks needs arguments/parameters."
                )
            cmd, tail = splitted[0][1:], splitted[1]

            match next(filter(lambda w: cmd == w, commands), None):
                case "r":
                    return tail
                case "run":
                    return tail
                case _:
                    raise_error(cmd, "bot", commands)


def get_chatid(update: dict) -> None | int:
    if message := update.get("message"):
        if chat := message.get("chat"):
            if _id := chat.get("id"):
                return _id


def as_block(text: str) -> str:
    return f"```\n{text.strip()}\n```"


def from_query(query) -> str:
    if "result" in query:
        return f"Command: `{query['cmd']}`. Result:\n{query['result']}"
    else:
        return f"Command: `{query['cmd']}`. Error:\n{query['error']}"


def reply(query):
    payload = {"chat_id": query["chat_id"], "parse_mode": "Markdown"}
    url = f"https://api.telegram.org/bot{config.token}/sendMessage"
    slices = slice_on_4096(from_query(query))

    if not slices:
        raise ValueError(
            f"No message could be constructed from this command: {query['cmd']}"
        )

    l = len(slices)

    if l == 1:
        payload["text"] = as_block(slices[0])
        config.session.post(url, json=payload)

    else:
        warning = "The response is too large. Trimming down to 2 or 3 messages..."
        payload["text"] = warning
        config.session.post(url, json=payload)

        for i, sli in enumerate(slices[:3]):
            payload["text"] = f"{i+1}/{l}\n\n{as_block(sli)}"
            config.session.post(url, json=payload)
