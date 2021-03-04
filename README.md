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
Databases for DD should be in SMILE format. For each compound of the database, DD requires the Morgan fingerprints of radius 2 and size 1024 bits, represented as the list of the indexes of bits that are set to 1. First, it is recommended to split the SMILES into a number of evenly populated files to facilitate other steps such as random sampling and inference, and place these files into a new folder. This reorganization can be achieved for example with the *split* command in bash, and the resulting files should have txt extensions. For example, considering a *smiles.smi* file with 1 billion of compounds, to obtain 1000 evenly splitted txt files of 1 million lines each:

```bash
split -l 1000000 smiles.smi smile_all_ --additional-suffix=.txt
```

Ideally the number of final files should be equal to the number of CPUs used for random sampling (phase 1, see below) and always larger than the number of GPUs used for inference (phase 3, see below). 

Morgan fingerprints can be then generated in the correct DD format using the *Morgan_fing.py* script (TO ADD in Utilities):

```bash
python Morgan_fing.py -sfp path_smile_folder -fp path_to_morgan_folder -fn name_morgan_folder -tp num_cpus
```
ADD HELP TOO

### Phase 1. Random sampling of molecules
In phase 1 molecules are randomly sampled from the database to build or augment the training set. During the first iteration, molecules are also sampled for generating the validation and test sets.

#### Run phase 1
To run phase_1, run the following sequence of scripts for random sampling of the database, and for extracting Morgan fingerprints and SMILES of the sampled molecules:

```bash
python molecular_file_count_updated.py -pt project_name -it current_iteration -cdd left_mol_directory -t_pos num_cpus -t_samp molecules_to_dock
python sampling.py -pt project_name -fp path_to_project_without_name -it current_iteration -dd left_mol_directory -t_pos total_processors -tr_sz train_size -vl_sz val_size
python sanity_check.py -pt project_name -fp path_to_project_without_name -it current_iteration
python Extracting_morgan.py -pt project_name -fp path_to_project_without_name -it current_iteration -md morgan_directory -t_pos total_processors
python Extracting_smiles.py -pt project_name -fp path_to_project_without_name -it current_iteration -fn 0 -smd smile_directory -sd NA -t_pos num_cpus -if True/False
```
SANITY CHECK MISSING

* *molecular_file_count_updated.py* determines the number of molecules to be sampled from each file of the database, according to the desired number of molecules to sample. The sample sizes (per million) are stored in *Mol_ct_file_updated.csv* file created in the left_mol_directory directory.

* *sampling.py* randomly samples the desired number of molecules for training, validation and test set during the first iteration, and for training only from the second iteration onwards. 

**IMPORTANT NOTE FOR *molecular_file_count_updated.py* AND *sampling.py*:** left_mol_directory is the directory from where molecules are sampled; for iteration 1, left_mol_directory is the directory storing the Morgan fingerprints of the database; for any other iteration, this must be the path to *morgan_1024_predictions* folder of the previous iteration; for example, in iteration 2

```bash
python molecular_file_count_updated.py -pt project_name -it current_iteration -cdd /path_to_project/project_name/iteration_1/morgan_1024_predictions -t_pos num_cpus -t_samp molecules_to_dock
python sampling.py -pt project_name -fp path_to_project_without_name -it current_iteration -dd /path_to_project/project_name/iteration_1/morgan_1024_predictions -t_pos total_processors -tr_sz train_size -vl_sz val_size
```
This will ensure that sampling is done progressively on better scoring subsets of the database over the course of DD.

* *sanity_check.py* removes overlaps between sampled sets.

* *Extracting_morgan.py* and *Extracting_smiles.py* scripts extract aorgan fingerprints and SMILES for the compounds that have been randomly sampled, and organize them in *morgan* and *smiles* folders inside the directory of the current iteration.


### After phase 1. Docking
After phase 1 is completed, molecules grouped in the smiles folder need to be prepared and docked to the target. Use your favourite docking workflow for this step. Once docking is completed, you should rearrange the results in three sdf files with names containing the names of the original sets where the molecules come from (for example, validation_docked.sdf, training_docked.sdf, test_docked.sdf) and place them in a subfolder called 'docked' inside the current iteration folder.


### Phase 2. Neural network training
In phase 2, deep learning models are trained on the docking scores from the previous step.

#### Run phase 2
```bash
python Extract_labels.py -if True/False -n_it current_iteration -protein project_name -file_path path_to_project_without_name -t_pos num_cpus -score score_keyword
python simple_job_models.py -n_it current_iteration -mdd morgan_directory -time 00-04:00 -file_path project_path -nhp num_hyperparameters -titr total_iterations -n_mol num_molecules --percent_first_mols percent_first_molecules -ct cutoff_threshold --percent_last_mols percent_last_mols
```
* *Extract_labels.py* extracts docking scores and organizes them to be used for model training. It should generate three comma-spaced files, training_labels.txt, validation_labels.txt and testing_labels.txt inside the current iteration folder.

* *simple_job_models.py* creates bash scripts to run model training using the *progressive_docking.py* script. Those scripts are generated inside the *simple_job* folder in the current iteration.

The bash scripts generated by *simple_job_models.py* should be then run on GPU nodes to train DD models. The resulting models will be stored in the *all_models* folder in the current iteration.

### Phase 3. Selection of best model and prediction of the entire database
In phase 3 the models from phase 2 are evalauted and the best performing one is chosen for predicting scores of all the molecules in the database. This step will create a morgan_1024_predictions subfolder which will contain all the molecules that are predicted as virtual hits in the current iteration.

#### Run phase 3
```bash
python -u hyperparameter_result_evaluation.py -n_it current_iteration --data_path project_path -mdd morgan_directory -n_mol num_molecules
python simple_job_predictions.py -protein project_name -file_path path_to_project_without_name -n_it current_iteration -mdd morgan_directory

```

* *hyperparameter_result_evaluation.py* evaluates the models generated in phase 2 and select the best (most precise) one

* *simple_job_predictions.py* creates bash scripts to run prediction over the full database. Those scripts will be stored in the *simple_job_predictions* folder of the current iteration.

The generated bash scripts can be run on GPU nodes to predict virtual hits from the full database. Predicted compounds will be stored in *morgan_1024_predictions* folder of the current iteration.








