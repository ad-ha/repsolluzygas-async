[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
![GitHub Release (latest SemVer including pre-releases)](https://img.shields.io/github/v/release/ad-ha/repsolluzygas-async?include_prereleases)
![GitHub Downloads (all assets, latest release)](https://img.shields.io/github/downloads/ad-ha/repsolluzygas-async/latest/total)

[![HACS Action](https://github.com/ad-ha/repsolluzygas-async/actions/workflows/hacs.yml/badge.svg)](https://github.com/ad-ha/repsolluzygas-async/actions/workflows/hacs.yml)
[![Validate with hassfest](https://github.com/ad-ha/repsolluzygas-async/actions/workflows/hassfest.yml/badge.svg)](https://github.com/ad-ha/repsolluzygas-async/actions/workflows/hassfest.yml)

# REPSOL LUZ Y GAS API for Home Assistant

Custom Integration for Home Assistant to connect and display data for Electricity, Gas and SVA Contracts with Repsol Luz y Gas.

This integration is based on the initial integration done by [bbzoiro](https://github.com/bzzoiro/repsolluzygas)

## Description

This integration has been redesigned to implement async methods and to allow the configuration via configflow directly from Home Assistant UI. No need to keep doing configuration in YAML.

This also supports Multi-house and Multi-Contracts.

The current version supports the following:

![image](https://github.com/ad-ha/repsolluzygas-async/assets/59612788/e8be456f-2b27-4eb4-95f6-253908e2a185)

![image](https://github.com/ad-ha/repsolluzygas-async/assets/59612788/69bb3eee-b638-4e1c-8d37-e47436d7db78)


### Installation

#### - Manual method

- Download/clone this repo
- Copy the [custom_components/repsolluzygas](custom_components/repsolluzygas) folder into your custom_components folder into your HA installation
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
1.2.2
- Revise latest Virtual Battery Redeemed Sensors
```

```
1.2.1
- Add new sensors for ELECTRICITY Contracts:
  - Contract Status
  - Energy Price
  - Power Prices (Punta y Valle)
  - Power
  - Tariff
```

```
1.1.1
- Code cleanup
- Update API addresses to newest Repsol releases
- Move several constants to const.py
- Add Virtual Battery Device and Sensors:
  - Current Status (€ and kWh)
  - Last Redeemed Status (€ and kWh)
  - Total kWh Charges/Discharges 
```

```
1.0.1
- Code cleanup
- Add SVAs queries from API
- Move headers and other constants to const.py
- Add new SVAs device for each house
- Add SVAs sensors, in preparation for further developments
- Import headers
- Add HOUSES_URL for new SVA sensors
- Preparation for next releases and new contract detail sensors
```

```
0.1.4
- Revise logic to segregate data for different Contracts (hopefully it will now work)
- Remove Number of Contracts sensor, as it is now redundant information
```

```
0.1.3
- Revise logics to enable CUPS data and Contract Type
- Revise the sensor details to include:
 - Add Device info for each contract, including details on Contract Type and CUPS, plus House ID
 - Use Home Assistant core units (EUR and kWh)
 - Rename sensor to include CUPS
 - Update Unique ID coding
- Revise Config Flow to include CUPS on contract selection.
- Add logic to prevent adding the same contract multiple times.
- Add Spanish translations to Config Flow
- Update English labeling on Config Flow
```

```
0.1.1
- Initial Release
- Add Next Invoice Amount Sensor (includes Amount, Variable Amount and Fixed Amount)
- Add ConfigFlow configuration
- Add HACS Custom Repository Configuration
- Revised Average Amount to be pulled from API, instead of calculation
- Implement Unique_Id for each sensor. The sensors are now configurable from UI.
```


## TO-DO

- Official HACS Release to use without Custom Repositories (currently pending approvals)
- ~~Add new sensors for Power, Fee, Contract Description~~
- ~~Figure out the SVAs information from API (Virtual Battery for PV Contracts and Additional Services)~~
- ~~Implement Gas Sensors (if you have this type of contract, please contact me)~~
- ~~Check multicontract capabilities, although it should work fine~~
- ~~Add Device and append Contract Information (CUPS. House_id, Contract_id, etc..) as additional information~~
- ~~Units from Home Assistant instead of fixed ones~~
- ~~Address unique-ids for multicontracts, multihouses~~

## Credits
- [bbzoiro](https://github.com/bzzoiro/repsolluzygas) - The developer of the base integration

## License

This project is licensed under MIT License.

## Disclaimer

THIS PROJECT IS NOT IN ANY WAY ASSOCIATED WITH OR RELATED TO THE REPSOL GROUP OF COMPANIES OR ANY OTHER. The information here and online is for educational and resource purposes only and therefore the developers do not endorse or condone any inappropriate use of it, and take no legal responsibility for the functionality or security of your devices.

