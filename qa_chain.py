# test_chain.py

import os
from langchain_community.graphs import Neo4jGraph
from langchain_community.chat_models import ChatOpenAI
from langchain_community.chains.graph_qa.cypher import GraphCypherQAChain
from langchain_core.messages import SystemMessage
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
import re


# Load .env
load_dotenv()

# System prompt
SYSTEM_PROMPT = """
You are an assistant that answers questions about the Dark Souls universe using a Neo4j knowledge graph.

The graph contains five node types:
Weapon, Spell, Shield, Gift, and Entity.
Each node has a name property.

Relationships (edges) connect these nodes and represent facts such as:
For example: 
(:Weapon)-[:WIELDED_BY]->(:Entity),
(:Spell)-[:CREATED_BY]->(:Entity),
(:Gift)-[:GIVEN_TO]->(:Entity), etc.
And many more

Nodes may be connected even if they are of different types. If you're unsure of a node's type, use a generic variable and search across all node types.

Your task:
Convert a natural language question into a valid Cypher query.

When you don’t know a node’s type (e.g., "What is X?" or "Who created Y?"), match against all possible types using:

MATCH (n)-[:RELATIONSHIP]->(m {name: "X"})
RETURN n
or
MATCH (n {name: "X"})-[r]->(m)
RETURN r, m
Always use the name property for identification.

Example 1:
Question: "Who wields the Chaos Blade?"
→ Cypher:
MATCH (w)-[:WIELDED_BY]->(e:Entity) WHERE w.name = "Chaos Blade" RETURN e.name

Example 2:
Question: "What is the effect of Power Within?"
→ Cypher:
MATCH (s)-[:EFFECT_ON]->(e) WHERE s.name = "Power Within" RETURN e.name

Example 3:
Question: "What is the Pendant?"
(Node type unknown — could be Gift, Spell, etc.)
→ Cypher:
MATCH (n) WHERE n.name = "Pendant" RETURN labels(n), properties(n)

**If you are using a UNION, generate the cypher like this:
MATCH (s:Shield)-[:FOUND_IN]->(e:Entity {name: 'Anor Londo'}) 
RETURN s.name AS item, 'Shield' AS type

UNION

MATCH (g:Gift)-[:FOUND_IN]->(e:Entity {name: 'Anor Londo'}) 
RETURN g.name AS item, 'Gift' AS type
**
Be flexible and precise. Use variable node types when needed, and make sure all Cypher queries are syntactically correct.

"""

# Custom prompt template
prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(SYSTEM_PROMPT),
    HumanMessagePromptTemplate.from_template("{question}")
])

# Neo4j connection
graph = Neo4jGraph(
    url="neo4j+s://2710f498.databases.neo4j.io",
    username="neo4j",
    password=os.getenv("neo4j_password")
)

# Define the LLM
llm = ChatOpenAI(temperature=0, model_name="gpt-4o", openai_api_key=os.getenv("OPEN_AI_KEY"))

# Initialize the QA Chain
qa_chain = GraphCypherQAChain.from_llm(
    llm=llm,
    cypher_llm=llm,
    graph=graph,
    verbose=True,
    allow_dangerous_requests=True,
    return_intermediate_steps=True,
    prompt=prompt
    
)
def strip_bad_labels(query: str) -> str:
    # Remove overly specific labels (e.g., :Shield, :Ring, :Weapon) from nodes
    return re.sub(r"\((\w+):(?:Shield|Spell|Weapon|Gift|Entity)\)", r"(\1)", query)
def standardize_union_returns(cypher: str) -> str:
    """
    Ensures all UNION return statements use: RETURN <name> AS item, '<Type>' AS type
    """
    # Matches: MATCH (x:Type)... RETURN x.name AS Whatever
    pattern = re.compile(
        r"MATCH\s*\(\w+:(\w+)\)[^)]+?\)\s*RETURN\s*(\w+)\.name\s+AS\s+\w+",
        re.IGNORECASE
    )

    def replacer(match):
        label = match.group(1)  # e.g., Shield, Gift, Weapon
        return f"RETURN {match.group(2)}.name AS item, '{label}' AS type"

    # Replace all RETURN statements
    fixed_cypher = pattern.sub(lambda m: f"{m.group(0).split('RETURN')[0]}{replacer(m)}", cypher)
    return fixed_cypher

def answer_question(question: str) -> dict:
    """Use the QA chain to answer a natural language question with Cypher and LLM summarization."""
    raw_result = qa_chain(question)
    raw_query = raw_result["intermediate_steps"][0]["query"]

    no_bad_labels = strip_bad_labels(raw_query)
    fixed_query = standardize_union_returns(no_bad_labels)

    try:
        neo4j_result = graph.query(fixed_query)

        if neo4j_result:
            rows = []

            for row in neo4j_result:
                vals = list(row.values())

                # Case 1: RETURN n (single node object)
                if len(vals) == 1:
                    val = vals[0]
                    if isinstance(val, dict) and 'name' in val:
                        rows.append([val['name']])
                    else:
                        # fallback: stringify entire object
                        rows.append([str(val)])

                # Case 2: RETURN a, b
                elif len(vals) == 2:
                    a, b = vals
                    a_val = a.get('name') if isinstance(a, dict) else a
                    b_val = b.get('name') if isinstance(b, dict) else b
                    rows.append([a_val, b_val])

            # ✅ Use LLM to summarize
            if all(len(r) == 1 for r in rows):
                values = [r[0] for r in rows]
                value_list = ", ".join(values[:-1]) + f", and {values[-1]}" if len(values) > 1 else values[0]
                prompt = f"""
You are a Dark Souls lore expert. The user asked:

"{question}"

These are the relevant items or entities:
{value_list}

Write a natural language summary listing these items.
"""
                answer = llm.predict(prompt).strip()

            elif all(len(r) == 2 for r in rows):
                bullet_list = "\n".join([f"- {a} → {b}" for a, b in rows])
                prompt = f"""
You are a Dark Souls lore expert.

Given the user's question and these subject–object pairs, summarize the relationships in a clear sentence.

Question:
{question}

Pairs:
{bullet_list}

Summary:
"""
                answer = llm.predict(prompt).strip()

            else:
                answer = "Unsupported result format returned from the graph."

        else:
            answer = "No result found in the graph."

    except Exception as e:
        answer = f"Error running Cypher query: {e}"

    return {
        "raw_query":raw_query,
        "answer": answer
    }