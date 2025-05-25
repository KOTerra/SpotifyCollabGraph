from neo4j import GraphDatabase
import xml.etree.ElementTree as ET
import time


class GraphMLImporter:
    def __init__(self, uri, user, password, database="neo4j"):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.database = database

    def close(self):
        self.driver.close()

    def import_graphml(self, file_path):
        tree = ET.parse(file_path)
        root = tree.getroot()

        ns = {'graphml': 'http://graphml.graphdrawing.org/xmlns'}

        with self.driver.session(database=self.database) as session:
            # Insert nodes
            for node in root.findall(".//graphml:node", ns):
                node_id = node.get("id")
                session.write_transaction(self._create_artist, node_id)
                print(f"Inserted node: {node_id}")

            # Insert edges
            for edge in root.findall(".//graphml:edge", ns):
                source = edge.get("source")
                target = edge.get("target")
                data_elements = edge.findall("graphml:data", ns)
                edge_data = {d.get("key"): d.text for d in data_elements}
                rel_type = edge_data.get("d1", "unknown")

                if rel_type == "collab":
                    session.write_transaction(self._create_collaboration, source, target, edge_data)
                    print(f"Inserted COLLABORATED_WITH: {source} -> {target} ({edge_data.get('d0', '')})")
                elif rel_type == "band_member":
                    session.write_transaction(self._create_band_membership, target, source)
                    print(f"Inserted MEMBER_OF: {target} -> {source}")
                else:
                    print(f"Skipped edge: {source} -> {target} with unknown type '{rel_type}'")

    @staticmethod
    def _create_artist(tx, name):
        tx.run("MERGE (:Artist {name: $name})", name=name)

    @staticmethod
    def _create_collaboration(tx, source, target, data):
        query = """
        MATCH (a:Artist {name: $source})
        MATCH (b:Artist {name: $target})
        MERGE (a)-[r:COLLABORATED_WITH {title: $title}]->(b)
        """
        tx.run(query, source=source, target=target, title=data.get("d0", ""))

    @staticmethod
    def _create_band_membership(tx, member, band):
        query = """
        MATCH (a:Artist {name: $member})
        MATCH (b:Artist {name: $band})
        MERGE (a)-[:MEMBER_OF]->(b)
        """
        tx.run(query, member=member, band=band)


# Usage
if __name__ == "__main__":
    start_time = time.time()

    uri = "bolt://192.168.1.128:7687"
    user = "neo4j"
    password = "Mihais123"
    file_path = "collaboration_graph_from_playlist.graphml"

    importer = GraphMLImporter(uri, user, password)
    importer.import_graphml(file_path)
    importer.close()

    print(f"Imported {time.time() - start_time} seconds")
