# controllers/pessoa_controller.py
from datetime import datetime
from config.database import get_db
from models.models import Pessoa, Apresentacao, ApresentacaoDanca, ApresentacaoIntegrante, Danca


class PessoaController:

    @staticmethod
    def listar_pessoas(filtro=""):
        db = get_db()
        try:
            query = db.query(Pessoa)
            if filtro:
                termo = f"%{filtro}%"
                query = query.filter(
                    (Pessoa.nome.ilike(termo)) | 
                    (Pessoa.cpf_rg.ilike(termo)) | 
                    (Pessoa.categoria.ilike(termo)) |
                    (Pessoa.status.ilike(termo))
                )
            return query.order_by(Pessoa.nome.asc()).all()
        finally:
            db.close()

    @staticmethod
    def buscar_por_id(pessoa_id: int):
        """Busca os dados completos de uma pessoa pelo ID."""
        db = get_db()
        try:
            return db.query(Pessoa).filter(Pessoa.id == pessoa_id).first()
        finally:
            db.close()

    @staticmethod
    def salvar_pessoa(dados: dict, pessoa_id: int = None):
        """Cadastra um novo integrante ou atualiza um existente se pessoa_id for fornecido."""
        db = get_db()
        try:
            nome = dados.get("nome", "").strip()
            if not nome:
                return False, "O campo 'Nome Completo' é obrigatório!"

            # Tratamento flexível de data de nascimento (formato YYYY-MM-DD do HTML5 ou DD/MM/YYYY)
            dt_nasc = None
            raw_date = dados.get("data_nascimento")
            if raw_date:
                if isinstance(raw_date, str):
                    for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
                        try:
                            dt_nasc = datetime.strptime(raw_date, fmt).date()
                            break
                        except ValueError:
                            pass
                elif hasattr(raw_date, 'year'):
                    dt_nasc = raw_date

            # Captura dos novos campos de vínculo
            status_val = dados.get("status", "Ativo")
            mes_ano_entrada = dados.get("mes_ano_entrada")
            mes_ano_saida = dados.get("mes_ano_saida") if status_val in ["Inativo", "Afastado"] else None

            if pessoa_id:
                pessoa = db.query(Pessoa).filter(Pessoa.id == pessoa_id).first()
                if not pessoa:
                    return False, "Registro não encontrado para atualização!"
            else:
                pessoa = Pessoa()
                db.add(pessoa)

            # Atribuição dos campos principais e de controle
            pessoa.nome = nome
            pessoa.cpf_rg = dados.get("cpf_rg")
            pessoa.telefone = dados.get("telefone")
            pessoa.email = dados.get("email")
            pessoa.categoria = dados.get("categoria", "Integrante")
            
            # NOVOS CAMPOS DE CONTROLE
            pessoa.mes_ano_entrada = mes_ano_entrada
            pessoa.mes_ano_saida = mes_ano_saida
            pessoa.status = status_val
            pessoa.ativo = True if status_val != "Inativo" else False

            # Dados Pessoais
            pessoa.data_nascimento = dt_nasc
            pessoa.genero = dados.get("genero")
            pessoa.nacionalidade = dados.get("nacionalidade")
            pessoa.naturalidade = dados.get("naturalidade")
            pessoa.estado_civil = dados.get("estado_civil")
            if dados.get("foto_path"):
                pessoa.foto_path = dados.get("foto_path")

            # Documentação
            pessoa.rg_orgao_uf = dados.get("rg_orgao_uf")
            pessoa.cnh = dados.get("cnh")
            pessoa.cartao_sus = dados.get("cartao_sus")
            pessoa.titulo_eleitor = dados.get("titulo_eleitor")
            pessoa.passaporte = dados.get("passaporte")

            # Endereço
            pessoa.rua = dados.get("rua")
            pessoa.numero = dados.get("numero")
            pessoa.complemento = dados.get("complemento")
            pessoa.bairro = dados.get("bairro")
            pessoa.cidade = dados.get("cidade")
            pessoa.estado = dados.get("estado")
            pessoa.cep = dados.get("cep")

            # Saúde e Emergência
            pessoa.possui_plano_saude = dados.get("possui_plano_saude", False)
            pessoa.plano_saude_info = dados.get("plano_saude_info")
            pessoa.alergias = dados.get("alergias")
            pessoa.medicamentos_continuos = dados.get("medicamentos_continuos")
            pessoa.restricoes_alimentares = dados.get("restricoes_alimentares")
            pessoa.condicoes_medicas = dados.get("condicoes_medicas")
            pessoa.contato_emergencia_nome = dados.get("contato_emergencia_nome")
            pessoa.contato_emergencia_telefone = dados.get("contato_emergencia_telefone")
            pessoa.contato_emergencia_parentesco = dados.get("contato_emergencia_parentesco")

            db.commit()
            msg = "Cadastro atualizado com sucesso!" if pessoa_id else "Integrante cadastrado com sucesso!"
            return True, msg

        except Exception as e:
            db.rollback()
            return False, f"Erro ao salvar integrante: {str(e)}"
        finally:
            db.close()

    @staticmethod
    def buscar_detalhes_completos(pessoa_id: int):
        """Retorna os dados cadastrais da pessoa e seu histórico cruzado de apresentações."""
        db = get_db()
        try:
            pessoa = db.query(Pessoa).filter(Pessoa.id == pessoa_id).first()
            if not pessoa:
                return None

            # Consulta as apresentações e danças em que a pessoa participou
            participacoes = (
                db.query(Apresentacao, Danca)
                .join(ApresentacaoDanca, Apresentacao.id == ApresentacaoDanca.apresentacao_id)
                .join(ApresentacaoIntegrante, ApresentacaoDanca.id == ApresentacaoIntegrante.apresentacao_danca_id)
                .join(Danca, ApresentacaoDanca.danca_id == Danca.id)
                .filter(ApresentacaoIntegrante.pessoa_id == pessoa_id)
                .order_by(Apresentacao.data_evento.desc())
                .all()
            )

            # Agrupa as danças por evento
            historico_eventos = {}
            for ap, danca in participacoes:
                if ap.id not in historico_eventos:
                    historico_eventos[ap.id] = {
                        "nome_evento": ap.nome_evento,
                        "data_evento": ap.data_evento,
                        "local_evento": ap.local_evento,
                        "dancas": []
                    }
                if danca.nome not in historico_eventos[ap.id]["dancas"]:
                    historico_eventos[ap.id]["dancas"].append(danca.nome)

            return {
                "pessoa": pessoa,
                "historico": list(historico_eventos.values())
            }
        finally:
            db.close()