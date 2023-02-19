from common import xdg

import shutil
print(xdg.get_config_dir())
print(xdg.get_data_home())
shutil.rmtree(xdg.get_config_dir())
shutil.rmtree(xdg.get_data_home())
