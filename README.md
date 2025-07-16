# Flowella API

A simple Python FastAPI for Flowella App.

## Features

- RESTful endpoints
- Easy integration
- Lightweight and fast

## Installation

```bash
pip install flowella
```

## Usage

```python
from flowella import FlowellaAPI

api = FlowellaAPI(api_key="YOUR_API_KEY")
response = api.get_data()
print(response)
```

## Configuration

Set your API key as an environment variable:

```bash
export FLOWELLA_API_KEY=your_api_key
```

## Documentation

See [docs/](docs/) for detailed API documentation.

## License

MIT License