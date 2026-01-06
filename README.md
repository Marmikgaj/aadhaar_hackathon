# UIDAI(Aadhaar) Data Hackathon - 2026

A comprehensive data analysis project for exploring and modeling Aadhaar-related datasets, including biometric, demographic, and enrolment information.

## 📋 Project Overview

This project analyzes three key datasets related to Aadhaar:

- **Biometric Data**: Contains biometric information (1,861,108 records)
- **Demographic Data**: Contains demographic information (2,071,700 records)
- **Enrolment Data**: Contains enrolment information (1,006,029 records)

## 📁 Project Structure

```
aadhaar_hackathon/
├── Data/
│   ├── Combined_CSV/              # Merged CSV files
│   │   ├── api_data_aadhar_biometric_combined.csv
│   │   ├── api_data_aadhar_demographic_combined.csv
│   │   └── api_data_aadhar_enrolment_combined.csv
│   ├── Raw_Data/                  # Raw data split into chunks
│   │   ├── api_data_aadhar_biometric/
│   │   ├── api_data_aadhar_demographic/
│   │   └── api_data_aadhar_enrolment/
│   └── merge.ipynb                # Notebook for merging raw data
├── model.ipynb                    # Main analysis notebook
├── requirements.txt               # Python dependencies
├── LICENSE                        # MIT License
└── README.md                      # This file
```

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Installation

1. Clone the repository:

```bash
git clone https://github.com/Marmikgaj/aadhaar_hackathon.git
cd aadhaar_hackathon
```

2. Create a virtual environment (recommended):

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install required packages:

```bash
pip install -r requirements.txt
```

## 💻 Usage

### Running the Analysis

1. Open the main analysis notebook:

```bash
jupyter notebook model.ipynb
```

2. Run the cells sequentially to:
   - Load the three datasets
   - View dataset summaries and statistics
   - Perform data analysis and modeling

### Data Processing

The project includes combined CSV files ready for analysis. If you need to re-merge the raw data chunks:

1. Navigate to the Data directory
2. Open `merge.ipynb` to combine raw data files

## 📦 Dependencies

- `pandas==2.3.3` - Data manipulation and analysis
- `numpy==2.4.0` - Numerical computing
- `python-dateutil==2.9.0.post0` - Date/time utilities
- `pytz==2025.2` - Timezone support
- `tzdata==2025.3` - Timezone database

## 📊 Dataset Information

| Dataset     | Rows      | Source Files |
| ----------- | --------- | ------------ |
| Biometric   | 1,861,108 | 4 chunks     |
| Demographic | 2,071,700 | 5 chunks     |
| Enrolment   | 1,006,029 | 3 chunks     |

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

<!-- - Marmik Gajbhiye
 -->
<a href="https://github.com/Marmikgaj">
    <img src="https://github.com/Marmikgaj.png" width="100px;"  style="border-radius:50%;" alt="Marmik Gajbhiye"/><br/>
    <sub><b>Marmik Gajbhiye</b></sub>
</a>

## 🤝 Contributor <!--List -->

<div align="left">
  <table>
    <tr>
      <td align="center">   
        <a href="https://github.com/theanant404">
          <img src="https://github.com/theanant404.png" width="100px;" style="border-radius:50%;" alt="Anant Kumar"/><br/>
          <sub><b>Anant Kumar</b></sub>
        </a>
      </td>
            <td align="center">   
        <a href="https://github.com/NickyY28">
          <img src="https://github.com/NickyY28.png" width="100px;" style="border-radius:50%;" alt="Nicky Yadav"/><br/>
          <sub><b>Nicky Yadav</b></sub>
        </a>
      </td>
            <td align="center">   
        <a href="https://github.com/TheCodeLord-INX">
          <img src="https://github.com/TheCodeLord-INX.png" width="100px;" style="border-radius:50%;" alt="Aditya Vaidhya IITM"/><br/>
          <sub><b>Aditya Vaidhya</b></sub>
        </a>
      </td>
      <td align="center">
        <a href="https://github.com/as-ga">
          <img src="https://github.com/as-ga.png" width="100px;"  style="border-radius:50%;" alt="Ashutosh Gaurav"/><br/>
          <sub><b>Ashutosh Gaurav</b></sub>
        </a>
      </td>
      </tr>
  </table>
</div>

## 🙏 Acknowledgments

- Aadhaar Hackathon organizers
- Data providers

---

**Note**: This project is developed for educational and research purposes as part of a hackathon.
