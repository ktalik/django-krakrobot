"""
Useful context processors for templates
"""

import meta


def meta_data(request):
    """
    Returns a dictionary of meta data of this app. Note that all property names
    are in lowercase.
    """
    return {
        'meta': dict([
            [var.lower(), eval('meta.{}'.format(var))]
            for var in dir(meta) if var[0:2] != '__'
        ])
    }
