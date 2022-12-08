def raise_error(cmd: str, service: str, allowed: list[str]) -> str:
    raise ValueError(
        f"This {service.upper()} command is not allowed: {cmd}. Allowed {service} commands are: {', '.join(allowed)}"
    )


commands = ["r", "run"]


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
