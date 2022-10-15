import os
import urllib.request


def print_download_progress(chunk_number, chunk_max_size, download_size) -> None:
    if download_size:
        if chunk_max_size > download_size:
            percentage = chunk_number * 100
        else:
            percentage = int(chunk_max_size / download_size * chunk_number * 100)
        print(f"{percentage}% done")


def download(url: str, target_path: str, report_progress=False) -> None:
    download_directory = os.path.dirname(target_path)
    if not os.path.isdir(download_directory):
        os.makedirs(download_directory)

    urllib.request.urlretrieve(
        url,
        target_path,
        reporthook=print_download_progress if report_progress else None,
    )
