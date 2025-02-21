from atproto import Client
import os
import argparse
from typing import Optional
from dotenv import load_dotenv


load_dotenv()

def login(client: Optional[Client] = None) -> Client:
    client = client or Client()
    client.login(
        os.environ['BSKY_HANDLE'],
        os.environ['BSKY_APP_PASSWORD']
    )
    return client

def get_or_create_block_list(client: Client) -> str:
    lists_response = client.app.bsky.graph.get_lists({'actor': client.me.did})
    
    for lst in lists_response.lists:
        if lst.name == 'block list':
            return lst.uri
    
    list_record = {
        'createdAt': client.get_current_time_iso(),
        'name': 'block list',
        'purpose': 'app.bsky.graph.defs#modlist',
        'description': "Liste de blocage automatique"
    }
    
    response = client.com.atproto.repo.create_record(
        data={
            'repo': client.me.did,
            'collection': 'app.bsky.graph.list',
            'record': list_record
        }
    )
    
    return response.uri

def resolve_account_to_did(client: Client, account: str) -> str:
    if account.startswith('http'):
        handle = account.split('/')[-1]
    else:
        handle = account.lstrip('@')
    
    resolved = client.com.atproto.identity.resolve_handle({'handle': handle.strip()})
    return resolved.did

def add_to_block_list(client: Client, list_uri: str, did: str) -> None:
    list_item = {
        'createdAt': client.get_current_time_iso(),
        'list': list_uri,
        'subject': did
    }

    client.com.atproto.repo.create_record(
        data={
            'repo': client.me.did,
            'collection': 'app.bsky.graph.listitem',
            'record': list_item
        }
    )


def get_users_from_list(client: Client, list_name: str) -> list[str]:
    """
    Récupère tous les utilisateurs d'une liste donnée (ex: "blocking list").
    
    :param client: Instance du client Bluesky (ATProto).
    :param list_name: Nom de la liste à récupérer.
    :return: Liste des utilisateurs présents dans la liste.
    """
    try:
        # Récupérer toutes les listes de l'utilisateur connecté
        user_lists = client.app.bsky.graph.get_lists({'actor': client.me.did}).lists
        
        # Trouver l'URI de la liste spécifiée
        list_uri = None
        for lst in user_lists:
            if lst.name == list_name:
                list_uri = lst.uri
                break

        if not list_uri:
            print(f"❌ La liste '{list_name}' n'existe pas.")
            return []

        # Récupérer les utilisateurs de la liste
        list_items = client.app.bsky.graph.get_list({'list': list_uri}).items
        users = [item.subject.handle for item in list_items]

        print(f"✅ {len(users)} utilisateurs trouvés dans la liste '{list_name}'")
        return users

    except Exception as e:
        print(f"❌ Erreur lors de la récupération de la liste '{list_name}': {e}")
        return []
    
def main():
    parser = argparse.ArgumentParser(description="Ajoute un compte à la block-list Bluesky")
    parser.add_argument('account', help="Handle (@exemple.bsky.social) ou URL de profil")
    args = parser.parse_args()

    try:
        client = login()
        list_uri = get_or_create_block_list(client)
        did = resolve_account_to_did(client, args.account)
        add_to_block_list(client, list_uri, did)
        print(f"Le compte {args.account} a été ajouté à la block-list avec succès.")
        print(get_users_from_list(client, "block list"))
    except Exception as e:
        print(f"Échec : {str(e)}")
        exit(1)

if __name__ == '__main__':
    main()