# This project is built on the game Dark Souls 1

## Created By - Dhrubajyoti Ray (dtray@tepper.cmu.edu)

### This knowledge graph can be visualized in the Neo4j Browser
### Interactive Graph Browser
- URL: https://browser.neo4j.io/?connectURL=neo4j+s://2710f498.databases.neo4j.io
- Aura URI: neo4j+s://2710f498.databases.neo4j.io
- Username: neo4j
- Password: Please email for the password on dtray@tepper.cmu.edu if you want to check how the graph looks
## Streamlit app for Question Answers

We used LangChain to create the Streamlit app
To access the Streamlit App for QA - https://dark-souls-cloudwalk-djray.streamlit.app/

## If you want to visualize the entire graph, in the first code block type "MATCH (n) RETURN n;" and run this query.

## Don't forget to set your initial node size in settings to 1000

## Steps to create new entity relations on your own (Use VSCode or Cursor or any terminal of your choice)

1. Clone the Repository in VS code or cursor terminal
- git clone https://github.com/ankur-ray23/dark-souls-cloudwalk.git
-cd dark-souls-cloudwalk

2. Create and activate a virtual environment
- python -m venv venv
- source venv/bin/activate 

3. Install dependencies
- pip install -r requirements.txt

4. Set your OpenAI API key
- Create a .env file in the root directory
- In the .env file paste whatever your openai api key is -> OPEN_AI_KEY=sk-xxxxxxxxxxxxxx

5. Scrape pages (optional)
- I have scraped the pages from wikidot, but you are free to use your own scraping method.
- Run all the notebooks to generate json files

6. Extract Entity relationships
- Go to the folder and run all notebooks. 
- In each notebook change the prompt according to your needs to extract the entity relations

7. Developing a Web Browser
- Go to Neo4j Aura, create a free account
- Create a free AuraDB instance and make sure you copy the password
- Paste the password on .env file as -> neo4j_password = xxxxxxxxxxxx
- Run the script to get the graph

8. Accessing the graph
- At the start of the notebook you can see the URL and Aura URI
- Paste your Aura URI after -> ?connectURL = your_aura_uri
- Add your login credentials
- In the first code block type "MATCH (n) RETURN n;" and run this query
