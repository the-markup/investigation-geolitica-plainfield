.PHONY: reproduce analysis

reproduce: data/processed/predictions_with_dosage.csv analysis

##  Run the prediction accuracy assessment notebook.
analysis:
	nbexec notebooks/pred-accuracy-assessment.ipynb

requirements.txt: requirements.in
	pip-compile requirements.in

data/processed/predictions_with_dosage.csv: scripts/match-dosage-to-preds.py data/inputs/plainfield_dosage.csv data/inputs/plainfield_predictions_with_shifts.csv
	python scripts/match-dosage-to-preds.py
