# Python ETL Project with Docker and MySQL

## Overview

This project demonstrates a simple ETL (Extract, Transform, Load) pipeline. The ETL script reads a CSV file, processes the data, and loads it into a MySQL database. The project is containerized using Docker with two services:
- **MySQL:** A MySQL 8.0 database container.
- **ETL:** A Python-based ETL container that processes the data and loads it into MySQL.

## Project Structure

. ├── Dockerfile ├── docker-compose.yml ├── etl.py ├── requirements.txt ├── .env.example ├── .gitignore └── dataset └── myntra_products_catalog.csv # CSV file used by the ETL script

markdown
Copy

**Note:**  
- The `.env` file (which holds sensitive information like passwords) is excluded from version control. Use `.env.example` as a template.

## Getting Started

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) installed on your machine.
- [Docker Compose](https://docs.docker.com/compose/install/) installed.

### Setup Steps

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/CodedbyAli/etl-pipeline.git
   cd your-repo-name

2. **Create Your Environment Variables File:**

   Copy the provided `.env.example` to a new file named `.env` and update it with your specific configuration. For example:

   ```bash
   cp .env.example .env

   Then, open .env in your favorite editor and set the values


3. **Build and Run the Containers:**

Use Docker Compose to build the images and start the containers. Run the following command from the root directory of the project:

    docker-compose up --build

This command will:

Build the ETL container image based on the Dockerfile.

Start the MySQL container, which will initialize the database.

Wait until MySQL passes its healthcheck before starting the ETL container.

Run the ETL script (etl.py) to load data into MySQL.


## Important Note

If the ETL container attempts to connect to MySQL before MySQL is fully up and listening on port 3306, you may encounter connection errors. In such cases, run the following commands separately:

```bash
docker-compose up -d mysql
# Wait a few seconds or check the logs to ensure MySQL is ready
docker-compose up --build etl

