import os
import requests

from typing import Callable


def download_data(url: str, out_file: str, out_path: str = None, chunk_size: int = 5, 
                  file_size: int = None, force_download: bool = False, print_out: bool = True,
                  chunk_callback: Callable = None):
    def print_msg(msg, **kwargs):
        if print_out:
            print(msg, **kwargs)

    if out_path is None:
        file_dir = os.path.dirname(__file__)
        out_path = os.path.join(file_dir, '..', '..', '.data')

    filename = os.path.join(out_path, out_file)
    if os.path.exists(filename) and not force_download:
        print_msg(f'File already downloaded, skipping download process')
        return filename

    print_msg(f'Downloading url {url} to file {filename}')
    url_request = requests.get(url, stream=True)
    if file_size is not None:
        print_msg('_' * (int(file_size/chunk_size)+ 1))

    chunk_bytes = chunk_size * 1024 * 1024
    with open(filename, 'wb') as wf_stream:
        for chunk in url_request.iter_content(chunk_size=chunk_bytes):
            if chunk:
                wf_stream.write(chunk)
                if chunk_callback:
                    chunk_callback()
                else:
                    print_msg('#', end='')

    print_msg(f'\nFile downloaded to {filename}')
    return filename

