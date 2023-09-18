



import pathlib
import runpy
import os
import sys
import pytest


scripts = pathlib.Path('test_examples').resolve().glob('launch.py')

@pytest.mark.parametrize('script', scripts)
def test_launching(script):

    parent_path = str(script.parent)
    sys.path.insert(0,parent_path)
    runpy.run_path(str(script),run_name='__main__')


scripts = pathlib.Path('test_examples').resolve().glob('read.py')


@pytest.mark.parametrize('script', scripts)
def test_reading(script):

    parent_path = str(script.parent)
    sys.path.insert(0,parent_path)
    #runpy.run_path(str(script),run_name='__main__')


