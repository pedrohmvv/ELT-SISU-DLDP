# -*- coding: UTF-8 -*-
"""Import modules"""
from lib_provider_theme.iface_extract import Extract
from lib_provider_theme.iface_transform import Transform


def download(**context) -> None:
    """ Download operator """
    Extract(**context).download()


def transform(**context) -> None:
    """ Transform operator """
    Transform(**context).execute()
