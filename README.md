# SWAP_analysis
Small tool to analyze SWAP redox sensor data. Cleaner and better documented version than the one implemented in `JoYvBa/MasterThesis/CW_data_analysis_scripts`.

Takes in an .xlsx/.xls or .csv/.dat file with the output data format of the SWAP redox sensors. Cleaning it up into a formatted DataFrame, then allows for visualization of the redox potential and soil temperature data.

- `CW_redox` -> Controller script with an example of how to use the functionalities using redox data from the Constructed Wetland pilot study.
- `tools` -> Module file with functions for reading in the files, cleaning them up and plotting the data. Also contains dictionaries to rename redox nodes to desired naming convention.
- `S9081 HMVT CR1000X_measurements.dat` -> Comma seperated file with redox and temperature data from the Constructed Wetland pilot study.
  
