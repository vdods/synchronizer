import threading

class ValueContainer (object):
    """This class exists to simulate being having a reference to any value, e.g. an int."""
    def __init__ (self, initial_value=None):
        self.value = initial_value

# From `Macke` at http://stackoverflow.com/questions/3462566/python-elegant-way-to-deal-with-lock-on-a-variable
class LockedObject (object):
    def __init__ (self, initial_value=None):
        self.__is_locked = False
        self.__lock = threading.RLock()
        self.__value_container = ValueContainer(initial_value)

    def is_locked (self):
        return self.__is_locked

    def acquire_assign_and_release (self, value):
        with self as value_container:
            value_container.value = value

    def release (self):
        self.__locked = False
        self.__lock.release()

    def __enter__ (self):
        self.__lock.__enter__()
        self.__is_locked = True
        return self.__value_container

    def __exit__ (self, *args, **kwargs):
        if self.__is_locked:
            self.__is_locked = False
            return self.__lock.__exit__(*args, **kwargs)

if __name__ == '__main__':
    import sys
    import time

    def log (message, *args):
        sys.stdout.write(message.format(*args))

    # Run some tests

    if True:
        x = LockedObject(3)
        with x as y:
            log('y.value = {0}\n', y.value)
            y.value += 10
            log('y.value = {0}\n', y.value)

        x.acquire_assign_and_release(100)

        with x as y:
            log('y.value = {0}\n', y.value)
            y.value += 13
            log('y.value = {0}\n', y.value)

    # Multi-threaded tests

    def run_thread (thread_name, value_increment, sleep_duration, x):
        while True:
            with x as y:
                log('in thread {0}: y.value = {1}; incrementing by {2}.\n', thread_name, y.value, value_increment)
                y.value += value_increment
                log('in thread {0}; sleeping for {1} seconds before releasing x.\n', thread_name, sleep_duration)
                time.sleep(sleep_duration)
            # Give the other thread(s) a chance to acquire the lock.
            time.sleep(0.1)

    # The program exits once all non-daemon threads are dead.

    t = threading.Thread(target=run_thread, name='thread a', args=('thread a', 11, 2.0, x))
    t.daemon = True
    t.start()

    t = threading.Thread(target=run_thread, name='thread b', args=('thread b', 13, 3.1, x))
    t.daemon = True
    t.start()

    try:
        # Only run for 60 seconds
        time.sleep(20.0)
    except KeyboardInterrupt:
        pass

    sys.exit(0)
