# coding: utf-8

import tarfile
import zipfile
import os.path
import os


def unzip_zip(file_path):
    try:
        (file_dir_path, file_name) = os.path.split(file_path)
        zfile = zipfile.ZipFile(file_path)
        for name in zfile.namelist():
          (dirname, filename) = os.path.split(name)
          dirname = os.path.join(file_dir_path, dirname)
          print "Decompressing " + filename + " on " + dirname
          if not os.path.exists(dirname):
            os.makedirs(dirname)
          zfile.extract(name, dirname)
    except zipfile.BadZipfile as error:
        return u'Plik powinien być typu archiwum'
    except Exception as error:
        print error
        return u'Błąd przetwarzania przesyłanego pliku (zip)'


def unzip_tar(file_path):
    try:
        (file_dir_path, file_name) = os.path.split(file_path)
        tar = tarfile.open(file_path)
        tar.extractall(path=file_dir_path)
        tar.close()
    except Exception as error:
        print error
        return u'Błąd przetwarzania przesyłanego pliku (tar)'


def unzip(file_path):
    error = unzip_tar(file_path)
    if error:
        error = unzip_zip(file_path)
    return error


