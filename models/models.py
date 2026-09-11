# models/models.py
import base64
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Float, Date, LargeBinary
from sqlalchemy.orm import relationship
from config.database import Base


class Usuario(Base):
    __tablename__ = 'usuarios'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(100), nullable=False)
    login = Column(String(50), unique=True, nullable=False)
    senha_hash = Column(String(255), nullable=False)
    ativo = Column(Boolean, default=True)
    data_cadastro = Column(DateTime, default=datetime.now)

    def __repr__(self):
        return f"<Usuario {self.login}>"


class Pessoa(Base):
    __tablename__ = 'pessoas'

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(100), nullable=False)
    cpf_rg = Column(String(20))
    telefone = Column(String(20))
    email = Column(String(100))
    categoria = Column(String(50), default="Integrante")
    
    # Controle de Vínculo e Status do Integrante
    mes_ano_entrada = Column(String(7), nullable=True)  # Formato: YYYY-MM
    mes_ano_saida = Column(String(7), nullable=True)    # Formato: YYYY-MM
    status = Column(String(20), default="Ativo")        # 'Ativo', 'Inativo', 'Afastado'
    ativo = Column(Boolean, default=True)               # Controle lógico do sistema

    # Dados Pessoais e Foto
    data_nascimento = Column(Date, nullable=True)
    genero = Column(String(30))
    nacionalidade = Column(String(50))
    naturalidade = Column(String(50))
    estado_civil = Column(String(30))
    foto_path = Column(String(255))

    # Documentação Completa
    rg_orgao_uf = Column(String(50))
    cnh = Column(String(30))
    cartao_sus = Column(String(30))
    titulo_eleitor = Column(String(30))
    passaporte = Column(String(30))

    # Endereço
    rua = Column(String(150))
    numero = Column(String(20))
    complemento = Column(String(50))
    bairro = Column(String(100))
    cidade = Column(String(100))
    estado = Column(String(2))
    cep = Column(String(15))

    # Ficha Médica e Emergência
    possui_plano_saude = Column(Boolean, default=False)
    plano_saude_info = Column(String(150))
    alergias = Column(Text)
    medicamentos_continuos = Column(Text)
    restricoes_alimentares = Column(Text)
    condicoes_medicas = Column(Text)
    contato_emergencia_nome = Column(String(100))
    contato_emergencia_telefone = Column(String(20))
    contato_emergencia_parentesco = Column(String(50))

    emprestimos = relationship("Emprestimo", back_populates="pessoa")


class BemMaterial(Base):
    __tablename__ = 'bens_materiais'

    id = Column(Integer, primary_key=True, autoincrement=True)
    codigo_patrimonio = Column(String(50), unique=True, nullable=False)
    nome = Column(String(150), nullable=False)
    descricao = Column(Text, nullable=True)
    categoria = Column(String(50), nullable=False)
    valor_estimado = Column(Float, default=0.0)
    estado_conservacao = Column(String(50), default="Bom")
    status = Column(String(30), default="Disponível")

    # Relacionamentos
    emprestimos_itens = relationship("EmprestimoItem", back_populates="bem")
    baixas = relationship("BaixaBem", back_populates="bem")
    fotos = relationship("FotoBemMaterial", back_populates="bem", cascade="all, delete-orphan", lazy="selectin")

    @property
    def quantidade_disponivel(self) -> int:
        return 1 if self.status == "Disponível" else 0

    def __repr__(self):
        return f"<BemMaterial {self.codigo_patrimonio} - {self.nome}>"


class FotoBemMaterial(Base):
    __tablename__ = 'fotos_bens_materiais'

    id = Column(Integer, primary_key=True, autoincrement=True)
    bem_id = Column(Integer, ForeignKey('bens_materiais.id'), nullable=False)
    foto_blob = Column(LargeBinary, nullable=False)  # Conteúdo da imagem salvo em binário no BD
    mimetype = Column(String(50), nullable=False)     # Ex: 'image/jpeg', 'image/png'
    data_cadastro = Column(DateTime, default=datetime.now)

    bem = relationship("BemMaterial", back_populates="fotos")

    @property
    def foto_base64(self) -> str:
        """Converte o binário da foto em string Data URI para exibição direta no HTML."""
        if self.foto_blob:
            encoded = base64.b64encode(self.foto_blob).decode('utf-8')
            return f"data:{self.mimetype};base64,{encoded}"
        return ""


class Emprestimo(Base):
    __tablename__ = 'emprestimos'

    id = Column(Integer, primary_key=True, autoincrement=True)
    pessoa_id = Column(Integer, ForeignKey('pessoas.id'), nullable=False)
    data_emprestimo = Column(DateTime, default=datetime.now)
    data_previsao_devolucao = Column(DateTime)
    data_devolucao = Column(DateTime, nullable=True)
    status = Column(String(20), default="Aberto")
    observacao = Column(Text)

    pessoa = relationship("Pessoa", back_populates="emprestimos")
    itens = relationship("EmprestimoItem", back_populates="emprestimo")


class EmprestimoItem(Base):
    __tablename__ = 'emprestimo_itens'

    id = Column(Integer, primary_key=True, autoincrement=True)
    emprestimo_id = Column(Integer, ForeignKey('emprestimos.id'), nullable=False)
    bem_id = Column(Integer, ForeignKey('bens_materiais.id'), nullable=False)
    quantidade = Column(Integer, default=1)

    emprestimo = relationship("Emprestimo", back_populates="itens")
    bem = relationship("BemMaterial", back_populates="emprestimos_itens")


class BaixaBem(Base):
    __tablename__ = 'baixas_bens'

    id = Column(Integer, primary_key=True, autoincrement=True)
    bem_id = Column(Integer, ForeignKey('bens_materiais.id'), nullable=False)
    quantidade = Column(Integer, default=1)
    motivo = Column(String(100), nullable=False)
    observacao = Column(Text)
    data_baixa = Column(DateTime, default=datetime.now)

    bem = relationship("BemMaterial", back_populates="baixas")


class Danca(Base):
    __tablename__ = 'dancas'

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(150), nullable=False)
    origem = Column(String(150))
    tempo_musica = Column(String(10)) 
    interprete_compositor = Column(String(255))
    detalhamento_historico = Column(Text)
    ativo = Column(Boolean, default=True)
    data_cadastro = Column(DateTime, default=datetime.now)

    def __repr__(self):
        return f"<Danca {self.nome}>"


class Apresentacao(Base):
    __tablename__ = 'apresentacoes'

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome_evento = Column(String(150), nullable=False)
    data_evento = Column(Date, nullable=False)
    local_evento = Column(String(200), nullable=False)
    observacoes = Column(Text)
    data_cadastro = Column(DateTime, default=datetime.now)

    dancas_escaladas = relationship("ApresentacaoDanca", back_populates="apresentacao", cascade="all, delete-orphan")


class ApresentacaoDanca(Base):
    __tablename__ = 'apresentacao_dancas'

    id = Column(Integer, primary_key=True, autoincrement=True)
    apresentacao_id = Column(Integer, ForeignKey('apresentacoes.id'), nullable=False)
    danca_id = Column(Integer, ForeignKey('dancas.id'), nullable=False)
    ordem_execucao = Column(Integer, default=1)

    apresentacao = relationship("Apresentacao", back_populates="dancas_escaladas")
    danca = relationship("Danca")
    integrantes = relationship("ApresentacaoIntegrante", back_populates="apresentacao_danca", cascade="all, delete-orphan")


class ApresentacaoIntegrante(Base):
    __tablename__ = 'apresentacao_integrantes'

    id = Column(Integer, primary_key=True, autoincrement=True)
    apresentacao_danca_id = Column(Integer, ForeignKey('apresentacao_dancas.id'), nullable=False)
    pessoa_id = Column(Integer, ForeignKey('pessoas.id'), nullable=False)

    apresentacao_danca = relationship("ApresentacaoDanca", back_populates="integrantes")
    pessoa = relationship("Pessoa")