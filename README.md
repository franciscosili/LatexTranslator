# LaTeX Translator

This repository makes translations of LaTeX files between two languages.

## Setup

To use, first create a conda environment as

```bash
conda env create -f environment.yaml
```

If not, you will find the dependencies in `requirements.txt`. This will install the `requests` and `deepl` python submodule, that will allow the translation.

You will need to provide an API key, please place it in the `setup_deepl.sh` file

## Translation

The process is divided into three steps:

1. Encode the LaTeX file:
   In this step all the commands and environments of the .tex file will be enconded using the following pattern: `#<number>#`, and an output `.CODED.tex` file is created. It will also output a `.json` file with the hash and what it encodes.
2. Translate:
   In this step the translation takes place. There are two ways to make the translation: full, or paragraph by paragraph. Since the DeepL API has a character limit, I reccommend to use the step-by-step procedure, to avoid making translations of the hashes. This step makes use of the CODED latex file, and outputs the same CODED file but with the translations.
3. Decoding:
   Now it's time to put back all the commands and envs to their places. This is achieved by simply running over the .json dict and replacing back the content into the translated file. You need to specify the name of the output file. In case it's not provided, the addon '_translated' will be added.
