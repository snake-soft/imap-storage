
# imap-storage
[![Build Status](https://travis-ci.org/snake-soft/imap-storage.svg?branch=master)](https://travis-ci.org/snake-soft/imap-storage)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Documentation Status](https://readthedocs.org/projects/imap-storage/badge/?version=latest)](https://imap-storage.readthedocs.io/en/latest/?badge=latest)
[![Coverage Status](https://coveralls.io/repos/github/snake-soft/imap-storage/badge.svg?branch=master)](https://coveralls.io/github/snake-soft/imap-storage?branch=master)

Use your Email-account as Storage for data structures and files 


## Getting Started
These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.
Have a look at the [documentation](https://imap-storage.readthedocs.io/en/latest/).

### Introducing notes
- Before reaching version 1.0, the storage layout may change when updating


### Prerequisites
python3.5 or later.
It should work Python3.4+ but tests are running on 2.7, 3.5 and 3.7.

This project makes use of the following libraries:
* [IMAPClient](https://imapclient.readthedocs.io/en/2.1.0/) - easy-to-use, Pythonic and complete IMAP client library.
* [lxml](https://lxml.de/) - the most feature-rich and easy-to-use library for processing XML and HTML in the Python language


### Installing
You can install the latest release from pip:
```
pip install imap-storage
```


### Short example
```python
from imap_storage import Account, Config

config = Config()
config.imap.user = 'email@example.com'
config.imap.password = '123'
config.imap.host = 'imap.example.com'  # config.imap.port default is 993

account = Account(config, 1)
directory = account.storage.directory_by_path(account.config.directory)
email = directory.new_email('Your_first_item')
email.add_item('TestMessage', text='Your first message')
email.save()
email.delete()
account.close()
```


## Running the tests
Rename 'secrets.sample.py' in tests directory to 'secrets.py' and include your e-mail account for testing.
Then run this inside root directory:
```
python -m unittest  # tests all
python -m unittest tests.test_account  # tests only account
```
or run it with coverage:
```
coverage run --source='imap_storage' -m unittest && coverage report -m --skip-covered
```


### And coding style tests
Code style is not finished, mostly because of missing docstrings.
```
pylint imap_storage
```


## Deployment
This library is not ready to be deployed productive


## Contributing
Please read [CONTRIBUTING.md](https://gist.github.com/PurpleBooth/b24679402957c63ec426) for details on our code of conduct, and the process for submitting pull requests to us.


## Versioning
We use [SemVer](http://semver.org/) for versioning.
During beta development minor versions may be incompatible, too.


## Authors
* **Me** - *Initial work* - [Snake-Soft](https://github.com/snake-soft)

See also the list of [contributors](https://github.com/snake-soft/imap-storage/graphs/contributors) who participated in this project.


## License
This project is licensed under the GNU General Public License v3.0 - see the [LICENSE.md](LICENSE.md) file for details
