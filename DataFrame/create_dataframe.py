import pandas as pd
from os import listdir
from trajectory_inheritance.trajectory import solvers
from Directories import data_home, SaverDirectories_new
from trajectory_inheritance.trajectory import get
from Analysis_Functions.Pathlength import path_length_per_experiment, path_length_during_attempts
from tqdm import tqdm
from Setup.Maze import Maze
from Setup.Attempts import Attempts

df_dir = data_home + 'DataFrame\\data_frame'


def maze_size(size):
    maze_s = {'Large': 'L',
              'Medium': 'M',
              'Small Far': 'S',
              'Small Near': 'S'}
    if size in maze_s.keys():
        return maze_s[size]
    else:
        return size


def get_filenames(solver):
    if solver == 'ant':
        return [filename for filename in listdir(SaverDirectories_new[solver]) if 'ant' in filename]
    elif solver == 'human':
        return [filename for filename in listdir(SaverDirectories_new[solver]) if '_' in filename]
    else:
        return [filename for filename in listdir(SaverDirectories_new[solver])]


def new_experiments_df(df, solver='ant'):
    new_experiment_dfs = pd.DataFrame()
    for filename in get_filenames(solver):
        if filename not in df['filename'].unique():
            new_experiment_df = pd.DataFrame([[filename, solver]],
                                             columns=['filename', 'solver'])
            new_experiment_dfs = new_experiment_dfs.append(add_information(new_experiment_df), ignore_index=True)
    return new_experiment_dfs


def save_df(df):
    # df.to_json(df_dir + ' - backup.json')
    df.to_json(df_dir + '.json')


def add_information(df):
    df['size'] = df[['filename', 'solver']].apply(lambda x: get(*x).size, axis=1)
    df['shape'] = df[['filename', 'solver']].apply(lambda x: get(*x).shape, axis=1)
    df['winner'] = df[['filename', 'solver']].apply(lambda x: get(*x).winner, axis=1)
    df['communication'] = df[['filename', 'solver']].apply(lambda x: x.communication, axis=1)
    # df['length unit'] = df[['solver']].apply(lambda x: length_unit_func(*x), axis=1) # TODO: install
    df['exit size [length unit]'] = df[['size', 'shape', 'solver']].apply(lambda x: Maze(*x).exit_size, axis=1)
    df['maze size'] = df[['size']].apply(lambda x: maze_size(*x), axis=1)

    df = apply_func(df, path_length_per_experiment, 'path length [length unit]')
    df = apply_func(df, path_length_during_attempts, 'path_length_during_attempts [length unit]')

    df['path length/exit size []'] = df.apply(
        lambda x: x['path length [length unit]'] / x['exit size [length unit]'], axis=1)
    df['average Carrier Number'] = df[['filename', 'solver']].progress_apply(
        lambda x: get(*x).averageCarrierNumber(), axis=1)
    df['Attempts'] = df[['filename', 'solver']].progress_apply(
        lambda x: Attempts(get(*x), 'extend'), axis=1)

    df = df[['filename', 'solver', 'size', 'maze size', 'shape',
             'winner', 'communication', 'average Carrier Number',
             'length unit', 'path length [length unit]', 'exit size [length unit]',
             'path length/exit size []',
             'Attempts', 'path_length_during_attempts [length unit]']]

    return df


def apply_func(df, func, column_name):
    tqdm.pandas()
    print('Calculating ' + column_name + ' with ' + func.__name__)
    df[column_name] = df[['filename', 'solver']].progress_apply(lambda x: func(get(*x)), axis=1)
    return df


def drop_non_existent(df):
    df = df.drop_duplicates(subset=['filename']).reset_index()

    for solver in solvers:
        to_drop = []
        df_solver = df.iloc[df.groupby(by='solver').groups[solver]]
        for i in df_solver.index:
            # print(i)
            if df.iloc[i]['filename'] not in get_filenames(solver):
                print('Dropped ' + str(df.iloc[i]['filename']))
                to_drop.append(i)
        df = df.drop(index=to_drop)

    return df.reset_index(drop=True).drop(columns=['index'])


df = pd.read_json(df_dir + '.json')
#
# for solver in solvers:
# for solver in ['ps_simulation']:
#     df = df.append(new_experiments_df(df, solver=solver), ignore_index=True)
#
#
# StartedScripts: path length during attempts is sometimes 0 for some reason
#  Attempts is also problematic , because smoothing window is off
#  just make all the Attempts for SPT NaN, and also path length during attempts

# df = drop_non_existent(df)

# save_df(df)
