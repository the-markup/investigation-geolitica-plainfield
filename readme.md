# Prediction: Bias follow-up

## How we assessed the accuracy of predictive policing software

The repository contains code and data supporting The Markup's investigation, ["Predictive Policing Software Terrible At Predicting Crimes."](https://themarkup.org/prediction-bias/2023/10/02/predictive-policing-software-terrible-at-predicting-crimes) Read our [methodology](https://themarkup.org/prediction-bias/2023/10/02/how-we-assessed-the-accuracy-of-predictive-policing-software) to understand the context for the code and data in this repository.

For the analyses in this repository, we use Geolitica (formerly PredPol) prediction data from our previous investigation, [Prediction: Bias](https://github.com/the-markup/investigation-prediction-bias), as well as crime reports obtained from the Plainfield, New Jersey police department (PD).

Using that data, the code in this repository carries out the following functions:
- Join Geolitica's predictions to the crime reports we received from Plainfield PD for the same time period
- Calculate the software's crime prediction success rate

### Repository contents

| File/Folder | Description |
| ----------- | ----------- |
| `Makefile` | Lists all steps taken to prepare data for analysis conducted in notebooks |
| `scripts/` | Folder contains code used to prepare data for analysis; takes files from `data/inputs` and `data/manual` as inputs and saves generated dataframes in `data/processed` |
| `notebooks/` | Folder contains analysis notebook |

#### `data/` folder

| File | Description |
| ---- | ----------- |
| `inputs/plainfield_dosage.csv` | Dosage data received from Plainfield PD |
| `inputs/plainfieldpdnj-geojson-with-data.json` | Shapefile of Plainfield census block groups, with race and household income demographics |
| `inputs/plainfield_predictions_with_shifts.csv` | Geolitica predictions for Plainfield from 2018 to 2020 |
| `manual/vague-addresses.csv` | Spreadsheet of manually checked addresses to exclude from analysis |
| `processed/crime_with_predictions.csv` | Crime reports with columns describing whether crime type could have been predicted by Geolitica software and whether crime reports had any associated predictions |
| `processed/predictions_with_crime_dosage.csv` | Geolitica predictions with columns describing whether crime report was generated during that prediction |

## Reproducibility

Reproducing the notebook’s calculations requires having Python 3.8 or greater installed on your computer and installing the Python libraries defined in this repository’s `requirements.txt` file, ideally in a Python virtual environment. To re-run the scripts and notebooks, use the command `make reproduce`. You can also open the notebooks in Jupyter and run them manually.
