#
#                         ThiccFlaskUtils __init__.py | 2020-2022 (c) IsThicc
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
#
import os, re, pathlib
from flask import Flask, Blueprint
from importlib import import_module
#
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
#

# TODO: make this work for this
# def old(blueprint: str, directories: tuple):
#
#     dir_path = ".".join(directories)
#     if blueprint.endswith(".py"):
#         if blueprint not in app.config['ignored']:
#             for line in open(dir_path.replace(".", "/") + "/" + blueprint, "r").readlines():
#                 if line.isspace():
#                     continue
#
#                 if  not re.findall("^#",      line) and \
#                         not re.findall("^from",   line) and \
#                         not re.findall("^import", line):
#
#                     app.register_blueprint(getattr(__import__(f"{dir_path}.{blueprint[:-3]}",
#                                                               fromlist=[line.split(" ", 1)[0]]),
#                                                    line.split(" ", 1)[0]))
#                     break
#             app.logger.warning(f"Blueprint Loaded: {dir_path}.{blueprint.lower()[:-3]}")
#         else:
#             app.logger.fatal(f"Failed to load blueprint '{dir_path}.{blueprint.lower()[:-3]}': File is ignored!")
#         return None

def loadBlueprint(blueprint: str,
                  directory: str,
                  utils: "flask_thiccutils.ThiccUtils",
                  app: Flask) -> bool:

    module_path = pathlib.PurePath(directory).parts
    module_path = list(module_path)
    module_0_path = module_path[0]
    if "/" in module_0_path or "\\" in module_0_path:
        module_path.remove(module_0_path)
    module_path = ".".join(module_path)

    import_module(f"{module_path}.{blueprint[:-3]}")  # If this fails it should stop the process

    for line in open((directory + "/" + blueprint), "r").readlines():
        if line.isspace():
            continue

        if  not re.findall("^#",      line) and \
            not re.findall('^"""',    line) and \
            not re.findall("^from",   line) and \
            not re.findall("^import", line):

            try:
                variable = getattr(
                    __import__(f"{module_path}.{blueprint[:-3]}", fromlist=[line.split(" ", 1)[0]]),
                    line.split(" ", 1)[0]
                )
            except ImportError as exc:
                # This probably means we tried to import something that isn't a variable ex. multi-line comment
                utils.logger.debug(str(exc))
                utils.logger.debug("An error occurred while loading a blueprint. This probably means "
                                   "the module tried to import a multi-line comment or something similar.")
                continue

            if not isinstance(variable, Blueprint):
                utils.logger.info("Found variable while loading a blueprint but is not instance of `flask.Blueprint`")
                continue

            app.register_blueprint(variable)
            utils.logger.debug(f"Blueprint Loaded: {module_path}.{blueprint.lower()[:-3]}")
            return True
    utils.logger.debug(f"Failed to load blueprint. Is there no blueprint variable?")
    return False

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

def setup(app: Flask, utils: "flask_thiccutils.ThiccUtils"):
    logger = utils.logger
    blueprint_dir = utils.config.get("blueprint_dir", False)  # A dir for just blueprints, no dirs

    if not blueprint_dir:
        blueprint_dirs = utils.config.get("blueprint_dirs", False)  # A dir for multiple blueprint dirs
        if not blueprint_dirs:
            raise ValueError("No blueprint directory defined for blueprint module. "
                             "Define using `blueprint_dir` or `blueprint_dirs` config option.")

    ignored_blueprints = utils.config.get("ignored_blueprints", [])

    def listBlueprintDir(dir):
        for blueprint in os.listdir(dir):
            if not blueprint.endswith(".py"):
                continue
            if blueprint in ignored_blueprints:
                logger.info(f"Failed to load blueprint '{dir}/{blueprint}': File is ignored!")

            loadBlueprint(blueprint, f"{blueprint_dir}/{blueprint}", utils, app)

    if blueprint_dir:
        listBlueprintDir(blueprint_dir)

    else:
        for directory in os.listdir(blueprint_dirs):
            if not os.path.isdir(os.path.abspath(directory)):
                continue

            listBlueprintDir(f"{blueprint_dirs}/{directory}")

            # for blueprint in os.listdir(directory):
            #     if not check_blueprint(blueprint):
            #         continue
            #     loadBlueprint(blueprint, f"{directory}/{blueprint}", utils, app)

#
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
#
