#!/usr/bin/env python
# -*- coding: utf-8 -*-

from uuid import UUID

from cassandra.auth import PlainTextAuthProvider
from cassandra.cluster import Cluster

class ConnectionClient:
    SECURE_CONNECT_BUNDLE = "/path/to/secure-connect-driver-demo.zip"
    CLIENT_ID = "client-id"
    CLIENT_SECRET = "client-secret"
    KEYSPACE = "demo"

    def __init__(self):
        self.cluster = None
        self.session = None
    
    def connect(self):
        cloud_config = {
            "secure_connect_bundle" : self.SECURE_CONNECT_BUNDLE
        }
        authProvider = PlainTextAuthProvider(self.CLIENT_ID, self.CLIENT_SECRET)
        self.cluster = Cluster(cloud = cloud_config, auth_provider = authProvider)
        self.session = self.cluster.connect(self.KEYSPACE)
        for host in self.cluster.metadata.all_hosts():
            print(f"{host}")
            
    def close(self):
        self.cluster.shutdown()

class BoundStatementsClient(ConnectionClient):
    def __init__(self):
        super().__init__()
        
    def createSchema(self):
        self.session.execute("DROP TABLE IF EXISTS demo.songs;", timeout = 10.0)
        self.session.execute("DROP TABLE IF EXISTS demo.playlists;", timeout = 10.0)
        self.session.execute("""
            CREATE TABLE demo.songs (
                id uuid PRIMARY KEY,
                title text,
                album text,
                artist text,
                tags set<text>,
                data blob
            );
        """)
        self.session.execute("""
            CREATE TABLE demo.playlists (
                id uuid,
                title text,
                album text,
                artist text,
                song_id uuid,
                PRIMARY KEY (id, title, album, artist)
            );
        """)
        print('schema created in demo keyspace')

    def loadData(self):
        bound_statement = self.session.prepare("""
            INSERT INTO demo.songs
            (id, title, album, artist, tags)
            VALUES (?, ?, ?, ?, ?);
        """)
        tags = set(['jazz', '2013'])
        self.session.execute(bound_statement.bind((
            UUID("756716f7-2e54-4715-9f00-91dcbea6cf50"),
            "La Petite Tonkinoise",
            "Bye Bye Blackbird",
            "Joséphine Baker",
            tags ))
        )
        tags = set(['1996', 'birds'])
        self.session.execute(bound_statement.bind((
            UUID("f6071e72-48ec-4fcb-bf3e-379c8a696488"),
            "Die Mösch",
            "In Gold'", 
            "Willi Ostermann",
            tags ))
        )
        tags = set(['1970', 'soundtrack'])
        self.session.execute(bound_statement.bind((
            UUID("fbdf82ed-0063-4796-9c7c-a3d4f47b4b25"),
            "Memo From Turner",
            "Performance",
            "Mick Jager",
            tags ))
        )
        bound_statement = self.session.prepare("""
            INSERT INTO demo.playlists
            (id, song_id, title, album, artist)
            VALUES (?, ?, ?, ?, ?);
        """)
        self.session.execute(bound_statement.bind((
            UUID("2cc9ccb7-6221-4ccb-8387-f22b6a1b354d"),
            UUID("756716f7-2e54-4715-9f00-91dcbea6cf50"),
            "La Petite Tonkinoise",
            "Bye Bye Blackbird",
            "Joséphine Baker"))
        )
        self.session.execute(bound_statement.bind((
            UUID("2cc9ccb7-6221-4ccb-8387-f22b6a1b354d"),
            UUID("f6071e72-48ec-4fcb-bf3e-379c8a696488"),
            "Die Mösch",
            "In Gold",
            "Willi Ostermann"))
        )
        self.session.execute(bound_statement.bind((
            UUID("3fd2bedf-a8c8-455a-a462-0cd3a4353c54"),
            UUID("fbdf82ed-0063-4796-9c7c-a3d4f47b4b25"),
            "Memo From Turner",
            "Performance",
            "Mick Jager"))
        )
        print('data loaded into demo schema')

def main():
    client = BoundStatementsClient()
    client.connect()
    client.createSchema()
    client.loadData()
    client.close()

if __name__ == "__main__":
    main()
