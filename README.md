# FortyGuard Product Evaluation

## Project Overview

This project evaluates the FortyGuard Temperature API
through practical Python-based API testing.

The evaluation focuses on:

- API authentication
- Request construction
- GeoJSON payload validation
- HTTP response handling
- Asynchronous task monitoring
- Error handling
- Response time measurement
- API response analysis

## Technologies Used

- Python
- Requests
- Python-dotenv
- Unittest
- REST API

## API Endpoint

POST https://api.fortyguard.com/v1/heatmap

## Authentication

The API uses an API key passed through
the api-key request header.

The API key is stored locally in an environment
variable and is not included in source control.

## Project Structure

text
FortyGuard-Product-Evaluation/
├── .env
├── api_test.py
├── results/
├── run_evaluation.py
├── requirements.txt
├── .env.ex
├── .gitignore
└── README.md
├── .gitkeep
└── fortygraud_client.py
└── test_client.py


## Installation

Install dependencies:

bash
pip install -r requirements.txt


Create a .env file and configure your API key.

## Run Unit Tests

bash
python -m unittest discover -s tests -v


## Submit a Heatmap Request

bash
python run_evaluation.py --submit


The application submits a Heatmap request,
receives an activity ID, and monitors its status.

## Results

API responses and execution information
are saved locally in the results/ directory.

## Security

API credentials are stored in .env.
The .env file is excluded from Git.

## Evaluation Scope

This project evaluates the REST API behavior.
Dashboard UX and MCP integration are evaluated separately.

## Documentation

https://docs-api.fortyguard.com/docs/quickstart