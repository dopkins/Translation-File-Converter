# Translation-File-Converter
A small program to convert source files into formats usable by standard CAT (computer aided translation) software.

The script contains several imports. Make sure you have them all installed before running it. The script runs on Python 2.7. 
The markdown package must be installed separately.

lang.txt contains the localized interface texts for the program. It is required in order to run atfc.py.

Types of conversion: 
MD -> HTML: Takes a ZIP file containing a directory of Markdown documents as input and converts all MDs into a single HTML. Warning: The resulting document cannot currently be converted back into pure Markdown. 

HTML -> MD: Takes a (translated) HTML file and the original ZIP file from the previous step and separates the HTML into individual quasi-MD documents. Images and other files from the ZIP are sorted into the correct directory. The resulting documents are not MD, but they should display properly on a website.

uit -> XML: Not currently implemented. Designed to convert proprietary UIT interface texts into a translation-friendly XML format.

XML -> uit: Not currently implemented. Designed to convert the translated version of the XML from the previous step back into the proprietary UIT format.

Javadoc -> HTML: Takes a ZIP file containing a Javadoc export as import and converts all HTML files within into a single HTML. Each individual HTML is enclosed in a specific tag containing the path to the file.

HTML -> Javadoc: Takes a (translated) HTML file based on the previous conversion and separates the HTML into individual HTML files in their original directory path. All other files are copied from the ZIP to their corresponding directory. 
