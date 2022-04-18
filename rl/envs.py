from collections import namedtuple
import os
from pdb import set_trace as TT

from gym import spaces

from gym_pcgrl import wrappers, conditional_wrappers

# from stable_baselines3.common.vec_env import SubprocVecEnv, DummyVecEnv
# from stable_baselines.common.vec_env import SubprocVecEnv, DummyVecEnv
# from utils import RenderMonitor, get_map_width

# def make_env(env_name, representation, rank=0, log_dir=None, **kwargs):
def make_env(cfg_dict):
    """
    Return a function that will initialize the environment when called.

    Args:
        cfg_dict: dictionary of configuration parameters
    """
    # Turn dictionary into an object with attributes instead of keys.
    cfg = namedtuple("env_cfg", cfg_dict.keys())(*cfg_dict.values())
    crop_size = cfg.crop_size
    cfg_dict.pop("crop_size")

    if cfg.representation == "wide":
        env = wrappers.ActionMapImagePCGRLWrapper(cfg.env_name, **cfg_dict)

    elif cfg.representation == "wide3D":
        # raise NotImplementedError("3D wide representation not implemented")
        env = wrappers.ActionMap3DImagePCGRLWrapper(cfg.env_name, **cfg_dict)

    elif cfg.representation == "cellular":
        # env = wrappers.CAWrapper(env_name, **kwargs)
        env = wrappers.CAactionWrapper(cfg.env_name, **cfg_dict)

    elif cfg.representation in ["narrow", "turtle"]:
        crop_size = cfg.crop_size
        env = wrappers.CroppedImagePCGRLWrapper(cfg.env_name, crop_size, **cfg_dict)

    elif cfg.representation in ["narrow3D", "turtle3D"]:
        crop_size = cfg.crop_size
        env = wrappers.Cropped3DImagePCGRLWrapper(cfg.env_name, crop_size, **cfg_dict)

    else:
        raise Exception("Unknown representation: {}".format(cfg.representation))
    env.configure(**cfg_dict)
    if cfg.max_step is not None:
        env = wrappers.MaxStep(env, cfg.max_step)
    #   if log_dir is not None and cfg.get('add_bootstrap', False):
    #       env = wrappers.EliteBootStrapping(env,
    #                                           os.path.join(log_dir, "bootstrap{}/".format(rank)))
    env = conditional_wrappers.ConditionalWrapper(
        env, ctrl_metrics=cfg.conditionals, **cfg_dict
    )
    if not cfg.evaluate:
        if not cfg.alp_gmm:
            env = conditional_wrappers.UniformNoiseyTargets(env, **cfg_dict)
        else:
            env = conditional_wrappers.ALPGMMTeacher(env, **cfg_dict)
    # it not conditional, the ParamRew wrapper should just be fixed at default static targets
    #   if render or log_dir is not None and len(log_dir) > 0:
    #       # RenderMonitor must come last
    #       env = RenderMonitor(env, rank, log_dir, **kwargs)

    return env
