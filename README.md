# ESODA Project
Project home for ESODA (http://www.esoda.org)

## Setup
* Install Python 2.7 and Java 8 is properly installed

* Install python packages

```shell
pip install -U -r requirements_x64.txt
```

* (Optional) Download and run the latest [Stanford CoreNLP Server](http://stanfordnlp.github.io/CoreNLP/corenlp-server.html)

```shell
java -mx8g -cp "path/to/stanford-corenlp-full-XXXX-XX-XX/*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer -port 9000
```

where `XXXX-XX-XX` is the version number of Stanford CoreNLP

* Python Decouple
As the project uses [python-decouple](https://github.com/henriquebastos/python-decouple) you will need to create a file named `.env` on the root of the project. You can copy from `.env.example` as following:

```
DEBUG=True
SECRET_KEY='mys3cr3tk3y'
STANFORD_CORENLP_SERVER='localhost:9000'
```

The project also uses [dj-database-url](https://pypi.python.org/pypi/dj-database-url/), so in the `.env` file you can set the `DATABASE_URL` as:

```
(on Windows) DATABASE_URL='sqlite:///C:\\path\\to\\project\\db.sqlite3'
(on Linux)   DATABASE_URL='sqlite:////path/to/project/db.sqlite3'
```

* Syncdb

```shell 
python manage.py migrate
```

* Runserver

```shell
python manage.py runserver
```

## Next Step
