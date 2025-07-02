import os

from neo4j import GraphDatabase
import xml.etree.ElementTree as ET
from dotenv import load_dotenv
from pathlib import Path
import time

env_path = Path('../') / '.env'
load_dotenv(dotenv_path=env_path)

BATCH_SIZE = 500


class GraphMLImporter:
    def __init__(self, uri, user, password, database=os.getenv("NEO4J_DATABASE")):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.database = database

    def close(self):
        self.driver.close()

    def import_graphml(self, file_path):
        tree = ET.parse(file_path)
        root = tree.getroot()
        ns = {'graphml': 'http://graphml.graphdrawing.org/xmlns'}

        with self.driver.session(database=self.database) as session:
            print("🧨 Clearing existing database...")
            session.run("MATCH (n) DETACH DELETE n")

            print("📦 Inserting nodes...")
            node_batch = []
            for node in root.findall(".//graphml:node", ns):
                node_id = node.get("id")
                node_batch.append(node_id)
                if len(node_batch) >= BATCH_SIZE:
                    self._insert_nodes_batch(session, node_batch)
                    node_batch = []
            if node_batch:
                self._insert_nodes_batch(session, node_batch)

            print("🔗 Inserting relationships...")
            collab_batch = []
            member_batch = []
            for edge in root.findall(".//graphml:edge", ns):
                source = edge.get("source")
                target = edge.get("target")
                data_elements = edge.findall("graphml:data", ns)
                edge_data = {d.get("key"): d.text for d in data_elements}
                rel_type = edge_data.get("d1", "unknown")

                if rel_type == "collab":
                    collab_batch.append((source, target, edge_data.get("d0", "")))
                    if len(collab_batch) >= BATCH_SIZE:
                        self._insert_collabs_batch(session, collab_batch)
                        collab_batch = []
                elif rel_type == "band_member":
                    member_batch.append((target, source))  # member -> band
                    if len(member_batch) >= BATCH_SIZE:
                        self._insert_members_batch(session, member_batch)
                        member_batch = []

            if collab_batch:
                self._insert_collabs_batch(session, collab_batch)
            if member_batch:
                self._insert_members_batch(session, member_batch)

    def _insert_nodes_batch(self, session, node_ids):
        query = "UNWIND $nodes AS name MERGE (:Artist {name: name})"
        session.run(query, nodes=node_ids)
        print(f"✅ Inserted {len(node_ids)} artists")

    def _insert_collabs_batch(self, session, collabs):
        query = """
        UNWIND $collabs AS collab
        MATCH (a:Artist {name: collab.source})
        MATCH (b:Artist {name: collab.target})
        MERGE (a)-[:COLLABORATED_WITH {title: collab.title}]->(b)
        """
        session.run(query, collabs=[{"source": s, "target": t, "title": title} for s, t, title in collabs])
        print(f"🔁 Inserted {len(collabs)} collaborations")

    def _insert_members_batch(self, session, members):
        query = """
        UNWIND $members AS rel
        MATCH (a:Artist {name: rel.member})
        MATCH (b:Artist {name: rel.band})
        MERGE (a)-[:MEMBER_OF]->(b)
        """
        session.run(query, members=[{"member": m, "band": b} for m, b in members])
        print(f"👥 Inserted {len(members)} member relationships")


# Usage
if __name__ == "__main__":
    start_time = time.time()

    uri = os.getenv("NEO4J_URI_BOLT_MAGNACLOUDA")
    user = os.getenv("NEO4J_USERNAME")
    password = os.getenv("NEO4J_PASSWORD")
    file_path = os.getenv("GRAPH_FILE")

    importer = GraphMLImporter(uri, user, password)
    importer.import_graphml(file_path)
    importer.close()

    print(f"🏁 Import finished in {time.time() - start_time:.2f} seconds")
