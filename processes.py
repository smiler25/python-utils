from multiprocessing import Process, Queue

SENTINEL = repr(object())


def _worker(func, input_queue, output_queue, error_queue):
    for one in iter(input_queue.get, SENTINEL):
        try:
            output_queue.put(func(one))
        except Exception as e:
            error_queue.put((one, e))
    output_queue.put(SENTINEL)
    error_queue.put(SENTINEL)


def _worker_unzip(func, input_queue, output_queue, error_queue):
    for one in iter(input_queue.get, SENTINEL):
        try:
            output_queue.put(func(*one))
        except Exception as e:
            error_queue.put((one, e))
    output_queue.put(SENTINEL)
    error_queue.put(SENTINEL)


def iter_with_queues(iterator, function, simple_arg=True, num_processes=2):
    """
    Applies function to each element in iterator using multiprocessing queues
    :param iterator: iterable
    :param function: callable that accepts as parameter(s) iterator element and returns result
    :param simple_arg: if False then args unzip is used
    :param num_processes: number of workers
    :return: list, list - two lists with results and error elements
    """
    task_queue = Queue()
    done_queue = Queue()
    error_queue = Queue()
    processes = []
    worker = _worker if simple_arg else _worker_unzip
    for i in range(num_processes):
        p = Process(target=worker, args=(function, task_queue, done_queue, error_queue))
        p.start()
        processes.append(p)
    for one in iterator:
        task_queue.put(one)
    for _ in range(num_processes):
        task_queue.put(SENTINEL)
    result = []
    for _ in range(num_processes):
        result.extend([one for one in iter(done_queue.get, SENTINEL)])
    errors = []
    for _ in range(num_processes):
        errors.extend([one for one in iter(error_queue.get, SENTINEL)])
    for p in processes:
        p.join(5)
    return result, errors
