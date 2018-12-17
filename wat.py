import ctypes
import ctypes.util
import os


PREFIX_DIR = os.path.abspath(os.path.join(".nox", "build_libbezier-build_type-debug", "usr"))


def shared_lib_info():
    print("*" * 60)
    bezier_found = ctypes.util.find_library("bezier")
    print("bezier_found = {}".format(bezier_found))
    if bezier_found is None:
        return
    libbezier = ctypes.cdll.LoadLibrary(bezier_found)
    print("libbezier = {}".format(libbezier))
    print("libbezier.compute_length = {}".format(libbezier.compute_length))


def main():
    shared_lib_info()
    path = os.environ["PATH"]
    new_path = os.pathsep.join([path, os.path.join(PREFIX_DIR, "bin")])
    os.environ["PATH"] = new_path
    shared_lib_info()


if __name__ == "__main__":
    main()
