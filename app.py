# app.py
import io
import os
from datetime import date
from flask import Flask, render_template, request, redirect, url_for, flash, send_file, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from PIL import Image

from config.database import get_db
from models.models import Pessoa, Danca, Apresentacao, Usuario, BemMaterial, FotoBemMaterial
from controllers.pessoa_controller import PessoaController
from controllers.danca_controller import DancaController
from controllers.apresentacao_controller import ApresentacaoController
from controllers.bem_controller import BemController
from controllers.emprestimo_controller import EmprestimoController
from utils.pdf_generator import RelatorioApresentacaoPDF, RelatorioPessoaPDF
from controllers.usuario_controller import UsuarioController

app = Flask(__name__)
app.secret_key = 'hugelmannerplattler_secret_key'

UPLOAD_FOLDER = os.path.join('static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def otimizar_imagem(arquivo_stream, tamanho_max=(1280, 1280), qualidade=80):
    """
    Redimensiona e comprime a imagem enviada para economizar espaço 
    no banco de dados sem perder qualidade perceptível.
    """
    try:
        img = Image.open(arquivo_stream)
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
            
        img.thumbnail(tamanho_max)
        
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=qualidade, optimize=True)
        return buffer.getvalue(), "image/jpeg"
    except Exception:
        arquivo_stream.seek(0)
        return arquivo_stream.read(), arquivo_stream.content_type


# -----------------------------------------------------------------------------
# LOGIN E SEGURANÇA
# -----------------------------------------------------------------------------

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login_input = request.form.get('login', '').strip()
        senha_input = request.form.get('senha', '').strip()

        db = get_db()
        try:
            usuario = db.query(Usuario).filter(Usuario.login == login_input, Usuario.ativo == True).first()
            if usuario and check_password_hash(usuario.senha_hash, senha_input):
                session['usuario_id'] = usuario.id
                session['usuario_nome'] = usuario.nome
                flash(f"Bem-vindo(a), {usuario.nome}!", "success")
                return redirect(url_for('dashboard'))
            else:
                flash("Usuário ou senha inválidos.", "danger")
        finally:
            db.close()

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash("Sessão encerrada com sucesso.", "info")
    return redirect(url_for('login'))


# -----------------------------------------------------------------------------
# DASHBOARD
# -----------------------------------------------------------------------------

@app.route('/')
def dashboard():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))

    db = get_db()
    try:
        total_integrantes = db.query(Pessoa).filter(Pessoa.ativo == True).count()
        total_dancas = db.query(Danca).filter(Danca.ativo == True).count()
        proximas_apresentacoes = db.query(Apresentacao).filter(Apresentacao.data_evento >= date.today()).count()

        return render_template('index.html', 
                               total_integrantes=total_integrantes,
                               total_dancas=total_dancas,
                               proximas_apresentacoes=proximas_apresentacoes)
    finally:
        db.close()


# -----------------------------------------------------------------------------
# MATERIAIS / BENS PATRIMONIAIS
# -----------------------------------------------------------------------------

@app.route('/materiais', methods=['GET', 'POST'])
def materiais():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        acao = request.form.get('acao')

        if acao == 'cadastrar_lote':
            nome = request.form.get('nome')
            descricao = request.form.get('descricao', '')
            categoria = request.form.get('categoria')
            quantidade = int(request.form.get('quantidade', 1))
            valor_unitario = float(request.form.get('valor_unitario') or 0.0)
            estado = request.form.get('estado_conservacao', 'Bom')
            prefixo = request.form.get('prefixo', 'PAT-')

            # Processamento de Múltiplas Fotos enviadas no formulário
            fotos_salvas = []
            fotos_enviadas = request.files.getlist('fotos')
            for arq in fotos_enviadas:
                if arq and arq.filename != '':
                    foto_bytes, mimetype = otimizar_imagem(arq)
                    fotos_salvas.append((foto_bytes, mimetype))

            sucesso, msg = BemController.cadastrar_lote(
                nome=nome, 
                descricao=descricao, 
                categoria=categoria, 
                quantidade=quantidade, 
                valor_unitario=valor_unitario, 
                estado=estado, 
                prefixo=prefixo,
                fotos=fotos_salvas
            )
            flash(msg, 'success' if sucesso else 'danger')

        elif acao == 'editar':
            id_bem = int(request.form.get('bem_id'))
            estado = request.form.get('estado_conservacao')
            descricao = request.form.get('descricao', '')
            valor = float(request.form.get('valor_estimado') or 0.0)

            # Processamento de Fotos Adicionais no formulário de edição
            fotos_salvas = []
            fotos_enviadas = request.files.getlist('fotos')
            for arq in fotos_enviadas:
                if arq and arq.filename != '':
                    foto_bytes, mimetype = otimizar_imagem(arq)
                    fotos_salvas.append((foto_bytes, mimetype))

            sucesso, msg = BemController.salvar_edicao(
                id_bem=id_bem, 
                estado=estado, 
                descricao=descricao, 
                valor=valor,
                fotos=fotos_salvas
            )
            flash(msg, 'success' if sucesso else 'danger')

        return redirect(url_for('materiais'))

    busca = request.args.get('busca', '')
    lista_bens = BemController.listar_todos(busca)
    return render_template('materiais.html', bens=lista_bens, busca=busca)


@app.route('/materiais/<int:id_bem>/excluir', methods=['POST'])
def excluir_material(id_bem):
    if 'usuario_id' not in session:
        return redirect(url_for('login'))

    sucesso, msg = BemController.excluir(id_bem)
    flash(msg, 'success' if sucesso else 'danger')
    return redirect(url_for('materiais'))


@app.route('/materiais/foto/<int:foto_id>/deletar', methods=['POST', 'DELETE'])
def deletar_foto_material(foto_id):
    if 'usuario_id' not in session:
        return jsonify({'sucesso': False, 'mensagem': 'Acesso negado.'}), 403

    db = get_db()
    try:
        foto = db.query(FotoBemMaterial).get(foto_id)
        if not foto:
            return jsonify({'sucesso': False, 'mensagem': 'Foto não encontrada.'}), 404

        db.delete(foto)
        db.commit()
        return jsonify({'sucesso': True, 'mensagem': 'Foto removida com sucesso!'})
    except Exception as e:
        db.rollback()
        return jsonify({'sucesso': False, 'mensagem': str(e)}), 500
    finally:
        db.close()


# -----------------------------------------------------------------------------
# EMPRÉSTIMOS
# -----------------------------------------------------------------------------

@app.route('/emprestimos', methods=['GET', 'POST'])
def emprestimos():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        pessoa_id = int(request.form.get('pessoa_id'))
        bem_id = int(request.form.get('bem_id'))
        data_prev_str = request.form.get('data_previsao') # Ex: YYYY-MM-DD
        obs = request.form.get('observacao', '')

        if data_prev_str:
            partes = data_prev_str.split('-')
            data_prev_fmt = f"{partes[2]}/{partes[1]}/{partes[0]}"
        else:
            data_prev_fmt = ""

        sucesso, msg = EmprestimoController.registrar_emprestimo(pessoa_id, bem_id, data_prev_fmt, obs)
        flash(msg, 'success' if sucesso else 'danger')
        return redirect(url_for('emprestimos'))

    status_filtro = request.args.get('status', 'Aberto')
    lista_emprestimos = EmprestimoController.listar_emprestimos(status_filtro)
    
    pessoas = PessoaController.listar_pessoas()
    todos_bens = BemController.listar_todos()
    bens_disponiveis = [b for b in todos_bens if b.status == 'Disponível']

    return render_template('emprestimos.html', 
                           emprestimos=lista_emprestimos, 
                           pessoas=pessoas, 
                           bens=bens_disponiveis, 
                           status_filtro=status_filtro)


@app.route('/emprestimos/<int:emprestimo_id>/devolver', methods=['POST'])
def devolver_emprestimo(emprestimo_id):
    if 'usuario_id' not in session:
        return redirect(url_for('login'))

    sucesso, msg = EmprestimoController.devolver_emprestimo(emprestimo_id)
    flash(msg, 'success' if sucesso else 'danger')
    return redirect(url_for('emprestimos'))


# -----------------------------------------------------------------------------
# PESSOAS / INTEGRANTES
# -----------------------------------------------------------------------------

@app.route('/pessoas', methods=['GET', 'POST'])
def pessoas():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        foto = request.files.get('foto')
        caminho_foto = None
        if foto and foto.filename:
            caminho_foto = os.path.join(app.config['UPLOAD_FOLDER'], foto.filename)
            foto.save(caminho_foto)

        dados = {
            "nome": request.form.get('nome'),
            "data_nascimento": request.form.get('data_nascimento'),
            "genero": request.form.get('genero'),
            "categoria": request.form.get('categoria'),
            
            "mes_ano_entrada": request.form.get('mes_ano_entrada'),
            "status": request.form.get('status', 'Ativo'),
            "mes_ano_saida": request.form.get('mes_ano_saida'),
            
            "foto_path": caminho_foto,
            "cpf_rg": request.form.get('cpf_rg'),
            "telefone": request.form.get('telefone'),
            "email": request.form.get('email'),
            "rua": request.form.get('rua'),
            "cidade": request.form.get('cidade'),
            "estado": request.form.get('estado'),
            "possui_plano_saude": True if request.form.get('possui_plano_saude') else False,
            "alergias": request.form.get('alergias'),
            "contato_emergencia_nome": request.form.get('contato_emergencia_nome'),
            "contato_emergencia_telefone": request.form.get('contato_emergencia_telefone'),
        }
        
        pessoa_id = request.form.get('pessoa_id')
        pessoa_id = int(pessoa_id) if pessoa_id else None

        sucesso, msg = PessoaController.salvar_pessoa(dados, pessoa_id)
        flash(msg, 'success' if sucesso else 'danger')
        return redirect(url_for('pessoas'))

    busca = request.args.get('busca', '')
    lista_pessoas = PessoaController.listar_pessoas(busca)
    return render_template('pessoas.html', pessoas=lista_pessoas, busca=busca)


@app.route('/pessoas/<int:pessoa_id>/pdf')
def gerar_pdf_pessoa(pessoa_id):
    if 'usuario_id' not in session:
        return redirect(url_for('login'))

    caminho_pdf = os.path.join('static', f'ficha_integrante_{pessoa_id}.pdf')
    sucesso, msg = RelatorioPessoaPDF.gerar_pdf(pessoa_id, caminho_pdf)

    if sucesso:
        return send_file(caminho_pdf, mimetype='application/pdf')
    else:
        flash(f"Erro ao gerar ficha PDF: {msg}", "danger")
        return redirect(url_for('pessoas'))


# -----------------------------------------------------------------------------
# DANÇAS
# -----------------------------------------------------------------------------

@app.route('/dancas', methods=['GET', 'POST'])
def dancas():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        dados = {
            "nome": request.form.get('nome'),
            "origem": request.form.get('origem'),
            "tempo_musica": request.form.get('tempo_musica'),
            "interprete_compositor": request.form.get('interprete_compositor'),
            "detalhamento_historico": request.form.get('detalhamento_historico')
        }
        danca_id = request.form.get('danca_id')
        danca_id = int(danca_id) if danca_id else None

        sucesso, msg = DancaController.salvar_danca(dados, danca_id)
        flash(msg, 'success' if sucesso else 'danger')
        return redirect(url_for('dancas'))

    busca = request.args.get('busca', '')
    lista_dancas = DancaController.listar_dancas(busca)
    return render_template('dancas.html', dancas=lista_dancas, busca=busca)


# -----------------------------------------------------------------------------
# APRESENTAÇÕES
# -----------------------------------------------------------------------------

@app.route('/apresentacoes', methods=['GET', 'POST'])
def apresentacoes():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        dados = request.get_json()
        if not dados:
            return jsonify({"sucesso": False, "mensagem": "Dados inválidos."}), 400

        dados_evento = {
            "nome_evento": dados.get("nome_evento"),
            "data_evento": dados.get("data_evento"),
            "local_evento": dados.get("local_evento"),
            "observacoes": dados.get("observacoes", "")
        }
        repertorio = dados.get("repertorio", [])
        apresentacao_id = dados.get("apresentacao_id")

        sucesso, res = ApresentacaoController.salvar_apresentacao(dados_evento, repertorio, apresentacao_id)
        if sucesso:
            flash("Apresentação salva com sucesso!", "success")
            return jsonify({"sucesso": True, "id": res})
        else:
            return jsonify({"sucesso": False, "mensagem": res}), 400

    lista_apresentacoes = ApresentacaoController.listar_apresentacoes()
    lista_dancas = DancaController.listar_dancas()
    lista_pessoas = PessoaController.listar_pessoas()
    return render_template('apresentacoes.html', 
                           apresentacoes=lista_apresentacoes, 
                           dancas=lista_dancas, 
                           pessoas=lista_pessoas)


@app.route('/apresentacoes/<int:apresentacao_id>/detalhes')
def detalhes_apresentacao_json(apresentacao_id):
    detalhes = ApresentacaoController.buscar_detalhes_completos(apresentacao_id)
    if detalhes:
        if detalhes.get('data_evento'):
            detalhes['data_evento'] = detalhes['data_evento'].strftime('%Y-%m-%d')
        return jsonify(detalhes)
    return jsonify({"erro": "Apresentação não encontrada."}), 404


@app.route('/apresentacoes/<int:apresentacao_id>/pdf')
def gerar_pdf_apresentacao(apresentacao_id):
    caminho_pdf = os.path.join('static', f'roteiro_{apresentacao_id}.pdf')
    sucesso, msg = RelatorioApresentacaoPDF.gerar_pdf(apresentacao_id, caminho_pdf)
    if sucesso:
        return send_file(caminho_pdf, mimetype='application/pdf')
    else:
        flash(f"Erro ao gerar PDF: {msg}", "danger")
        return redirect(url_for('apresentacoes'))

# -----------------------------------------------------------------------------
# UTILITÁRIOS / CONTROLE DE ACESSO
# -----------------------------------------------------------------------------

@app.route('/utilitarios/usuarios', methods=['GET', 'POST'])
def usuarios():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        usuario_id = request.form.get('usuario_id')
        usuario_id = int(usuario_id) if usuario_id else None
        
        nome = request.form.get('nome')
        login_usr = request.form.get('login')
        senha = request.form.get('senha')

        sucesso, msg = UsuarioController.salvar_usuario(nome, login_usr, senha, usuario_id)
        flash(msg, 'success' if sucesso else 'danger')
        return redirect(url_for('usuarios'))

    busca = request.args.get('busca', '')
    lista_usuarios = UsuarioController.listar_todos(busca)
    return render_template('usuarios.html', usuarios=lista_usuarios, busca=busca)


@app.route('/utilitarios/usuarios/<int:usuario_id>/status', methods=['POST'])
def alternar_status_usuario(usuario_id):
    if 'usuario_id' not in session:
        return redirect(url_for('login'))

    # Evita que o usuário inative a si mesmo na sessão atual
    if usuario_id == session.get('usuario_id'):
        flash("Você não pode inativar o seu próprio usuário logado!", "danger")
        return redirect(url_for('usuarios'))

    sucesso, msg = UsuarioController.alternar_status(usuario_id)
    flash(msg, 'success' if sucesso else 'danger')
    return redirect(url_for('usuarios'))    


if __name__ == '__main__':
    app.run(debug=True, port=5000)