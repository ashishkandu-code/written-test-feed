# Monitor feeds

## Table of Contents

- [About](#about)
- [Getting Started](#getting_started)
- [Usage](#usage)

## About <a name = "about"></a>

A script for monitoring the site [tmolicense](http://tmolicense.lumbini.gov.np/) continuously and mail the latest feeds.

## Getting Started <a name = "getting_started"></a>

Complete the below prerequisites and run the main.py script

### Prerequisites

To start using the script, install the requirements file and give your mail client credentials in credentials.json.

```python
python -m pip install -r requirements.txt
```

## Usage <a name = "usage"></a>

The recipients can be specified in recipients.txt file which is created at the first run of the script with dev email populated.

*This script is indented to be used with CronJob so that the run can be executed for desired frequency.*
