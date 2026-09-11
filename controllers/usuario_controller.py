# controllers/usuario_controller.py
from werkzeug.security import generate_password_hash
from config.database import get_db
from models.models import Usuario

class UsuarioController:

    @staticmethod
    def listar_todos(filtro=""):
        db = get_db()
        try:
            query = db.query(Usuario)
            if filtro:
                filtro_limpo = f"%{filtro.strip()}%"
                query = query.filter(
                    Usuario.nome.ilike(filtro_limpo) | 
                    Usuario.login.ilike(filtro_limpo)
                )
            return query.order_by(Usuario.nome).all()
        finally:
            db.close()

    @staticmethod
    def salvar_usuario(nome, login, senha=None, usuario_id=None):
        if not nome or not nome.strip():
            return False, "O nome do usuário é obrigatório!"
        if not login or not login.strip():
            return False, "O login é obrigatório!"

        db = get_db()
        try:
            login_limpo = login.strip().lower()

            # Verificação de login duplicado
            existente = db.query(Usuario).filter(
                Usuario.login == login_limpo, 
                Usuario.id != usuario_id
            ).first()

            if existente:
                return False, "Já existe um usuário cadastrado com este login!"

            if usuario_id:
                usr = db.get(Usuario, usuario_id) if hasattr(db, 'get') else db.query(Usuario).get(usuario_id)
                if not usr:
                    return False, "Usuário não encontrado!"

                usr.nome = nome.strip()
                usr.login = login_limpo
                if senha and senha.strip():
                    usr.senha_hash = generate_password_hash(senha.strip())
                
                db.commit()
                return True, "Usuário atualizado com sucesso!"
            else:
                if not senha or not senha.strip():
                    return False, "A senha é obrigatória para novos usuários!"

                novo_usuario = Usuario(
                    nome=nome.strip(),
                    login=login_limpo,
                    senha_hash=generate_password_hash(senha.strip()),
                    ativo=True
                )
                db.add(novo_usuario)
                db.commit()
                return True, "Usuário cadastrado com sucesso!"

        except Exception as e:
            db.rollback()
            return False, f"Erro ao salvar usuário: {str(e)}"
        finally:
            db.close()

    @staticmethod
    def alternar_status(usuario_id):
        """Ativa ou Inativa o acesso de um usuário."""
        db = get_db()
        try:
            usr = db.get(Usuario, usuario_id) if hasattr(db, 'get') else db.query(Usuario).get(usuario_id)
            if not usr:
                return False, "Usuário não encontrado!"

            usr.ativo = not usr.ativo
            db.commit()
            
            status_str = "ativado" if usr.ativo else "inativado"
            return True, f"Usuário {status_str} com sucesso!"
        except Exception as e:
            db.rollback()
            return False, f"Erro ao alterar status: {str(e)}"
        finally:
            db.close()