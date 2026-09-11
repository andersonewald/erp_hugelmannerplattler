# controllers/auth_controller.py
from config.database import get_db
from models.models import Usuario
from werkzeug.security import check_password_hash, generate_password_hash

class AuthController:
    @staticmethod
    def autenticar(login, senha):
        """Valida as credenciais do usuário no banco PostgreSQL via Hash."""
        db = get_db()
        try:
            # Busca o usuário ativo pelo login
            usuario = db.query(Usuario).filter_by(login=login, ativo=True).first()
            
            # Valida a senha digitada contra o hash armazenado no banco
            if usuario and check_password_hash(usuario.senha_hash, senha):
                return True, usuario
            
            return False, None
        except Exception as e:
            return False, str(e)
        finally:
            db.close()

    @staticmethod
    def cadastrar_usuario(nome, login, senha):
        """Cadastra novos usuários salvando a senha como Hash de forma segura."""
        db = get_db()
        try:
            if db.query(Usuario).filter_by(login=login).first():
                return False, "Login já cadastrado no sistema!"

            # Criptografa a senha antes de salvar no banco
            senha_criptografada = generate_password_hash(senha)

            novo_usuario = Usuario(
                nome=nome,
                login=login,
                senha_hash=senha_criptografada,
                ativo=True
            )
            db.add(novo_usuario)
            db.commit()
            return True, "Usuário cadastrado com sucesso!"
        except Exception as e:
            db.rollback()
            return False, f"Erro ao salvar: {str(e)}"
        finally:
            db.close()