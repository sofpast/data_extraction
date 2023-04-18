# Introduction 
The project aims to (TBD)

Project Structure (to be updated)
---------------------------------
```text
./
├── models/                                     <- Models in the project
│   ├── extraNer/                               <- Extra NER model class
│   │	└── flair_ner.py
│   │
│   ├── layoutlmft/                             <- LayoutXLM class
│   │   └── models/
│   │       ├── layoutlm/
│   │       ├── layoutlmv2/
│   │       ├── layoutxlm/
│   │		└── model_args.py
│   │
│   ├── relationml/                             <- Relation Model class
│   │   └── rel.py
│   │
│   ├── weights/                                <- Weights/ trained models
│   │   ├── extra_ner/
│   │   ├── ner/
│   │   └── rel/
│   │
│   ├── configs.py                              <- Configuration 
│   ├── logger.py                               <- Define which log level will be printed 
│   ├── predict_extra_ner.py                    <- Inference source code of extra NER
│   ├── predict_ner.py                          <- Inference source code of LayoutXLM NER
│   ├── predict_rel.py                          <- Inference source code of Relation Model
│   ├── processor.py                            <- Inference source code of processor to encode images by using tokenizer
│   └── utils.py                                <- Auxiliary functions
│   
├── predict_kv.py                               <- Inference source code
├── README.md                                   <- README for inference
|── RELEASE_NOTES.md                            <- Release notes
└── requirements.txt                            <- Package requirements
```

# Getting Started

## Package requirement
>- Python 3.8.16
>- azure-ai-textanalytics==5.2.1
>- gremlinpython==3.4.13
>- spacy==3.5.1

## Installation process
First, create an Anaconda environment then install the environment by using `requirements.txt` and other packages as the commands below.

1. Create new environement
```bash
conda create --name hackathon python==3.8.16
```
Activate the environement
```bash
conda activate hackathon
```
2. Install requirements
```bash
pip install -r requirements.txt
```
3. Install other packages

Besides packages listed in `requirement.txt`, `spacy` is required for some step in tokenizing the documents into sentences. To install spacy, use the command below:

* Install spacy
```bash
pip install -U pip setuptools wheel
pip install -U spacy
python -m spacy download en_core_web_sm
```
* Install stanford_openie
`stanford_openie` is used to extract a triple (subject-verb-object) from a sentence, this is an important step to find the relation between two entities. The installation of stanford_openie would be done by using `pip install stanford_openie` version specified in `requirement.txt` but you need to ensure that Java JDK is already installed in your computer.

To check and install JDK version, please access to the link: [Download JDK](https://www.oracle.com/java/technologies/downloads/)

4. Download the weights
  - ner_weight (models/weights/ner): LayoutXLM NER model weights and others required by tokenizer
  - rel_weight (models/weights/rel): Relation extraction model weights and scaler
  - extraNER_weight (models/weights): extraNER model weights

Access here [link](https://eastgatesoftware.sharepoint.com/:u:/s/PROJECTACTINEOProject2/EcjaVwyiYVVFvaIj_gmV6NgBi-T4XkZuZnNCX5DS2MkqaQ) to download all the weights then place them into the folder `models`

# Run Inference
Use the command below to run the inference
```bash
python predict_kv.py --input_folder <path_to_input_folder> \
                     --output_folder <path_to_output_folder> \
                     --save_debug \
                     --mode <"inference" or "eval">
```

In which:
- `--input_folder`: type=str, help="Path to input folder"
- `--output_path`: type=str, help="Path to output folder"
- `--save_debug`: action='store_true', help="Save debug output". If "--save_debug" is not selected, the default is FALSE.
- `--mode`: type=str, default="inference", help="Run mode (inference/eval)". Mode is added to satisfy the input requirements of both inference and evaluation modes.

Example:

```bash
# output debug and inference mode
python predict_kv.py --input_folder data/test_unseen_v4 \
                     --output_folder nhung/output_test_unseen_v4 \
                     --save_debug \
                     --mode inference

# no debug and inference mode
python predict_kv.py --input_folder data/test_unseen_v4 \
                     --output_folder nhung/output_test_unseen_v4 \
                     --mode eval
```

# Model Architectures
The project contains 3 models as below:
- Model 1 - Semantic/ Name Entity Recognition (SER/NER): to classify texts into 4 classes including (OTHER, HEADER, QUESTION, ANSWER) --> final outputs of SER/NER is a list of entities (QUESTION, ANSWER). It was based on [LayoutXLM Hunggingface transformers](https://huggingface.co/docs/transformers/model_doc/layoutxlm) by Microsoft 

- Model 2 - Relation Extraction (REL): to classify the relation between every pair of question/ answer (None or KV), it is a machine learning model by using RandomForest

- Model 3 - extraNER: use pre-trained model to extract some basic classes from the entities ANSWER

Path to those models are listed in `configs.py`

