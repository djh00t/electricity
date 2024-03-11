# Electricity Plans Data Sync Application

This application is designed to synchronize backend data for electricity plans locally by fetching information from various providers. It is currently in the data synchronization phase, with the next phase planned to include a set of APIs for querying the JSON data based on customer location and historical usage.

## Current Features

- **Data Fetching**: The application can fetch electricity plans from a list of provider URLs and save them to JSON files.
- **Data Synchronization**: It ensures that the local data is up-to-date by checking the last downloaded timestamp and refreshing the data as needed.
- **PDF Extraction**: The application can download and extract retailer information from a specified PDF file.
- **Concurrent Processing**: Utilizes multi-threading for efficient data fetching and processing.

## Upcoming Features

- **API Endpoints**: A set of APIs will be provided to query the synchronized JSON data based on various filters such as customer location and historical usage.
- **Data Analysis**: Tools for analyzing the data to provide insights into electricity plan trends and customer preferences.

## Installation

To set up the application, you will need Python 3 and the packages listed in `requirements.txt`. Install them using the following command:

```sh
pip install -r requirements.txt
```

## Usage

To start the data synchronization process, run the following command:

```sh
python get_plans.py [--debug]
```

Use the `--debug` flag to enable detailed logging.

## Configuration

Configuration settings such as the refresh interval and the number of threads for concurrent processing can be adjusted in `config.py`.

## Contributing

Contributions to the project are welcome. Please ensure that your code adheres to the PEP 8 style guidelines and includes appropriate comments and docstrings.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contact

For any queries or contributions, please open an issue in the project's repository.
