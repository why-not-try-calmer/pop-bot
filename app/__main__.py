import logging
from threading import Thread

import cherrypy

from app import config, cons_queue, proc_queue
from app.funcs import parse_query, reply
from app.workers import consume, process


class Webhook:
    @cherrypy.expose()
    @cherrypy.tools.json_in()  # type: ignore
    @cherrypy.tools.json_out()  # type: ignore
    def pop(self, rec_termination: str):
        if rec_termination != config.endpoint_termination:
            return 404
        update = cherrypy.request.json
        if query := parse_query(update):
            try:
                if "error" in query:
                    reply(query)
                    logging.info(f"Invalid query: {query}")
                else:
                    proc_queue.put_nowait(query)
                    logging.info(f"Enqueuing process_q: {query}")
            except Exception as error:
                query.error = str(error)
                reply(query)
        return 200


def start_workers(daemon=True):
    proc_worker = Thread(target=process, args=(proc_queue, cons_queue), daemon=daemon)
    cons_worker = Thread(target=consume, args=(cons_queue,), daemon=daemon)
    cons_worker.start()
    proc_worker.start()


def main():
    start_workers()
    global_config = {
        "server.socket_host": "0.0.0.0",
        "server.socket_port": config.port,
        "environment": "production",
    }
    cherrypy.config.update(global_config)
    cherrypy.quickstart(Webhook())


if __name__ == "__main__":
    main()
