# Deep-Docking-NonAutomated

Deep docking (DD) is a deep learning-based tool developed to accelerate docking-based virtual screening. Using a docking program of choice, one can screen extensive chemical libraries like ZINC15 (containing > 1.3 billion molecules) 50-100 times faster than typical docking. For further details into the processes behind DD, please refer to our paper (https://doi.org/10.1021/acscentsci.0c00229). 

If you use Deep Docking, please cite:

Gentile F, Agrawal V, Hsing M, Ton A-T, Ban F, Norinder U, et al. *Deep Docking: A Deep Learning Platform for Augmentation of Structure Based Drug Discovery.* ACS Cent Sci 2020:acscentsci.0c00229.

## Requirements
* rdkit
* tensorflow >= 1.14.0
* pandas
* numpy
* keras
* matplotlib
* scikit-learn
* Ligand preparation tool
* Docking program

## Usage

### Before starting. Preparing a database for deep docking
Databases for DD should be obtained in SMILE format. For each compound of the database, DD requires the Morgan fingerprints of radius 2 and size 1024 bits, represented as the list of the indexes of bits that are set to 1. The  Utilities folder of this repository provides tools to facilitate the preparation of a database of SMILES structures. First, it is recommended to split the SMILES into a number of evenly populated files to facilitate other steps such as random sampling and inference, and place these files into a new folder. This reorganization can be achieved for example with the *split* command in bash, and the resulting files should have txt extensions. For example, considering a *smiles.smi* file with 1 billion of compounds, to obtain 1000 evenly splitted txt files

```bash
split -l 1000000 smiles.smi smile_all_ --additional-suffix=.txt
```

Ideally the number of final files should be equal to the number of CPUs used for random sampling (phase 1, see below) and always larger than the number of GPUs used for inference (phase 3, see below). 

Morgan fingerprints can be then generated in the correct format with

```bash
python Morgan_fing.py -sfp path_smile_folder -fp path_to_morgan_folder -fn name_morgan_folder -tp num_cpus
```

with num_cpus = number of CPUs for multiprocessing Morgan fingeprint calculations.


### Phase 1. Random sampling of molecules
In phase 1 molecules are randomly sampled from the database to build or augment the training set. During the first iteration, molecules are also sampled for generating the validation and test sets.

#### Run phase 1
To run phase 1, run sequentially the following commands 
```bash
python molecular_file_count_updated.py -pt project_name -it current_iteration -cdd morgan_directory -t_pos total_processors -t_samp molecules_to_dock
python sampling.py -pt project_name -fp path_to_project_without_name -it current_iteration -dd morgan_directory -t_pos total_processors -tr_sz train_size -vl_sz val_size
python sanity_check.py -pt project_name -fp path_to_project_without_name -it current_iteration
python Extracting_morgan.py -pt project_name -fp path_to_project_without_name -it current_iteration -md morgan_directory -t_pos total_processors
python Extracting_smiles.py -pt project_name -fp path_to_project_without_name -it current_iteration -fn 0 -smd smile_directory -sd NA -t_pos total_processors -if is_final_iteration?
```
molecules_to_dock = number of molecules to dock in the current iteration
train_size =  size of the training set to sample
val_size = sizes of test and validation sets (just used in the first iteration). molecules_to_dock should be equal to train_size + 2*val_size


### After phase 1. Docking
After phase 1 is completed, molecules grouped in the smiles folder need to be prepared and docked to the target. Use your favourit docking workflow for this step. Once docking is completed, you should rearrange the results in three sdf files with names starting with the original sets where they come from (for example, validation_docked.sdf, training_docked.sdf, test_docked.sdf) and place them in a subfolder called 'docked' inside the iteration folder.


### Phase 2. Neural network training
In phase 2, different deep learning models are trained on the docking scores from the previous step.

#### Run phase 2
```bash
python Extract_labels.py -if is_final_iteration? -n_it current_iteration -protein project_name -file_path path_to_project_without_name -t_pos total_processors -score score_keyword
python simple_job_models.py -n_it current_iteration -mdd morgan_directory -time 00-04:00 -file_path project_path -nhp num_hyperparameters -titr total_iterations -n_mol num_molecules --percent_first_mols percent_first_molecules -ct cutoff_threshold --percent_last_mols percent_last_mols
```

### Phase 3. Selection of best model and prediction of the entire database
In phase 3 the models from phase 2 are evalauted and the best performing one is chosen for predicting scores of all the molecules in the database. This step will create a morgan_1024_predictions subfolder which will contain all the molecules that are predicted as virtual hits in the current iteration.

#### Run phase 3
```bash
python -u hyperparameter_result_evaluation.py -n_it current_iteration --data_path project_path -mdd morgan_directory -n_mol num_molecules
python simple_job_predictions.py -protein project_name -file_path path_to_project_without_name -n_it current_iteration -mdd morgan_directory

```









