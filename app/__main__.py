from os import environ

import cherrypy
from app.proc import parse_validate, run_in_sub


class Webhook:
    @cherrypy.expose
    @cherrypy.tools.json_in()   # type: ignore
    def pop_bot(self):
        data = cherrypy.request.json
        try:
            cmd = data["cmd"]
            args = parse_validate(cmd)
            res = run_in_sub(cmd, args)
            return {"res": res}
        except Exception as error:
            return error


if __name__ == "__main__":
    token = environ["TOKEN"]
    port = int(environ.get("PORT", "8000"))
    endpoint = f"/pop_bot/bot{token}"
    config = {endpoint: {"server.socket_port": port}}
    cherrypy.quickstart(Webhook(), endpoint, config=config)
