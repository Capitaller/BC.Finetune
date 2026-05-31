# BC.Finetune

BC.Finetune prepares Microsoft Dynamics 365 Business Central AL source code for continued pretraining of Gemma 4 E2B in Kaggle.

The repository keeps the original Business Central source export out of git and generates a plain-text training file for the Kaggle notebook.

## Layout

- `Base Application.Source/` - local Business Central Base Application source export. This folder is ignored by git.
- `scripts/convert_al_to_text.py` - converts `.al` files into text training data.
- `data/bc_al_text/files/` - mirrored `.txt` files generated from `.al` files.
- `data/bc_al_text/business_central_al_training_text.txt` - combined AL training text file to upload as a Kaggle Dataset for the notebook.
- `nb/Gemma4_E2B_BC_CPT.ipynb` - Gemma 4 E2B continued-pretraining notebook for BC AL code in Kaggle.

## Generate The Corpus

Run the converter from the repository root:

```bash
python3 scripts/convert_al_to_text.py
```

To preview the conversion without writing files:

```bash
python3 scripts/convert_al_to_text.py --dry-run
```

By default, the script reads from `Base Application.Source/` and writes to `data/bc_al_text/`. It creates one `.txt` file per `.al` file under `data/bc_al_text/files/`, preserving the relative source folders, and also creates `data/bc_al_text/business_central_al_training_text.txt` with file-boundary markers.

## Kaggle Training Notebook

The notebook does not load training data from this local repository. It expects `business_central_al_training_text.txt` from an attached Kaggle Dataset.

1. Generate `data/bc_al_text/business_central_al_training_text.txt` locally.
2. Upload `business_central_al_training_text.txt` as a Kaggle Dataset.
3. Attach that Dataset to the Kaggle notebook.
4. Open `nb/Gemma4_E2B_BC_CPT.ipynb` in Kaggle.
5. If needed, set `KAGGLE_TRAINING_TEXT_PATH` in the data-loading cell to the exact path, for example `/kaggle/input/bc-al-training-text/business_central_al_training_text.txt`.

The notebook is configured for raw continued pretraining:

- It trains on plain AL source text, not chat messages.
- It does not use response-only masking.
- It adds EOS tokens to chunks for completion-style training.
- It targets Gemma 4 E2B with Unsloth.

## Data And Licensing

The Business Central source export and generated training text are ignored because they may be large and may be governed by separate Microsoft licensing terms. Keep those files local unless you have explicit rights to publish or share them.
