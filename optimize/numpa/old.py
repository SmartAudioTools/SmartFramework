"""
numpy like with :
- fonction multithreaded with numba
- "out" and "inplace" (overwriting first array)  optionnal parameter when possible
"""


@njit(cache=True, parallel=is_64_bit)
def add(x1, x2, out=None, dtype=None):
    height, width = x1.shape[:2]
    if out is None:
        if dtype is None:
            _dtype = x1.dtype
        else:
            _dtype = _dtype
        _out = numpy.empty(x1.shape, dtype=_dtype)
    else:
        _out = out
    # nb_thread = 8
    # block_size = math.ceil(len(x1) / nb_thread)
    # for t in prange(8):
    #    start = t * block_size
    #    stop = (t + 1) * block_size
    #    _out[start:stop] = x1[start:stop] + x2[start:stop]
    for i in prange(height):
        _out[i] = x1[i] + x2[i]
        # x1[i] += x2[i]  # pas mieux pour du inplace
    return _out


@njit(cache=True, parallel=is_64_bit)
def subtract(x1, x2, out=None, dtype=None):
    "le inplace n'apporte rien par contre on cagne en 2D sur numpy"
    if out is None:
        if dtype is None:
            _dtype = x1.dtype
        else:
            _dtype = dtype
        _out = numpy.empty(x1.shape, dtype=_dtype)
    else:
        _out = out
    for i in prange(len(x1)):
        _out[i] = x1[i] - x2[i]  # 0.127 msec pour du 640x480
        # x1[i] -= x2[i]  # 0.139 msec pour du 640x40
    return _out


@njit(cache=True, parallel=is_64_bit)  # dtype=None,
def diff(a, axis, out=None, dtype=None):
    if out is None:
        if dtype is None:
            _dtype = a.dtype
        else:
            _dtype = _dtype
        _out = numpy.empty(a.shape, dtype=_dtype)
    else:
        _out = out
    inplace = a is out
    # print(inplace)
    height, width = a.shape[:2]
    if axis == 0:
        if inplace:
            for j in prange(width):
                a[1:, j] -= a[:-1, j]
        else:
            for j in prange(width):
                _out[0, j] = a[0, j]
                _out[1:, j] = a[1:, j] - a[:-1, j]
    elif axis == 1:
        if inplace:
            for i in prange(height):
                a[i, 1:] -= a[i, :-1]
        else:
            for i in prange(height):
                _out[i, 0] = a[i, 0]
                _out[i, 1:] = a[i, 1:] - a[i, :-1]
    else:
        raise Exception(
            "numpa.cumsum is not fully coded and does'nt support other axis than 0 and 1 yet"
        )
    return _out


@njit(cache=True, parallel=is_64_bit)
def new_key_frame_detector(new, key, step):
    sum_diff_temp = 0
    sum_diff_spacial = 0
    new_ = new.view(numpy.int8)
    key_ = key.view(numpy.int8)
    height, width = new.shape[:2]
    for index in prange(int(height / step)):
        i = index * step
        line_diff_temp = 0
        line_diff_spacial = 0
        for j in range(0, width - 1, step):
            line_diff_temp += abs(new_[i, j] - key_[i, j])
            line_diff_spacial += abs(new_[i, j] - new_[i, j + 1])
        sum_diff_temp += line_diff_temp
        sum_diff_spacial += line_diff_spacial
    return sum_diff_spacial < sum_diff_temp


# compile or load cashed numpa function
if compile:
    a = numpy.empty((640, 480), dtype="uint8")
    b = numpy.empty((640, 480), dtype="uint8")
    out = cumsum(a, 1)
    cumsum(a, 1, out=out)  # plante
    out = add(a, b)
    add(a, b, out=out)
    out = diff(a, 1)
    diff(a, 1, out=out)
    out = subtract(a, b)
    subtract(a, b, out=out)
    new_key_frame_detector(a, b, 8)


# OLD---------------------


"""def cumsum_1D(a, dtype=None,out = None):

        
    if out is not None:
        if dtype is None:
            dtype = a.dtype
        out = numpy.empty(a.shape, dtype)
    #else 
    # 
    #   a_flat = a.reshape((-1))
    return cumsum(a, dtype=None, out=a_flat)

def diff1D_v2(image):
    return numpy.ediff1d(image, to_begin=image[0, 0])  # 0.416 msec


def diff1D(image):
    # shape = image.shape
    diff_image = numpy.empty(image.shape, dtype="uint8")
    image_flat = image.reshape((-1))
    # image_flat = image.ravel() #0.182 msec
    diff_image_flat = diff_image.reshape((-1))
    diff_image_flat[0] = image_flat[0]
    diff_image_flat[1:] = image_flat[1:] - image_flat[:-1]
    return diff_image
    # image.reshape(shape)


@njit(cache=True)  # sec au lieu de sans
def diff1D_numba(image):
    return numpy.ediff1d(image, to_begin=image[0, 0])  # 0.416 msec


def diff1D__outv1(image, diff_image):
    diff_image.reshape((-1))[:] = numpy.ediff1d(
        image, to_begin=image[0, 0]
    )  ## 2.10msec.. naze ne marche pas avec numba


@njit(cache=True)
def diff1D__outv1_numba(image, diff_image):
    diff_image.reshape((-1))[:] = numpy.ediff1d(
        image, to_begin=image[0, 0]
    )  ## 2.10msec.. naze ne marche pas avec numba


# @profile
def diff1D__outv2(image, diff_image):
    # shape = image.shape
    image_flat = image.reshape((-1))
    # image_flat = image.ravel() #0.182 msec
    diff_image_flat = diff_image.reshape((-1))
    diff_image_flat[0] = image_flat[0]
    diff_image_flat[1:] = image_flat[1:] - image_flat[:-1]
    # image.reshape(shape)


@njit(cache=True)
def diff1D__outv2_numba(image, diff_image):
    # shape = image.shape
    image_flat = image.reshape((-1))  # plus rapide si image pas contigunous que ravel()
    # image_flat = image.ravel()  # 0.182 msec
    diff_image_flat = diff_image.reshape((-1))
    diff_image_flat[0] = image_flat[0]
    diff_image_flat[1:] = image_flat[1:] - image_flat[:-1]
    # image.reshape(shape)


@njit(cache=True)
def diff1D__outv3_numba(image, diff_image):
    diff_image_flat = diff_image.ravel()
    image_flat = image.ravel()
    last_image_value = 0
    for i in range(image.size):
        image_value = image_flat[i]
        diff_image_flat[i] = (
            image_value - last_image_value
        )  # RuntimeWarning: overflow encountered in ubyte_scalars
        last_image_value = image_value
"""
