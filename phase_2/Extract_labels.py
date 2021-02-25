import argparse
import builtins as __builtin__
import glob
import gzip
import os
from contextlib import closing
from multiprocessing import Pool


# For debugging purposes only:
def print(*args, **kwargs):
    __builtin__.print('\t extract_L: ', end="")
    return __builtin__.print(*args, **kwargs)


parser = argparse.ArgumentParser()
parser.add_argument('-if', '--is_final', required=True)
parser.add_argument('-n_it', '--iteration_no', required=True)
parser.add_argument('-protein', '--protein', required=True)
parser.add_argument('-file_path', '--file_path', required=True)
parser.add_argument('-t_pos', '--tot_process', required=True)
parser.add_argument('-sof', '--software', required=True)

io_args = parser.parse_args()

is_final = io_args.is_final
n_it = int(io_args.iteration_no)
protein = io_args.protein
file_path = io_args.file_path
tot_process = int(io_args.tot_process)
sof = io_args.software

if is_final == 'False' or is_final == 'false':
    is_final = False
elif is_final == 'True' or is_final == 'true':
    is_final = True
else:
    raise TypeError('-if parameter must be a boolean (true/false)')

if sof == 'GLIDE':
    key_word = 'r_i_docking_score'
elif sof == 'OEDDOCKING':
    key_word = 'FRED Chemgauss4 score'
elif sof == "AUTODOCK_GPU":
    key_word = 'ADSCOR'
else:
    raise ValueError('Unknown docking software, check line 7 logs.txt and try again.')

# mol_key = 'ZINC'
print("Keyword: ", key_word)


def get_scores(ref):
    scores = []
    for line in ref:  # Looping through the molecules
        zinc_id = line.rstrip()
        line = ref.readline()
        # '$$$' signifies end of molecule info
        while line != '' and line[:4] != '$$$$':  # Looping through its information and saving scores

            tmp = line.rstrip().split('<')[-1]

            if key_word == tmp[:-1]:
                tmpp = float(ref.readline().rstrip())
                if tmpp > 50 or tmpp < -50:
                    print(zinc_id, tmpp)
                else:
                    scores.append([zinc_id, tmpp])

            line = ref.readline()
    return scores


def extract_glide_score(filen):
    scores = []
    try:
        # Opening the GNU compressed file
        with gzip.open(filen, 'rt') as ref:
            scores = get_scores(ref)

    except Exception as e:
        print('Exception occured in Extract_labels.py: ', e)
        # file is already decompressed
        with open(filen, 'r') as ref:
            scores = get_scores(ref)

    if 'test' in os.path.basename(filen):
        new_name = 'testing'
    elif 'valid' in os.path.basename(filen):
        new_name = 'validation'
    elif 'train' in os.path.basename(filen):
        new_name = 'training'
    else:
        print("Could not generate new training set")
        exit()

    with open(file_path + '/' + protein + '/iteration_' + str(n_it) + '/' + new_name + '_' + 'labels.txt', 'w') as ref:
        ref.write('r_i_docking_score' + ',' + 'ZINC_ID' + '\n')
        for z_id, gc in scores:
            ref.write(str(gc) + ',' + z_id + '\n')


if __name__ == '__main__':
    files = []
    iter_path = file_path + '/' + protein + '/iteration_' + str(n_it)

    # Checking to see if the labels have already been extracted:
    sets = ["training", "testing", "validation"]
    files_labels = glob.glob(iter_path + "/*_labels.txt")
    foundAll = True
    for s in sets:
        found = False
        print(s)
        for f in files_labels:
            set_name = f.split('/')[-1].split("_labels.txt")[0]
            if set_name == s:
                found = True
                print('Found')
                break
        if not found:
            foundAll = False
            print('Not Found')
            break
    if foundAll:
        print('Labels have already been extracted...')
        print('Remove "_labels.text" files in \"' + iter_path + '\" to re-extract')
        exit(0)

    # Checking to see if this is the final iteration to use the right folder
    if is_final:
        path = file_path + '/' + protein + '/after_iteration/docked/*.sdf*'
    else:
        path = iter_path + '/docked/*.sdf*'
        path_labels = iter_path + '/*labels*'

    for f in glob.glob(path):
        files.append(f)

    print("num files in", path, ":", len(files))
    print("Files:", [os.path.basename(f) for f in files])
    if len(files) == 0:
        print('NO FILES IN: ', path)
        print('CANCEL JOB...')
        exit(1)

    # Parallel running of the extract_glide_score() with each file path of the files array
    with closing(Pool(len(files))) as pool:
        pool.map(extract_glide_score, files)

    if not is_final:
        # renaming from f1_f2_f3 to f3_labels.txt
        try:
            for f in glob.glob(path_labels):
                print(f, iter_path + '/' + f.split('/')[-1].split('_')[2] + '_' + 'labels.txt')
                os.rename(f, iter_path + '/' + f.split('/')[-1].split('_')[2] + '_' + 'labels.txt')  ## why are we renaming this?
        except IndexError:
            print("Index error on renaming", f)
