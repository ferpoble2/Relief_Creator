from multiprocessing import Process, Queue
import time


# noinspection PyMissingOrEmptyDocstring
def f(q):
    time.sleep(1.5)
    # q.put([42, None, 'hello'])
    q.put(None)


if __name__ == '__main__':
    q = Queue()
    p = Process(target=f, args=(q,))
    p.start()
    print('process started')

    while True:

        # noinspection PyBroadException
        try:
            queue = q.get(False)
            print(queue)
            break
        except:
            print('nothing to report')
            pass

    p.join()
