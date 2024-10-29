### Visit the deployed website ###

URL: [https://stock-danalysis.streamlit.app/](https://stock-danalysis.streamlit.app/)

- Front-end client deployed using Streamlit
- Back-end Django server deployed using AWS EC2
- PostgreSQL database hosted using AWS RDS

### Run on your local machine ###

To run this project on your local machine, you will need to have [Docker](https://www.docker.com/get-started/) installed.

#### Clone the repository ####

Start by cloning the repository on to your local machine.

```git clone https://github.com/allen-siu/StockDanalysis.git```

Then navigate to the project directory.

#### Set your Alpha Vantage API key environment variable ####

Claim your Alpha Vantage API key [here](https://www.alphavantage.co/support/#api-key).

In the project directory, open the `docker-compose.yaml` file with your text editor of choice.

Under the `django` service environment variables, replace `***YOUR API KEY HERE***` with your own Alpha Vantage API key.

#### Run the project using Docker ####

Ensure that you have Docker open and ready.

Open your terminal of choice and change your current working directory to the root folder of the project.

Run the command:

```docker compose up --build```

Now wait a few minutes for all services to start.

After all services are up and running, you are done setting up the project. You can open the Streamlit application by navigating to [http://localhost:8501](http://localhost:8501)


