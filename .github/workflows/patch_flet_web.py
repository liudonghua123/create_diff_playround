import sys
from flet.utils import get_package_web_dir
from distutils.dir_util import copy_tree

if __name__ == '__main__':
  src_path = sys.argv[1] if len(sys.argv) > 1 else 'web'
  dst_path = get_package_web_dir()
  print(f'copy {src_path} to {dst_path}')
  copy_tree(src_path, dst_path)