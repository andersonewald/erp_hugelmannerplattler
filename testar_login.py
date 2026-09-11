# testar_login.py
from config.database import get_db
from models.models import Usuario
from werkzeug.security import check_password_hash

def testar():
    db = get_db()
    usuario = db.query(Usuario).filter_by(login="admin").first()
    
    if not usuario:
        print("❌ ERRO: Usuário 'admin' NÃO foi encontrado no banco de dados.")
        return

    print(f"✔️ Usuário encontrado ID: {usuario.id}")
    print(f"   Login: '{usuario.login}'")
    print(f"   Ativo: {usuario.ativo}")
    print(f"   Tamanho do hash no banco: {len(usuario.senha_hash)} caracteres")
    print(f"   Hash gravado: {usuario.senha_hash}")

    valido = check_password_hash(usuario.senha_hash, "admin123")
    if valido:
        print("✅ SUCESSO: A senha 'admin123' bateu com o hash do banco!")
    else:
        print("❌ ERRO: A senha 'admin123' NÃO bateu com o hash do banco.")
        if len(usuario.senha_hash) < 162:
            print("⚠️ ATENÇÃO: O hash gravado no banco está cortado/incompleto! O campo VARCHAR é muito pequeno.")

if __name__ == "__main__":
    testar()