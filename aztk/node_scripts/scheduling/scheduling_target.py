import concurrent.futures
import os
import time

import requests

from aztk import error


def http_request_wrapper(func, *args, timeout=None, max_execution_time=300, **kwargs):
    start_time = time.clock()
    while True:
        try:
            response = func(*args, timeout=timeout, **kwargs)
            response.raise_for_status()
            return response
        except requests.Timeout:
            pass

        if (time.clock() - start_time > max_execution_time):
            raise error.AztkError("Waited {} seconds for request {}, exceeded max_execution_time={}".format(
                time.clock() - start_time,
                func.__name__,
                max_execution_time,
            ))


def _download_resource_file(task_id, resource_file):
    response = http_request_wrapper(requests.get, url=resource_file.blob_source, timeout=None, stream=True)
    if resource_file.file_path:
        write_path = os.path.join(os.environ.get("AZ_BATCH_TASK_WORKING_DIR"), resource_file.file_path)
        with open(write_path, 'wb') as stream:
            for chunk in response.iter_content(chunk_size=16777216):
                stream.write(chunk)
            return None

    raise error.AztkError("ResourceFile file_path not set.")


def download_task_resource_files(task_id, resource_files):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {
            executor.submit(_download_resource_file, task_id, resource_file): resource_file
            for resource_file in resource_files
        }
    done, not_done = concurrent.futures.wait(futures)
    if not_done:
        raise error.AztkError("Not all futures completed. {}".format(not_done.pop().result()))
    errors = [result.result() for result in done if isinstance(result.result(), Exception)]
    if errors:
        raise error.AztkError(errors)
    else:
        return [result.result() for result in done]
