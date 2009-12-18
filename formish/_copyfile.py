__all__ = ['copyfileobj']

import shutil


try:
    from fadvise import posix_fadvise, POSIX_FADV_DONTNEED

    def copyfileobj(fsrc, fdst, length=16*1024, advise_after=1024*1024):
        """
        Reimplementation of shutil.copyfileobj that advises the OS to remove
        parts of the source file from the OS's caches once copied to the
        destination file.

        Usage profile:
            * You have a (potentially) large file to copy.
            * You know you don't need to access the source file once copied.
            * You're quite likely to access the destination file soon after.
        """
        # If we can't access the the fileno then fallback to using shutil.
        if not hasattr(fsrc, 'fileno'):
            return shutil.copyfileobj(fsrc, fdst, length)
        # Calculate the appoximate number of blocks to copy before advising the
        # OS to drop pages from the cache.
        advise_after_blocks = int(advise_after/length)
        # Off we go ...
        blocks_read = 0
        while True:
            data = fsrc.read(length)
            if not data:
                break
            fdst.write(data)
            blocks_read += 1
            if not blocks_read % advise_after_blocks:
                posix_fadvise(fsrc.fileno(), 0, length*blocks_read,
                              POSIX_FADV_DONTNEED)
        # One final advise to flush the remaining blocks.
        posix_fadvise(fsrc.fileno(), 0, 0, POSIX_FADV_DONTNEED)

except ImportError:
    copyfileobj = shutil.copyfileobj

