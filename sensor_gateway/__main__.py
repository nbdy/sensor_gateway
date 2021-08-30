from time import sleep
from argparse import ArgumentParser

from sensor_gateway import log
from sensor_gateway.USBSerial import SerialManager
from sensor_gateway.API import API


def build_database_uri(username: str, password: str, host: str, port: int, database: str):
    return f"postgresql://{username}:{password}@{host}:{port}/{database}"


def parse_args():
    log.debug("Parsing arguments")
    ap = ArgumentParser()
    ap.add_argument("-d", "--database", help="PostgreSQL database to use", default="sensor_gateway")
    ap.add_argument("-du", "--database-user", help="PostgreSQL database username", default="postgres")
    ap.add_argument("-dp", "--database-pass", help="Password for database-user", default="postgres")
    return ap.parse_args()


def start_processes(procs: list):
    log.debug("Starting processes")
    for proc in procs:
        proc.start()


def wait_for_ctrl_c():
    try:
        while True:
            sleep(500)
    except KeyboardInterrupt:
        log.info("Caught CTRL+C. Stopping.")
        pass


def stop_processes(procs: list):
    log.debug("Stopping processes")
    for proc in procs:
        proc.stop()
    log.debug("Joining processes")
    for proc in procs:
        proc.join()


def main():
    a = parse_args()
    db_uri = build_database_uri(a.database_user, a.database_pass, "127.0.0.1", 5432, a.database)
    log.debug("Initializing processes")
    processes = [SerialManager(db_uri), API(db_uri)]
    start_processes(processes)
    wait_for_ctrl_c()
    stop_processes(processes)
    log.info("Exiting")


if __name__ == '__main__':
    main()
