# pip install tensorflow==1.15
# Install stable-baselines as described in the documentation
import json
import os
from pdb import set_trace as TT

import numpy as np

import gym_pcgrl  # noqa : F401
from args import parse_args
from envs import make_vec_envs

# from stable_baselines3.common.policies import ActorCriticCnnPolicy
# from model import CustomPolicyBigMap, CApolicy, WidePolicy
from model_sb2 import (
    CustomPolicyBigMap,
    CustomPolicySmallMap,
    FullyConvPolicyBigMap,
    FullyConvPolicySmallMap,
    CAPolicy,
)

# from stable_baselines3 import PPO
from stable_baselines import PPO2

# from stable_baselines3.common.results_plotter import load_results, ts2xy
from stable_baselines.results_plotter import load_results, ts2xy
import tensorflow as tf
from utils import (
    get_crop_size,
    get_env_name,
    get_exp_name,
    load_model,
    #                  max_exp_idx
)

n_steps = 0
log_dir = "../"
best_mean_reward, n_steps = -np.inf, 0


def callback(_locals, _globals):
    """
    Callback called at each step (for DQN an others) or after n steps (see ACER or PPO)
    :param _locals: (dict)
    :param _globals: (dict)
    """
    global n_steps, best_mean_reward
    # Print stats every 1000 calls

    if (n_steps + 1) % 10 == 0:
        x, y = ts2xy(load_results(log_dir), "timesteps")

        # pdb.set_trace()
        mean_reward = np.mean(y[-100:])
        ti = 0 if len(x) == 0 else x[-1]
        print(f"{ti} timesteps")
        print(
            "Best mean reward: {:.2f} - Last mean reward per episode: {:.2f}".format(
                best_mean_reward, mean_reward
            )
        )

        # New best model, we save the agent here

        if mean_reward > best_mean_reward:
            best_mean_reward = mean_reward
            # Example for saving best model
            print("Saving new best model")
            _locals["self"].save(os.path.join(log_dir, "best_model.zip"))
        else:
            print("Saving latest model")
            _locals["self"].save(os.path.join(log_dir, "latest_model.zip"))

        if alp_gmm:
            pass

    # TODO: log env._rep_stats ??? Q: how to pass from env to callback? Possibly
    writer = _locals["writer"]
    ep_info_buf = _locals["ep_info_buf"]

    #   summary = tf.Summary(value=[tf.Summary.Value(tag="episode_reward", simple_value=rew_acc[env_idx])])
    #   writer.add_summary(summary, steps + dones_idx[0, 0])
    #   for k in range(1, len(dones_idx[:, 0])):
    #       rew_acc[env_idx] = sum(rewards[env_idx, dones_idx[k-1, 0]:dones_idx[k, 0]])
    #       summary = tf.Summary(value=[tf.Summary.Value(tag="episode_reward", simple_value=rew_acc[env_idx])])
    #       writer.add_summary(summary, steps + dones_idx[k, 0])
    #   rew_acc[env_idx] = sum(rewards[env_idx, dones_idx[-1, 0]:])
    n_steps += 1

    # Returning False will stop training early
    return True


def main(game, representation, n_frames, n_cpu, render, logging, **kwargs):
    if (
        game
        not in [
            "binary_ctrl",
            "sokoban_ctrl",
            "zelda_ctrl",
            "smb_ctrl",
            "MicropolisEnv",
            "RCT",
        ]
    ) and ("minecraft" not in game):
        raise Exception(
            "Not a controllable environment. Maybe add '_ctrl' to the end of the name? E.g. 'sokoban_ctrl'"
        )
    kwargs["n_cpu"] = n_cpu
    env_name = get_env_name(game, representation)
    print("env name: ", env_name)
    exp_name = get_exp_name(game, representation, **kwargs)

    resume = kwargs.get("resume", True)
    ca_action = kwargs.get("ca_action")

    if representation == "wide" and not ("RCT" in game or "Micropolis" in game):
        policy = FullyConvPolicyBigMap

        if game == "sokoban" or game == "sokoban_ctrl":
            policy = FullyConvPolicySmallMap
    elif representation == "cellular":
        policy = CAPolicy
    else:
        #       policy = ActorCriticCnnPolicy
        policy = CustomPolicyBigMap

        if game == "sokoban" or game == "sokoban_ctrl":
            #           T()
            policy = CustomPolicySmallMap
    crop_size = kwargs.get("crop_size")

    #   if crop_size == -1:
    #       kwargs['crop_size'] = map_width * 2
    # kwargs['crop_size'] = get_crop_size(game)

    exp_id = kwargs.get("experiment_id")
    #   n = kwargs.get('experiment_id')

    #   if n is None:
    #       n = max_exp_idx(exp_name)
    #       if not resume:
    #           n += 1
    global log_dir

    exp_name_id = "{}_{}".format(exp_name, exp_id)
    #   log_dir = 'rl_runs/{}_{}_log'.format(exp_name, n)
    log_dir = "rl_runs/{}_log".format(exp_name_id)

    kwargs = {
        **kwargs,
        "render_rank": 0,
        "render": render,
    }

    #   if not resume:
    try:
        os.mkdir(log_dir)
        print("Log directory does not exist, starting anew, bb.")
        resume = False
    except Exception:
        print("Log directory exists, fumbling on. Will try to load model.")
    try:
        env, dummy_action_space, n_tools = make_vec_envs(
            env_name, representation, log_dir, **kwargs
        )
    except Exception as e:
        # if this is a new experiment, clean up the logging directory if we fail to start up

        #       if not resume:
        #           os.rmdir(log_dir)
        raise e

    with open(os.path.join(log_dir, "settings.json"), "w", encoding="utf-8") as f:
        json.dump(kwargs, f, ensure_ascii=False, indent=4)

    #       pass
    if resume:
        model = load_model(log_dir, n_tools=n_tools)

    if representation == "wide":
        #       policy_kwargs = {'n_tools': n_tools}
        policy_kwargs = {}

        if ca_action:
            # FIXME: there should be a better way hahahaha
            env.action_space = dummy_action_space
            # more frequent updates, for debugging... or because our action space is huge?
        #           n_steps = 512
        else:
            pass
    #           n_steps = 2048
    else:
        policy_kwargs = {}
        # the default for SB3 PPO
    #       n_steps = 2048

    if not resume or model is None:
        if representation == "cellular":
            learning_rate = 1e-7
        #           learning_rate = 0.00001
        #           learning_rate = 0.00025
        else:
            learning_rate = 0.00025
        # model = PPO(policy, env, verbose=1, n_steps=n_steps,
        #             tensorboard_log="./runs", policy_kwargs=policy_kwargs)
        model = PPO2(
            policy,
            env,
            verbose=1,
            tensorboard_log="./rl_runs",
            policy_kwargs=policy_kwargs,
            learning_rate=learning_rate,
        )

    n_params = 0
    for param in model.params:
        n_params += np.prod(param.shape)
    print(f"Model has {n_params} parameters.")

    model.set_env(env)

    # model.policy = model.policy.to('cuda:0')
    #   if torch.cuda.is_available():
    #       model.policy = model.policy.cuda()
    tb_log_name = "{}_tb".format(exp_name_id)
    if not logging:
        model.learn(
            total_timesteps=n_frames, reset_num_timesteps=False, tb_log_name=tb_log_name
        )
    else:
        model.learn(
            total_timesteps=n_frames,
            tb_log_name=tb_log_name,
            reset_num_timesteps=False,
            callback=callback,
        )


opts = parse_args()

################################## MAIN ########################################

# User settings
conditional = len(opts.conditionals) > 0
problem = opts.problem
representation = opts.representation
n_frames = opts.n_frames
render = opts.render
logging = True
n_cpu = opts.n_cpu
# resume = opts.resume
resume = True
midep_trgs = opts.midep_trgs
ca_action = opts.ca_action
alp_gmm = opts.alp_gmm
#################

# if 'sokoban' in problem:
#    map_width = 5
# elif 'minecraft' in problem:
#    map_width = 7
# elif 'zelda' in problem:
#    map_width = 14
# elif 'binary' in problem:
#    map_width = 16
# else:
#    raise NotImplementedError(
#        "Not sure how to deal with 'map_width' variable when dealing with problem: {}".format(problem))


max_step = opts.max_step
# TODO: play with change percentage for controllable agents?
change_percentage = opts.change_percentage
global COND_METRICS

if conditional:
    COND_METRICS = opts.conditionals
#   change_percentage = 1.0
else:
    COND_METRICS = []
#   change_percentage = opts.change_percentage
kwargs = {
    #   'map_width': map_width,
    "change_percentage": change_percentage,
    "conditional": conditional,
    "cond_metrics": COND_METRICS,
    "resume": resume,
    "max_step": max_step,
    "midep_trgs": midep_trgs,
    "ca_action": ca_action,
    "crop_size": opts.crop_size,
    "alp_gmm": alp_gmm,
    "experiment_id": opts.experiment_id,
}

if __name__ == "__main__":
    main(problem, representation, int(n_frames), n_cpu, render, logging, **kwargs)
