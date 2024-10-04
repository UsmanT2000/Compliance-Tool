# Compliance Tool

## Overview

The Compliance Tool is a comprehensive application designed to fetch news articles from various sources, analyze their sentiment, and assign connotations to the content. It also integrates with data scraped from Interpol's Red Notice to search for queried names, providing a robust solution for compliance and risk assessment.

### Features

- **News Fetching**: Retrieve articles from **NewsAPI** and **Google Custom Search Engine**.
- **Sentiment Analysis**: Analyze the sentiment of fetched articles to understand the tone (positive, negative, neutral).
- **Connotation Assignment**: Automatically classify articles based on their sentiment scores.
- **Interpol Red Notice Search**: Search for queried names against data sourced from Interpol’s Red Notice to identify potential compliance risks.

## Requirements

Before running the project, ensure you have the following installed:

- Python 3.x
- Docker and Docker Compose (if running in a Docker environment)

## Getting Started

Follow the steps below to run the project locally or in a Docker environment.

### Local Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/compliance-tool.git
   cd compliance-tool
