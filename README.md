# TCdata360PubGenerator
Generates Datascope_TnC_Publications.csv using input files

**Input files:**
- Copy of TC%20Related%20Publications%20from%20FY12_FY17_as%20of%20June%2020.xls (Needs FRESH DOWNLOAD every year from IFC intranet. Note that this file SHOULD be in XLS format, not XLSX.)
- CountryClassification.csv (Reference file. No need to be updated.)
- TC_Publications-category_mapping.csv (FOR UPDATING by T&C data scientist)

**Output file:** Datascope_TnC_Publications.csv

===

**Improvements from R version (Datascope_publications.R):**
- Updated Category keyword matching based on latest TCdata360 categories
- Allows multiple country matches based on publication Title
- Process doesn't require the usage of a separate excel file (TnC_PublicationsSharepoint.xlsm) to extract URLs from Excel cells. The Python code extracts the URLs by itself.
