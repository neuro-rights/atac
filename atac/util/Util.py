import math
import numpy as np

# from pydbg import *
import random
import regex
import string
import os
import sys
import unicodedata


def fast_scandir(dirname):
    """
    Description:
    ------------

    Parameters:
    -----------

    """

    subfolders = [f.path for f in os.scandir(dirname) if f.is_dir()]
    for dirname in list(subfolders):
        subfolders.extend(fast_scandir(dirname))
    return subfolders


def get_file_content(file_path):
    """
    Description:
    ------------

    Parameters:
    -----------

    """

    if not os.path.isfile(file_path):
        print("invalid file path!")
        sys.exit(1)
    #
    lines = None
    try:
        with open(file_path, encoding="utf-8") as content_file:
            lines = [line.rstrip() for line in content_file]
    except OSError as e:
        print("{} file error {}".format(file_path, e.errno))
    #
    return lines


class FourierDatum:
    """
    Description:    Holds Fourier Transform data: complex result, frequency, phase, and amplitude
    ------------

    Attributes:
    ----------

    Methods:
    --------

    """
    def __init__(self, complex_num, freq):
        self.complex_num = complex_num
        self.freq = freq
        self.phase = math.atan2(complex_num.imag, complex_num.real)
        self.amplitude = np.sqrt(complex_num.real**2 + complex_num.imag**2)


def fft(z):
    """Take FFT of complex vector z and store its values in FourierDatum array

    :param z Complex-valued vector
    :returns Array of FourierDatum objects
    """
    fft_vals = np.fft.fft(z)
    fft_data = []
    N = len(z)
    k = 0

    for fft_val in fft_vals:
        # divide by N to keep drawing size reasonable
        fft_data.append(FourierDatum(fft_val / N, k))
        k += 1

    return fft_data


def dft(z):
    """Take DFT of complex vector z and store its values in FourierDatum array

    :param z Complex-valued vector
    :returns Array of FourierDatum objects
    """
    dft_data = []
    N = len(z)
    # k is frequency
    for k in range(0, N):
        zk = complex(0, 0)
        for n in range(0, N):
            phi = (2 * np.pi * k * n) / N
            zk += z[n] * complex(np.cos(phi), -np.sin(phi))
        zk /= N
        dft_data.append(FourierDatum(zk, k))
    #
    return dft_data


def partition_find(string, start, end):
    """
    Description:
    ------------

    Parameters:
    -----------

    """

    return string.partition(start)[2].rpartition(end)[0]


def re_find(string, start, end):
    """
    Description:
    ------------

    Parameters:
    -----------

    """

    return regex.search(start + "(.*)" + end, string, regex.DOTALL).group(1)


def index_find(string, start, end):
    """
    Description:
    ------------

    Parameters:
    -----------

    """

    return string[string.find(start) + len(start) : string.rfind(end)]


def generate_password(length):
    """
    Description:
    ------------

    Parameters:
    -----------

    """

    all = string.ascii_letters + string.digits + string.punctuation
    return "".join(random.sample(all, length))


def generate_word():
    """
    r = RandomWords()
    # Return a single random word
    return r.get_random_word(
        hasDictionaryDef="true",
        includePartOfSpeech="noun,verb",
        minCorpusCount=1,
        maxCorpusCount=10,
        minDictionaryCount=1,
        maxDictionaryCount=10,
        minLength=5,
        maxLength=10)
    """
    pass


def str2bool(v):
    """
    Description:
    ------------

    Parameters:
    -----------

    """

    if isinstance(v, bool):
        return v
    if v.lower() in ("yes", "true", "t", "y", "1"):
        return True
    elif v.lower() in ("no", "false", "f", "n", "0"):
        return False
    try:
        raise TypeError()
    except (ValueError, TypeError) as exception:
        print("Catching all exceptions")


def remove_accent_chars_regex(x: str):
    """
    Description:
    ------------

    Parameters:
    -----------

    """

    return regex.sub(r"\p{Mn}", "", unicodedata.normalize("NFKD", x))


def remove_accent_chars_join(x: str):
    """
    Description:
    ------------

    Parameters:
    -----------

    """
    # answer by MiniQuark
    # https://stackoverflow.com/a/517974/7966259
    return "".join([c for c in unicodedata.normalize("NFKD", x) if not unicodedata.combining(c)])


def fix_mixed_encoding(s):
    """
    Description:    Fixed mixed encoding

    Parameters:
    -----------
    s : str
        The mixed encoding string to fix
    """

    output = ""
    ii = 0
    for _ in s:
        if ii <= len(s) - 1:
            if s[ii] == "\\" and s[ii + 1] == "x":
                b = s[ii : ii + 4].encode("ascii").decode("utf-8")
                output = output + b
                ii += 3
            else:
                output = output + s[ii]
        ii += 1
    #
    return output


"""
def breakpoint_handler(dbg):
    print(dbg.dump_context())
    return DBG_CONTINUE


# Defining a decorator
def inspect(f):
    def wrap(*args, **kwargs):
        dbg(f(*args, **kwargs))
        return f(*args, **kwargs)

    return wrap
"""

# Defining a decorator
def trace(f):
    """
    Description:
    ------------

    Parameters:
    -----------

    """

    def wrap(*args, **kwargs):
        """
        Description:
        ------------

        Parameters:
        -----------

        """

        print(f"[TRACE] func: {f.__name__}, args: {args}, kwargs: {kwargs}")
        return f(*args, **kwargs)

    return wrap
