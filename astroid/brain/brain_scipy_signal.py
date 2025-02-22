# Copyright (c) 2019 Valentin Valls <valentin.valls@esrf.fr>
# Copyright (c) 2020-2021 hippo91 <guillaume.peillex@gmail.com>
# Copyright (c) 2020 Claudiu Popa <pcmanticore@gmail.com>
# Copyright (c) 2021 Pierre Sassoulas <pierre.sassoulas@gmail.com>

# Licensed under the LGPL: https://www.gnu.org/licenses/old-licenses/lgpl-2.1.en.html
# For details: https://github.com/PyCQA/astroid/blob/master/LICENSE


"""Astroid hooks for scipy.signal module."""

import astroid


def scipy_signal():
    return astroid.parse(
        """
    # different functions defined in scipy.signals

    def barthann(M, sym=True):
        return numpy.ndarray([0])

    def bartlett(M, sym=True):
        return numpy.ndarray([0])

    def blackman(M, sym=True):
        return numpy.ndarray([0])

    def blackmanharris(M, sym=True):
        return numpy.ndarray([0])

    def bohman(M, sym=True):
        return numpy.ndarray([0])

    def boxcar(M, sym=True):
        return numpy.ndarray([0])

    def chebwin(M, at, sym=True):
        return numpy.ndarray([0])

    def cosine(M, sym=True):
        return numpy.ndarray([0])

    def exponential(M, center=None, tau=1.0, sym=True):
        return numpy.ndarray([0])

    def flattop(M, sym=True):
        return numpy.ndarray([0])

    def gaussian(M, std, sym=True):
        return numpy.ndarray([0])

    def general_gaussian(M, p, sig, sym=True):
        return numpy.ndarray([0])

    def hamming(M, sym=True):
        return numpy.ndarray([0])

    def hann(M, sym=True):
        return numpy.ndarray([0])

    def hanning(M, sym=True):
        return numpy.ndarray([0])

    def impulse2(system, X0=None, T=None, N=None, **kwargs):
        return numpy.ndarray([0]), numpy.ndarray([0])

    def kaiser(M, beta, sym=True):
        return numpy.ndarray([0])

    def nuttall(M, sym=True):
        return numpy.ndarray([0])

    def parzen(M, sym=True):
        return numpy.ndarray([0])

    def slepian(M, width, sym=True):
        return numpy.ndarray([0])

    def step2(system, X0=None, T=None, N=None, **kwargs):
        return numpy.ndarray([0]), numpy.ndarray([0])

    def triang(M, sym=True):
        return numpy.ndarray([0])

    def tukey(M, alpha=0.5, sym=True):
        return numpy.ndarray([0])
        """
    )


astroid.register_module_extender(astroid.MANAGER, "scipy.signal", scipy_signal)
