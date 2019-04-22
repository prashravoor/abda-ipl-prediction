# IPL Match Prediction using Machine Learning

## Requirements
Python 3.6+ <br>
Sklearn <br>
TODO: Add any missing requirements into requirements.txt <br>

## Setup
After cloning the repo, install necessary modules through `pip install -r requirements.txt` <br>
Extract the contents of `yaml.zip` into the `yaml` folder <br>

## Running
Simply run the driver file `train_data.py` to perform all the necessary functions <br>

## Prediction
Save the playing XI for both teams in the `data` directory, as file `<team_name>.csv` as a list of names separated by comma (Some example files are added to the repo), for e.g. `rcb.csv`, `kkr.csv` etc.. The order specified in the file will be the batting order for the teams. The bowler selection is predicted based on past statistics. <br>
<br> 
Run the script `match_simulator.py` to start the match prediction <br>
Enter the team names using just the 3 or 2 letter prefix used to save the team file (Like kkr, rcb) <br>
The prediction will then run to completion, and displays the result <br>
