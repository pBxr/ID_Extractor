# ID_Extractor (ID_Ex) for extracting IDs and references from `jats` article files

## Introductory remarks
Several scientific journals edited by the German Archaeological Institute use `jats xml` to be displayed in an instance of the eLife Lens 2.0.0 (for example _Archäologischer Anzeiger_, see: https://publications.dainst.org/journals/aa). 
The articles are enhanced with bibliographic and geographic authority data as well as other references to specific information resources of the institute´s information infrastructure.

## Approach
ID_Ex browses the `.xml` files stored in the article repository folder and extracts the pre-defined references. The results are stored in separate `sqlite3` tables reflecting the relation of a specific record to the `doi` of the article, e. g. from
- bibliographic records (zenon-IDs, see https://zenon.dainst.org/), 
- geographic authority data (gazetteer-IDs, see https://gazetteer.dainst.org/),
- or records of other entities like objects (iDAI.objects-IDs, see https://arachne.dainst.org/) or records from archaeological fieldwork documentation systems (iDAI.field-IDs, see https://field.idai.world/).

ID_Ex is based on `Python 3.12.0` using `bs4` from `BeautifulSoup` library, so it can be easily modified for own purposes.

## Mode of operation - and things to be done
If not existing, ID_Ex generates the required `sqlite3` tables in a subfolder ("db_folder") when starting the tool for the first time. In the initial version of ID_Ex you have to enter the path to the repository folder in which the `.jats` files are stored manually. ID_Ex extracts the data and saves them in mentioned `sqlite3` tables. 
To avoid duplicates ID_Ex checks if an article is already recorded using the `doi` and skipps in this case further actions. 
Additionally ID_Ex generates a detailed `.txt` log file containing the file names and the IDs extracted from them in a subfolder ("_ID_Ex_LOG").
With minor modifications ID_Ex can be run at certain intervalls (using a CronJob for example) to keep the corpus up to date automatically.

## New in v1.1.0:
- A menue allows to export the records of a selected table into a `.txt` file in the log subfolder, not only after the extraction process but also in form of a request to a previous generated database
- Improved handling of the parameters needed for `sqlite3` operations using a `dict` that contains all necessary informations to minimize repetitions

## To be done:
- Enable automatical scraping of scattered repositories containing `.jats` article files.
- Adding step by step features to export the records as `.json` files or in other formats.
- Enable ID_Ex to handle more complex queries and requests
- Implement a mode of running autonomously to make ID_Ex usable within a CronJob

## Technical remarks 
- `Python 3.12.0`
- `bs4` from `BeautifulSoup`
- `sqlite3`
- Tested for Windows (not for Linux yet)

## See also
In this context see following repositories for preparing the `.jats` files of the journals mentioned above:
- TagTool_WiZArD application (ttw), see https://github.com/pBxr/TagTool_WiZArd
- Web Extension for TagTool_WiZArD application (ttw_webx), see https://github.com/pBxr/ttw_WebExtension
