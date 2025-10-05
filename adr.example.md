
+---------------------------------------------------------------------------------+
ADR:
Data ingestion & handling

+---------------------------------------------------------------------------------+
Context:
Setting up data processing and handling for the project "xyz". Goal is to keep
ingestion simple & reproducable

+---------------------------------------------------------------------------------+
Decision:
1) Data source
	- source: data from kaggle.com: this-fancy-data.csv by datamaker123
	- access through download/Kaggle CLI/API
	- license is CC0
	
2) Availability
	- SLO: Kaggle dataset release v2.1
	- (Batch) download once (or streaming), no usage of updates planned
	- raw data stored locally in /data/raw/
	
3) Privacy & security
	- open, public dataset under CC0. no privacy or security concerns

4) Volume & growth
	- File size: 8.7 GByte (local storage OK)
	- Fixed size, no growth (no continuous ingestion)
	- 

5) Quality checks
	- check on import using pandas (types, nan, outliers, categoricals, duplicates,..)
	- data leakage check for train/test split
	- curated by preprocessing pipeline in jupyter notebook, report logged in data
	  directory
	  
6) Versioning for training/testing
	- data versioning using DVC with MinIO object storage running in a docker container
	  on the local host
	  
7) Lineage tracking (source->raw->features)
	- track preprocessing pipelines by appending input (raw dataset name,version,...)
 	  and output data file along the quality report
	- enables traceability for generated dataset


+---------------------------------------------------------------------------------+
Consequences:

- Pro: ...
- Con: ...
- Tradeoffs: ...

Alternatives:
...

Implementation notes:
...


+---------------------------------------------------------------------------------+
Status:	open
+---------------------------------------------------------------------------------+
