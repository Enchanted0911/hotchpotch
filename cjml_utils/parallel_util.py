import multiprocessing.dummy as parallel


def parallel_process(process, path_list):
    pool = parallel.Pool(12)
    pool.map(process, path_list)
    pool.close()
    pool.join()
