from serial import Serial
from serial.tools.list_ports import comports

import dataset
from simplejson import loads, JSONDecodeError

from procpy import Process, Queue
from runnable import Runnable

from sensor_gateway import log


class SerialReader(Runnable):
    _queue: Queue = None
    serial: Serial = None
    device_name: str = None
    helo: bytes = None

    def __init__(self, queue: Queue, serial: Serial, helo: bytes = b"AYE"):
        Runnable.__init__(self)
        self._queue = queue
        self.serial = serial
        self.helo = helo

    def get_device_name(self, helo: bytes) -> str:
        self.serial.write(helo)
        return self.serial.readline().strip(b"\r\n").decode("utf-8")

    def on_start(self):
        self.device_name = self.get_device_name(self.helo)
        log.debug("Going to read from: {}", self.device_name)

    def next_line_2_json(self):
        try:
            return loads(self.serial.readline().strip(b"\r\n"))
        except JSONDecodeError:
            return None

    def work(self):
        data = self.next_line_2_json()
        if data is not None:
            self._queue.put({"device": self.device_name, "data": data})


class SerialManager(Process):
    db: dataset.Database = None
    serial_devices: list[SerialReader] = []
    serial_queue: Queue = None

    def __init__(self, database_url: str):
        Process.__init__(self)
        self.db = dataset.connect(database_url)
        self.serial_queue = Queue()
        self.init_serial_devices()

    def init_serial_devices(self):
        ts = []
        for adp in comports():
            ad = adp.device
            if "USB" in ad:
                ts.append(ad)
        for s in ts:
            if "USB" in s:
                self.serial_devices.append(SerialReader(self.serial_queue, Serial(s)))

    def on_start(self):
        log.debug("Starting serial readers")
        for dev in self.serial_devices:
            dev.start()

    def on_stop(self):
        log.debug("Stopping serial readers")
        for dev in self.serial_devices:
            dev.stop()
            dev.join()

    def work(self):
        while not self.serial_queue.empty():
            item = self.serial_queue.get()
            log.debug(item)
            self.db[(item["device"])].insert(item["data"])
        self.sleep(0.4)
