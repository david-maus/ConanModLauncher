import os
import sys
import hashlib








def sha1OfFile(filepath):
    """Main entry point of the app."""
    sha = hashlib.sha1()
    with open(filepath, 'rb') as f:
        while True:
            block = f.read(2**10)
            if not block:
                break
            sha.update(block)
        return sha.hexdigest()


def hash_dir(dir_path):
    """Main entry point of the app."""
    hashes = []
    for path, dirs, files in os.walk(dir_path):
        for file in sorted(files):
            hashes.append(sha1OfFile(os.path.join(path, file)))
        for dir in sorted(dirs):
            hashes.append(hash_dir(os.path.join(path, dir)))
        break
    return str(hash(''.join(hashes)))
