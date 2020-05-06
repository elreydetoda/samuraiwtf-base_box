from os import listdir
from os.path import isdir, join, dirname, realpath, abspath
import yaml
import katanaerrors

module_dict = {}


def load_module_info(path):
    with open(path, 'r') as stream:
        module_info = yaml.load(stream, Loader=yaml.SafeLoader)
        module_info['path'] = dirname(path)

        provisioner_class = module_info.get("class", "provisioners.DefaultProvisioner")
        if "." in provisioner_class:
            class_name = provisioner_class[provisioner_class.rindex(".") + 1:]
        else:
            class_name = provisioner_class

        mod = __import__(provisioner_class, fromlist=[class_name])
        klass = getattr(mod, class_name)

        provisioner = klass(module_info)
        module_dict[module_info.get('name').lower()] = provisioner

        return provisioner


def list_modules(path=None, module_list=None):
    if module_list is None:
        module_list = []
    if path is None:
        my_path = abspath(dirname(__file__))
        path = realpath(join(my_path, "modules"))

    if len(module_list) == 0:
        module_dict.clear()

    file_list = listdir(path)
    for f in file_list:
        file_path = join(path, f)
        if isdir(file_path):
            list_modules(file_path, module_list)
        elif f.endswith(".yml"):
            module_info = load_module_info(file_path)
            if module_info is not None:
                module_list.append(module_info)
    return module_list


def get_module_info(name):
    return module_dict.get(name)


def _run_function(module_name, function_name):
    if len(module_dict) == 0:
        list_modules()

    provisioner = module_dict.get(module_name.lower())
    if provisioner is None:
        raise katanaerrors.ModuleNotFound(module_name)

    if hasattr(provisioner, function_name) and callable(getattr(provisioner, function_name)):
        function_to_call = getattr(provisioner, function_name)
        return function_to_call()
    else:
        raise katanaerrors.NotImplemented(function_name, type(provisioner).__name__)


def install_module(name):
    _run_function(name, "install")


def remove_module(name):
    _run_function(name, "remove")


def start_module(name):
    _run_function(name, "start")


def stop_module(name):
    _run_function(name, "stop")


def status_module(name):
    return _run_function(name, "status")