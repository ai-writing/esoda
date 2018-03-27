# ESODA Project
Project home for ESODA (http://www.esoda.org)

## Setup
### 0. Install Python 2.7.

### 1. Install prerequisite python packages

Using `virtualenv` is recommended. Create a fresh environment named `venv` in the project's root folder.

```shell
(venv) pip install -U -r requirements.txt
```

### (Optional, only for deployment. Never do this during developing.) Install the latest Java runtime. Download and deploy the latest [Stanford CoreNLP Server](http://stanfordnlp.github.io/CoreNLP/corenlp-server.html)

```shell
java -mx8g -cp "path/to/stanford-corenlp-full-XXXX-XX-XX/*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer -port 9000
```

where `XXXX-XX-XX` is the version number of Stanford CoreNLP

### 2. Create and Modify Essential Settings
As the project uses [python-decouple](https://github.com/henriquebastos/python-decouple) you will need to **create a file named `.env` on the root of the project**. You can copy from `.env.example` as following:

```
DEBUG=True
...
```

The project also uses [dj-database-url](https://pypi.python.org/pypi/dj-database-url/), so in the `.env` file you should set the `DATABASE_URL` as:

```
# (on Windows)
DATABASE_URL='sqlite:///X:\\path\\to\\project\\db.sqlite3'
# (on Linux)
DATABASE_URL='sqlite:////path/to/project/db.sqlite3'
```

Ask team Slack for other sensitive settings marked with `???`. **(You should NEVER commit setting files containing passwords to Github, of course.)**

### 3. Syncdb

```shell 
python manage.py migrate
```

If `syncdb` fails, check the `DATABASE_URL` in your `.env` file.

### (Optional, for deployment) Django's [translation framework](https://docs.djangoproject.com/en/dev/topics/i18n/translation/) for multilingual interface

Install [gettext](https://www.gnu.org/software/gettext/) toolset and add `gettext/bin/` to `PATH`

* On Linux, use `apt-get` to install
* On Windows, download [precompiled binaries](https://mlocati.github.io/articles/gettext-iconv-windows.html)

Then compile the translation files for use:

```shell
python manage.py compilemessages
```


### 4. Runserver

```shell
python manage.py runserver
```

Then have fun searching!

## Next Step
