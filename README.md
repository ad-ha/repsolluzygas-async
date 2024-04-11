[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
![GitHub Release (latest SemVer including pre-releases)](https://img.shields.io/github/v/release/ad-ha/repsolluzygas-async?include_prereleases)
![GitHub Downloads (all assets, latest release)](https://img.shields.io/github/downloads/ad-ha/repsolluzygas-async/latest/total)

# REPSOL LUZ Y GAS API for Home Assistant

Custom Integration for Home Assistant to connect and display data for Electricity Contracts with Repsol Luz y Gas.

This integration is based on the initial integration done by [bbzoiro](https://github.com/bzzoiro/repsolluzygas)

## Description

This integration has been redesigned to implement async methods and to allow the configuration via configflow directly from Home Assistant UI. No need to keep doing configuration in YAML.

This also supports Multi-house and Multi-Contracts.

The current version supports the following sensors:

![image](https://github.com/ad-ha/repsolluzygas-async/assets/59612788/44be4adc-d46e-4ef3-acd9-9977b3dd2900)


### Installation

#### - Manual method

- Download/clone this repo
- Copy the [custom_components/ide](custom_components/repsolluzygas) folder into your custom_components folder into your HA installation
- Restart HA

#### - [HACS](https://hacs.xyz/) method (recommended)

- Copy this repo URL
- In the HACS section, add this repo as a custom one:

  ![image](https://github.com/ad-ha/repsolluzygas-async/assets/59612788/6bd01379-d132-4193-989a-ba0985a25987)

  
  - On the "Repository" field put the URL copied before
  - On the "Category" select "Integration"
  - Click the "Download" button and download latest version. 
- Restart HA

## How to configure
[<img src="https://github.com/ad-ha/repsolluzygas-async/assets/59612788/e9d46e15-eee7-41e4-ba1b-bb09e9bbbcfd">](https://my.home-assistant.io/redirect/config_flow_start?domain=repsolluzygas)

- Go to Settings > Devices & Services > Add Integration > Repsol Luz y Gas
  ![image](https://github.com/ad-ha/repsolluzygas-async/assets/59612788/91309474-fdf5-4b7b-a73b-1d5d116fd0ab)

- Use your Username and Password

- Enjoy!

## Version History

```
0.1.1
- Initial Release
- Add Next Invoice Amount Sensor (includes Amount, Variable Amount and Fixed Amount)
- Add ConfigFlow configuration
- Add HACS Custom Repository Configuration
- Revised Average Amount to be pulled from API, instead of calculation
```


## TO-DO

- Implement Gas Sensors (if you have this type of contract, please contact me)
- Check multicontract capabilities, although it should work fine
- Address unique-ids for multicontracts, multihouses
- Official HACS Release to use without Custom Repositories
- Units from Home Assistant instead of fixed ones
- Figure out the SVAs information from API (Virtual Battery for PV Contracts and Additional Services)
- Add Device and append Contract Information (CUPS. House_id, Contract_id, etc..) as additional information


## Credits
- [bbzoiro](https://github.com/bzzoiro/repsolluzygas) - The developer of the base integration

## License

This project is licensed under MIT License.

## Disclaimer

THIS PROJECT IS NOT IN ANY WAY ASSOCIATED WITH OR RELATED TO THE REPSOL GROUP OF COMPANIES OR ANY OTHER. The information here and online is for educational and resource purposes only and therefore the developers do not endorse or condone any inappropriate use of it, and take no legal responsibility for the functionality or security of your devices.

