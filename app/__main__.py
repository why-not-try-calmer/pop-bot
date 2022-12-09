import logging
from threading import Thread

import cherrypy

from app import config
from app.funcs import get_chatid, get_cmd, reply
from app.worker import Query, consume, queue

logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.DEBUG)


class Webhook:
    @cherrypy.expose()
    @cherrypy.tools.json_in()  # type: ignore
    @cherrypy.tools.json_out()  # type: ignore
    def pop(self, rec_termination: str):
        if rec_termination != config.endpoint_termination:
            return 404

        update = cherrypy.request.json

        if chat_id := get_chatid(update):
            try:
                if cmd := get_cmd(update):
                    query = Query(cmd=cmd, chat_id=chat_id)
                    queue.put_nowait(query)
                    logging.info("Enqueued.")
                else:
                    error = f"No valid command for {update}"
                    reply(Query(error=error, chat_id=chat_id))
                    logging.info(error)
            except Exception as error:
                reply(Query(error=error, chat_id=chat_id))
                logging.info(f"Exception: {error}")
            finally:
                return 200


def main():
    worker = Thread(target=consume, args=(queue,))
    worker.start()

    global_config = {"server.socket_host": "0.0.0.0", "server.socket_port": config.port}
    cherrypy.config.update(global_config)
    cherrypy.quickstart(Webhook())


if __name__ == "__main__":
    main()
