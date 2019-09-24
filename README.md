
# imap-storage
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

Use your Email-account as Storage for data structures and files 


## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Introducing notes
- Before reaching version 1.0, the storage layout may change when updating

### Prerequisites

python3.5 or later.
It should work with all versions of Python3 but tests are running on 3.5.3 and 3.7.4 now.

This project makes use of the following libraries:
```
- imapclient
- lxml
```

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
```


## Running the tests
```
git clone https://github.com/snake-soft/imap-storage.git
cd imap-storage
virtualenv -p python3 env
source env/bin/activate
pip install -r requirements.txt
# > First fill the data of your testserver in 'tests/secrets.py'
python -m coverage run --source='imap_storage' run_tests.py && coverage report -m --skip-covered
```

### And coding style tests

Code style is not finished, mostly because of missing docstrings.
```
pylint imap_storage
```

## Deployment

This library is not ready to be deployed productive


## Built With
* [IMAPClient](https://imapclient.readthedocs.io/en/2.1.0/) - easy-to-use, Pythonic and complete IMAP client library.
* [lxml](https://lxml.de/) - the most feature-rich and easy-to-use library for processing XML and HTML in the Python language


## Contributing
Please read [CONTRIBUTING.md](https://gist.github.com/PurpleBooth/b24679402957c63ec426) for details on our code of conduct, and the process for submitting pull requests to us.


## Versioning
We use [SemVer](http://semver.org/) for versioning.. 
During beta development minor versions may be incompatible, too.

## Authors
* **Me** - *Initial work* - [Snake-Soft](https://github.com/snake-soft)

See also the list of [contributors](https://github.com/snake-soft/imap-storage/graphs/contributors) who participated in this project.

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE.md](LICENSE.md) file for details
