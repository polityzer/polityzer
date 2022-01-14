# Polityzer
A framework to semi-automatically analyze the privacy practices of election campaigns. This repo contains the source code to the automated part, the datasets collected for the analysis of the 2020 election, as well as the results of the analysis. 

## Dependencies
Polityzer supports building the project via [poetry](https://python-poetry.org/). 
All required dependencies are listed in pyproject.toml under _tool.poetry.dependencies_. 
If using poetry, simply run <code> poetry install </code> to install dependencies.
If poetry is not used, you can also install the dependency individually via <code>pip install</code>. 

## Folder Structure
<code>polityzer_tool</code> folder contains all the relevant source code. <code>datasets_2020</code> contains the datasets while the <code>results</code> folder contains the results. 

## How to use Polityzer
1. Install all the dependencies. 
2. Move to the project folder i.e., <code>polityzer_tool</code> folder. 
3. List the candidates to be downloaded in the <code>database/candidate_office_website.csv</code> file. This is the main input. 
4. Configure any parameter as needed in <code>config.py</code>. 
5. Run <code>python polityzer.py</code>.

**NOTE:** By default, <code>config.py</code> is set to download the websites, check/extract privacy policies, check/extract all outbound links, and finally, check/extract data types from the input forms. To skip any step, set the relevant flag to 0. 

### Results
After Polityzer finishes, the results are stored in the <code>results</code> folder. The logfiles are stored at <code>logs</code> folder. The html files are stored in the <code>html</code> folder. The path to all the files are stored at <code>database/downloaded_websites.csv</code>. 