import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument('-file_path', '--file_path', required=True)
# adding parameter for where to save all the data to:
parser.add_argument('-save', '--save_path', required=False, default=None)
parser.add_argument('-n_it', '--iteration_no', required=True)
parser.add_argument('-jid', '--job_id', required=True)  # SLURM_JOB_NAME
parser.add_argument('-jn', '--job_name', required=True)  # SLURM_JOB_NAME.sh

io_args = parser.parse_args()
n_it = int(io_args.iteration_no)
job_id = io_args.job_id
job_name = io_args.job_name

DATA_PATH = io_args.file_path  # Now == file_path/protein
SAVE_PATH = io_args.save_path
# if no save path is provided we just save it in the same location as the data
if SAVE_PATH is None: SAVE_PATH = DATA_PATH

if n_it != -1:  # creating the job directory
    try:
        os.mkdir(SAVE_PATH + '/iteration_' + str(n_it))
    except OSError:  # file already exists
        pass
    with open(SAVE_PATH + '/iteration_' + str(n_it) + '/' + job_name, 'w') as ref:
        ref.write(job_id + '\n')

else:  # When n_it == -1 we create a seperate directory (for jobs that occur after an iteration)
    try:
        os.mkdir(SAVE_PATH + '/after_iteration')
    except OSError:
        pass
    with open(SAVE_PATH + '/after_iteration' + '/' + job_name, 'w') as ref:
        ref.write(job_id + '\n')
