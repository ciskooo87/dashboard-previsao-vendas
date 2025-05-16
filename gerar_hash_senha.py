
import bcrypt

def gerar_hash(senha: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(senha.encode(), salt)
    return hashed.decode()

if __name__ == "__main__":
    senha = input("Digite a senha a ser criptografada: ")
    print("Hash gerado:")
    print(gerar_hash(senha))
