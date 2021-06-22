# SiteMapPython

<br>

*Building*

* Ensure you have java 1.8
Enter in Command Prompt
```bash
java -version
```
if not get it here </br>
https://www.oracle.com/java/technologies/javase/javase-jdk8-downloads.html

* Download Tika (if you need to parse pdfs) </br>
https://www.apache.org/dyn/closer.cgi/tika/2.0.0-BETA/tika-2.0.0-BETA-src.zip </br>
Extract the contents in the Java/bin directory on your system (eg. C:\Program Files(x86)\Java\bin\). </br>

* Set the server path </br>
Enter in Command Prompt
```bash
set TIKA_SERVER_JAR="file:////tika-server.jar"
```

* Build the Qt Application
```bash
pyinstaller --onefile --windowed --icon=sitemapLogo.ico --name=SiteMap.exe --hidden-import=lxml 
--hidden-import=simplekml --hidden-import=tika -c cli.py
```
<hr>

*Dev Dependencies*
* python3
* pip3
* pyinstaller

```bash
pip3 install pyinstaller
 ```
* PyQt5
```bash
pip3 install pyqt5
```
* simplekml
```bash
pip3 install simplekml
```
* lxml
```bash
pip3 install lxml
```
* tika
```bash
pip3 install tika
```
