# create_db.py
from config.database import engine, Base, SessionLocal
from models.models import Usuario, Pessoa, BemMaterial, Emprestimo, EmprestimoItem, BaixaBem

def init_db():
    print("Criando tabelas no banco de dados PostgreSQL...")
    Base.metadata.create_all(bind=engine)
    
    # Criar usuário inicial para o primeiro login
    db = SessionLocal()
    if not db.query(Usuario).filter_by(login="admin").first():
        admin = Usuario(
            nome="Administrador",
            login="admin",
            senha_hash="admin123",  # No futuro aplicaremos hash de senha real
            ativo=True
        )
        db.add(admin)
        db.commit()
        print("Usuário padrão 'admin' (senha: 'admin123') criado com sucesso!")
    db.close()
    print("Banco de dados inicializado com sucesso!")

if __name__ == "__main__":
    init_db()