from centrosome.threshold import get_threshold as __get_threshold__
from centrosome.threshold import get_global_threshold as __get_global_threshold__
from centrosome.threshold import get_adaptive_threshold as __get_adaptive_threshold__
from centrosome.threshold import get_per_object_threshold as __get_per_object_threshold__
from centrosome.threshold import get_otsu_threshold as __get_otsu_threshold__
from centrosome.threshold import get_mog_threshold as __get_mog_threshold__
from centrosome.threshold import get_background_threshold as __get_background_threshold__
from centrosome.threshold import get_robust_background_threshold as __get_robust_background_threshold__
from centrosome.threshold import mad as __mad__
from centrosome.threshold import binned_mode as __binned_mode__
from centrosome.threshold import get_ridler_calvard_threshold as __get_ridler_calvard_threshold__
from centrosome.threshold import get_kapur_threshold as __get_kapur_threshold__
from centrosome.threshold import get_maximum_correlation_threshold as __get_maximum_correlation_threshold__
from centrosome.threshold import weighted_variance as __weighted_variance__
from centrosome.threshold import sum_of_entropies as __sum_of_entropies__
from centrosome.threshold import log_transform as __log_transform__
from centrosome.threshold import inverse_log_transform as __inverse_log_transform__
from centrosome.threshold import numpy_histogram as __numpy_histogram__


def get_threshold(threshold_method, threshold_modifier, image, mask, labels, threshold_range_min, threshold_range_max,
                  threshold_correction_factor, adaptive_window_size, **kwargs):
    __get_threshold__(threshold_method, threshold_modifier, image, mask, labels, threshold_range_min,
                      threshold_range_max, threshold_correction_factor, adaptive_window_size, **kwargs)


def get_global_threshold(threshold_method, image, mask, **kwargs):
    return __get_global_threshold__(threshold_method, image, mask, **kwargs)


def get_adaptive_threshold(threshold_method, image, threshold, mask, adaptive_window_size, **kwargs):
    return __get_adaptive_threshold__(threshold_method, image, threshold, mask, adaptive_window_size, **kwargs)


def get_per_object_threshold(method, image, threshold, mask, labels, threshold_range_min, threshold_range_max,
                             **kwargs):
    return __get_per_object_threshold__(method, image, threshold, mask, labels, threshold_range_min,
                                        threshold_range_max, **kwargs)


def get_otsu_threshold(image, mask, two_class_otsu, use_weighted_variance, assign_middle_to_foreground):
    return __get_otsu_threshold__(image, mask, two_class_otsu, use_weighted_variance, assign_middle_to_foreground)


def get_mog_threshold(image, mask, object_fraction):
    return __get_mog_threshold__(image, mask, object_fraction)


def get_background_threshold(image, mask):
    return __get_background_threshold__(image, mask)


def get_robust_background_threshold(image, mask, lower_outlier_fraction, upper_outlier_fraction,
                                    deviations_above_average, average_fn, variance_fn):
    return __get_robust_background_threshold__(image, mask, lower_outlier_fraction, upper_outlier_fraction,
                                               deviations_above_average, average_fn, variance_fn)


def mad(a):
    return __mad__(a)


def binned_mode(a):
    return __binned_mode__(a)


def get_ridler_calvard_threshold(image, mask):
    return __get_ridler_calvard_threshold__(image, mask)


def get_kapur_threshold(image, mask):
    return __get_kapur_threshold__(image, mask)


def get_maximum_correlation_threshold(image, mask, bins):
    return __get_maximum_correlation_threshold__(image, mask, bins)


def weighted_variance(image, mask, binary_image):
    return __weighted_variance__(image, mask, binary_image)


def sum_of_entropies(image, mask, binary_image):
    return __sum_of_entropies__(image, mask, binary_image)


def log_transform(image):
    return __log_transform__(image)


def inverse_log_transform(image, d):
    return __inverse_log_transform__(image, d)


def numpy_histogram(a, bins, range, normed, weights):
    return __numpy_histogram__(a, bins, range, normed, weights)
