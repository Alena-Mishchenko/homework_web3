import logging
from multiprocessing import Pool, Process,current_process,cpu_count
from time import  ctime, time

logger = logging.getLogger()
stream_handler = logging.StreamHandler()
logger.addHandler(stream_handler)
logger.setLevel(logging.DEBUG)

def is_prime(n):
    if n < 2:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True

def factorize(*numbers):
    start_time = time()
    logging.debug(f'Start : {ctime()}')
    result = []
    for number in numbers:
        if number <= 0:
            raise ValueError("Numbers must be positive")
        factors = [i for i in range(1, number + 1) if number % i == 0]
        prime_factors = [factor for factor in factors if is_prime(factor)]
        result.append(prime_factors)
    logging.debug(f'End : {ctime()}')
    end_time = time()  
    elapsed_time = end_time - start_time  # Визначаємо різницю часу
    print(f"Elapsed Time: {elapsed_time} seconds")
    return result

def is_prime_async(n):
    if n < 2:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True

def factorize_async(*numbers):
    start_time_async = time()
    logging.debug(f'Start : {current_process().name} {ctime()}')
    result = []
    for number in numbers:
        if number <= 0:
            raise ValueError("Numbers must be positive")
        factors = [i for i in range(1, number + 1) if number % i == 0]
        prime_factors = [factor for factor in factors if is_prime_async(factor)]
        result.append(prime_factors)
    logging.debug(f'End :{current_process().name} {ctime()}')
    end_time_async = time()  
    elapsed_time_async = end_time_async - start_time_async  
    print(f"Elapsed Time: {elapsed_time_async} seconds")
    return result


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(message)s')
    
    a, b, c, d = factorize(128, 255, 99999, 10651060)
    logger.debug("Results for synchronous execution:")
    logger.debug("a: %s", a)
    logger.debug("b: %s", b)
    logger.debug("c: %s", c)
    logger.debug("d: %s", d)
  
    print(f"Number of CPUs: {cpu_count()}")


    with Pool(cpu_count()) as pool:
        results_async = pool.map_async(factorize_async, (128, 255, 99999, 10651060))
        results_async.wait()

    a_async, b_async, c_async, d_async = results_async.get()
    logger.debug("Results for asynchronous execution:")
    logger.debug("a: %s", a_async)
    logger.debug("b: %s", b_async)
    logger.debug("c: %s", c_async)
    logger.debug("d: %s", d_async)

   