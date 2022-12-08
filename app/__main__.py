import cherrypy
import logging

from app.proc import parse_validate, run_in_sub
from app.funcs import get_cmd, reply
from app import config

logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.DEBUG)


class Webhook:
    @cherrypy.expose()
    @cherrypy.tools.json_in()  # type: ignore
    @cherrypy.tools.json_out()  # type: ignore
    def pop(self, rec_termination: str):
        if rec_termination != config.endpoint_termination:
            return 404

        update = cherrypy.request.json

        try:
            if cmd := get_cmd(update):
                args = parse_validate(cmd)
                res = run_in_sub(cmd, args)
                reply(update, res)
                logging.info(f"Ok")
            else:
                reply(
                    update,
                    "Unable to find any command in what you sent.",
                )
                logging.info(f"No valid command")

        except Exception as error:
            logging.info(f"Exception: {error}")
            reply(update, str(error).strip())

        finally:
            return 200


def main():
    global_config = {"server.socket_host": "0.0.0.0", "server.socket_port": config.port}
    cherrypy.config.update(global_config)
    cherrypy.quickstart(Webhook())


if __name__ == "__main__":
    main()
