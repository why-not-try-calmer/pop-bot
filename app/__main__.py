from os import environ

import cherrypy

from app.proc import parse_validate, run_in_sub

token = environ["TOKEN"]
port = int(environ.get("PORT", "8000"))
termination = f"bot{token}"


class Webhook:
    @cherrypy.expose()
    @cherrypy.tools.json_in()  # type: ignore
    @cherrypy.tools.json_out()  # type: ignore
    def pop_bot(self, rec_termination: str):
        if rec_termination != termination:
            return 404

        try:
            cmd = cherrypy.request.json["cmd"]
            args = parse_validate(cmd)
            res = run_in_sub(cmd, args)
            result_msg = "results" if isinstance(res, list) else "result"
            return {result_msg: res}
        except Exception as error:
            return {"error": str(error)}


if __name__ == "__main__":
    config = {"server.socket_host": "0.0.0.0", "server.socket_port": port}
    cherrypy.config.update(config)
    cherrypy.quickstart(Webhook())
