# BoostNote exporter

Just a single script to save your boostnote documents into local files

  Important: it only saves documents that are inside the folders, if you have a document outside the folders they won't be saved, this is because BoostNote API is not listing these documents at the moment.

# Requirements

  Python 3.6+

# How to install

Create a virtualenv and then install the requirements in

```sh
pip install -r requirements.txt
```

Then, copy `.env.example` file into `.env` and fill the Token with the one provided by BoostNote (at the moment I wrote this it was in the api settings section) and the `BASE_DIR` (this is optional, you can delete it if you want)

# How to use

`path` is optional, use it if you didn't set the `BASE_DIR` env variable, if you don't set any dir it will fallback to `./backup`

```sh
python main.py [<path>]
```

