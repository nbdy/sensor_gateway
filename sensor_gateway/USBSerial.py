from serial import Serial, SerialException
from serial.tools.list_ports import comports
from datetime import datetime

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

    def __init__(self, queue: Queue, serial: Serial):
        Runnable.__init__(self)
        self._queue = queue
        self.serial = serial

    def next_line_2_json(self):
        try:
            return loads(self.serial.readline().strip(b"\r\n"))
        except JSONDecodeError:
            pass
        except UnicodeDecodeError:
            pass
        except SerialException:
            log.debug("Lost connection. Stopping.")
            self.stop()
        return None

    def work(self):
        data = self.next_line_2_json()
        if data is not None:
            self._queue.put(data)


class SerialManager(Process):
    db: dataset.Database = None
    serial_devices: list = []
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
            device_name = item["device"]
            del item["device"]
            item["last_updated"] = datetime.now()
            log.debug(item)
            self.db[device_name].insert(item)
        self.sleep(0.4)
