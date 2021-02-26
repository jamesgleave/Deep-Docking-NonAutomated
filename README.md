# Deep-Docking-NonAutomated

Deep docking (DD) is a deep learning-based tool developed to accelerate docking-based virtual screening. Using NVIDIA's own Autodock-GPU,  one can screen extensive chemical libraries like ZINC15 (containing > 1.3 billion molecules) {how much faster is it than just docking?} times faster than typical docking. For further details into the processes behind DD, please refer to our paper (https://doi.org/10.1021/acscentsci.0c00229). 

## Requirements
* Docking Program
* tensorflow >= 1.14.0
* pandas
* numpy
* keras
* matplotlib
* scikit-learn


## Usage

### Phase 1. Random sampling of molecules
Description of phase 1...


#### Run phase 1
```bash
python jobid_writer.py -file_path path_to_project -n_it current_iteration -jid job_id -jn job_name
python molecular_file_count_updated.py -pt project_name -it current_iteration -cdd prediction_directory -t_pos total_processors -t_samp molecules_to_dock
python sampling.py -pt project_name -fp path_to_project_without_name -it current_iteration -dd prediction_directory -t_pos total_processors -tr_sz train_size -vl_sz val_size
python sanity_check.py -pt project_name -fp path_to_project_without_name -it current_iteration
python Extracting_morgan.py -pt project_name -fp path_to_project_without_name -it current_iteration -md morgan_directory -t_pos total_processors
python Extracting_smiles.py -pt project_name -fp path_to_project_without_name -it current_iteration -fn 0 -smd smile_directory -sd sdf_directory -t_pos total_processors -if is_final_iteration?
```
  
### Phase 2. Neural network training
description of phase 2...

#### Run phase 2
```bash

python Extract_labels.py -if is_final_iteration? -n_it current_iteration -protein project_name -file_path path_to_project_without_name -t_pos total_processors -sof docking_software
python simple_job_models.py -n_it current_iteration -mdd morgan_directory -time 00-04:00 -file_path project_path -nhp num_hyperparameters -titr total_iterations -n_mol num_molecules --percent_first_mols percent_first_molecules -ct cutoff_threshold --percent_last_mols percent_last_mols
```

### Phase 3. Selection of best model and prediction of the entire database
description of phase 3...

#### Run phase 3
```bash
python -u hyperparameter_result_evaluation.py -n_it current_iteration --data_path project_path -mdd morgan_directory -n_mol num_molecules
python simple_job_predictions.py -protein project_name -file_path path_to_project_without_name -n_it current_iteration -mdd morgan_directory

```









