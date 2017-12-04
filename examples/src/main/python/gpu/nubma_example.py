import numpy as np 
import numba
import math
import time
from numba import cuda, vectorize, jit
from pyspark.sql import SparkSession

@cuda.jit('(float32[:], float32[:])')
def func(inp, out):
    i = cuda.grid(1)
    if i < out.size:
        out[i] = inp[i] ** 2


def gpu_work(xs):
    inp = np.asarray(list(xs), dtype=np.float32)
    out = np.zeros_like(inp)
    block_size = 32 * 4
    grid_size = (inp.size + block_size - 1)
    func[grid_size, block_size](inp, out)
    return out

spark = SparkSession\
    .builder\
    .getOrCreate()

sc = spark.sparkContext

# detect if there is an available GPU
if cuda.is_available():
    rdd = sc.parallelize(list(range(100)))
    print("Partitions", rdd.getNumPartitions())

    rdd = rdd.mapPartitions(gpu_work)
    print(rdd.collect())


    # compare cpu and gpu run times

    @vectorize(["float32(float32, float32)", "float64(float64, float64)"], target='cpu')
    def cpu_some_trig(x, y):
        return math.cos(x) + math.sin(y)

    @vectorize(["float32(float32, float32)", "float64(float64, float64)"], target='cuda')
    def cuda_some_trig(x, y):
        return math.cos(x) + math.sin(y)


    nelem = 10 ** 8

    xs = np.random.random(nelem).astype(np.float32)
    ys = np.random.random(nelem).astype(np.float32)

    start_time = time.time()
    cpu_some_trig(xs, ys)
    cpu_elapsed_time = time.time() - start_time

    start_time = time.time()
    cuda_some_trig(xs, ys)
    gpu_elapsed_time = time.time() - start_time

    print("CPU time: {}".format(cpu_elapsed_time))
    print("GPU time: {}".format(gpu_elapsed_time))
    print("GPU performed {}% faster than CPU".format((cpu_elapsed_time-gpu_elapsed_time)*100))

else:
    print("No CUDA devices detected. Are you running this on a GPU enabled VM?")
