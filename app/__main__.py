import cherrypy

from app.proc import parse_validate, run_in_sub
from app.funcs import get_cmd
from app import config


class Webhook:
    @cherrypy.expose()
    @cherrypy.tools.json_in()  # type: ignore
    @cherrypy.tools.json_out()  # type: ignore
    def pop(self, rec_termination: str):
        if rec_termination != config.endpoint_termination:
            return 404

        try:
            update = cherrypy.request.json

            if cmd := get_cmd(update):
                args = parse_validate(cmd)
                res = run_in_sub(cmd, args)
                result_msg = "results" if isinstance(res, list) else "result"
                return {result_msg: res}

            else:
                return 200

        except Exception as error:
            return {"error": str(error).strip()}


def main():
    global_config = {"server.socket_host": "0.0.0.0", "server.socket_port": config.port}
    cherrypy.config.update(global_config)
    cherrypy.quickstart(Webhook())


if __name__ == "__main__":
    main()
