from centrosome.watershed import watershed as __watershed__


def watershed(image, markers, connectivity=None, offset=None, mask=None):
    return __watershed__(image, markers, connectivity, offset, mask)
