# RespyHRV

## Main goals
- extract respiration cycles from a respiration signal
- visualize and extract metrics of respHRV, also known as RSA (Respiratory Sinusal Arrhythmia)
- Simplify access to signal analysis through a web interface

## Limitations
- Only handles files from BioSemi modules (.bdf or .edf)
- Specialized in respiration signals from with piezoelectric sensor

## References
This project would be nothing without the <a href='https://github.com/samuelgarcia/physio'>physio</a> projet that does the work for ECG and RSA analyses, and <a href='https://github.com/plotly/dash'>Dash</a> that generates the interactives plots and the webserver.

## Note
The project is supposed to be improved soon to simplify installation and extend the file types handled.
