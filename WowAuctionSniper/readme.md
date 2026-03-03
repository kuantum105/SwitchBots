# World of Warcraft Auction Sniper

The purpose of this is to target a specific commodity on the auction house and to purchase it whenever it drops below a specified price. 

## Installation

### WoW Setup 

* Set your UI Scale to 90% in Options → Game → Graphics → Use UI Scale 
* Download the AIRLAN.tff and FRIZQT__.tff font files
* Place the downloaded font files in your `WOW Install Folder/_anniversary_/Fonts`

### Script Setup 

* `py -m pip install -r .\requirements.txt`

### CUDA & PyTorch Setup 
* Follow the instructions on https://pytorch.org/
* Ensure that you have installed a compatible version of CUDA from https://developer.nvidia.com/cuda-toolkit-archive

### Custom Modifications 

* At the top of the script, modify your `min_quantity` and `purchase_limit`

## Usage Instructions

* Open the auction house 
* Search for your exact, desired item
* Ensure that you are set to sorting by Buyout and Unit Price 
* Ensure that it is sorted to lowest first

### To stop the script 

* Close the Auction House by pressing `ESC`