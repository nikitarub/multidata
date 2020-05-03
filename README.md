# multidata
Collect different data simultaneously.


## Datasets folder

There are 3 datasets:
* 1 and 2 – collected at 10 fps of camera
* 3 – collected at 3 fps of camera and more emg data per frame
  
# Startup

## Backend Server
* In seperate terminal run: `python backcend/ws_server.py`
* In seperate terminal run: `python emd_server/emg_server.py`

## Frontend
* Install dependencies and run:
```bash
yarn 
yarn watch
```

Use controls to start, stop and save dataset

## TO DO
* add requirements.txt
* create ML model
* create prediction mode
* add script to run all
* dockerise
