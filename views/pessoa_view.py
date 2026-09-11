# views/pessoa_view.py
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, 
    QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, 
    QHeaderView, QAbstractItemView, QMessageBox, QComboBox,
    QCheckBox, QFileDialog, QScrollArea, QDateEdit
)
from PyQt6.QtCore import Qt, QDate
from controllers.pessoa_controller import PessoaController


class PessoaView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.caminho_foto = ""
        self.pessoa_id_selecionado = None  # Armazena o ID quando estiver editando
        self._init_ui()
        self.carregar_dados()

    def _init_ui(self):
        layout_principal = QVBoxLayout(self)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        container_form = QWidget()
        lay_form = QVBoxLayout(container_form)

        # 1. DADOS PESSOAIS
        box_pessoais = QGroupBox("1. Dados Pessoais")
        lay_p = QVBoxLayout()
        
        lay_p1 = QHBoxLayout()
        lay_p1.addWidget(QLabel("Nome Completo:*"))
        self.txt_nome = QLineEdit()
        lay_p1.addWidget(self.txt_nome)

        lay_p1.addWidget(QLabel("Data Nascimento:"))
        self.dt_nascimento = QDateEdit()
        self.dt_nascimento.setDisplayFormat("dd/MM/yyyy")
        self.dt_nascimento.setDate(QDate.currentDate())
        lay_p1.addWidget(self.dt_nascimento)

        lay_p1.addWidget(QLabel("Gênero:"))
        self.combo_genero = QComboBox()
        self.combo_genero.addItems(["Masculino", "Feminino", "Outro", "Não Informar"])
        lay_p1.addWidget(self.combo_genero)

        lay_p.addLayout(lay_p1)

        lay_p2 = QHBoxLayout()
        lay_p2.addWidget(QLabel("Nacionalidade:"))
        self.txt_nacionalidade = QLineEdit("Brasileira")
        lay_p2.addWidget(self.txt_nacionalidade)

        lay_p2.addWidget(QLabel("Naturalidade:"))
        self.txt_naturalidade = QLineEdit()
        lay_p2.addWidget(self.txt_naturalidade)

        lay_p2.addWidget(QLabel("Estado Civil:"))
        self.combo_estado_civil = QComboBox()
        self.combo_estado_civil.addItems(["Solteiro(a)", "Casado(a)", "Divorciado(a)", "Viúvo(a)", "União Estável"])
        lay_p2.addWidget(self.combo_estado_civil)

        lay_p2.addWidget(QLabel("Vínculo:"))
        self.combo_categoria = QComboBox()
        self.combo_categoria.addItems(["Dançarino(a)", "Diretoria", "Músico", "Colaborador"])
        lay_p2.addWidget(self.combo_categoria)

        lay_p.addLayout(lay_p2)

        lay_foto = QHBoxLayout()
        self.lbl_foto = QLabel("Foto 3x4: Nenhuma selecionada")
        self.btn_foto = QPushButton("📁 Selecionar Foto 3x4")
        self.btn_foto.clicked.connect(self.selecionar_foto)
        lay_foto.addWidget(self.lbl_foto)
        lay_foto.addWidget(self.btn_foto)
        lay_foto.addStretch()
        lay_p.addLayout(lay_foto)

        box_pessoais.setLayout(lay_p)
        lay_form.addWidget(box_pessoais)

        # 2. DOCUMENTAÇÃO E CONTATOS
        box_docs = QGroupBox("2. Documentação e Contatos")
        lay_d = QVBoxLayout()

        lay_d1 = QHBoxLayout()
        lay_d1.addWidget(QLabel("CPF:"))
        self.txt_cpf = QLineEdit()
        lay_d1.addWidget(self.txt_cpf)

        lay_d1.addWidget(QLabel("RG / Org. Emissor / UF:"))
        self.txt_rg = QLineEdit()
        lay_d1.addWidget(self.txt_rg)

        lay_d1.addWidget(QLabel("CNH:"))
        self.txt_cnh = QLineEdit()
        lay_d1.addWidget(self.txt_cnh)

        lay_d.addLayout(lay_d1)

        lay_d2 = QHBoxLayout()
        lay_d2.addWidget(QLabel("Cartão SUS:"))
        self.txt_sus = QLineEdit()
        lay_d2.addWidget(self.txt_sus)

        lay_d2.addWidget(QLabel("Título de Eleitor:"))
        self.txt_titulo = QLineEdit()
        lay_d2.addWidget(self.txt_titulo)

        lay_d2.addWidget(QLabel("Passaporte:"))
        self.txt_passaporte = QLineEdit()
        lay_d2.addWidget(self.txt_passaporte)

        lay_d.addLayout(lay_d2)

        lay_d3 = QHBoxLayout()
        lay_d3.addWidget(QLabel("Telefone:"))
        self.txt_telefone = QLineEdit()
        lay_d3.addWidget(self.txt_telefone)

        lay_d3.addWidget(QLabel("E-mail:"))
        self.txt_email = QLineEdit()
        lay_d3.addWidget(self.txt_email)

        lay_d.addLayout(lay_d3)

        box_docs.setLayout(lay_d)
        lay_form.addWidget(box_docs)

        # 3. ENDEREÇO
        box_end = QGroupBox("3. Endereço")
        lay_e = QVBoxLayout()

        lay_e1 = QHBoxLayout()
        lay_e1.addWidget(QLabel("Rua / Avenida:"))
        self.txt_rua = QLineEdit()
        lay_e1.addWidget(self.txt_rua)

        lay_e1.addWidget(QLabel("Nº:"))
        self.txt_numero = QLineEdit()
        self.txt_numero.setMaximumWidth(80)
        lay_e1.addWidget(self.txt_numero)

        lay_e1.addWidget(QLabel("Complemento:"))
        self.txt_complemento = QLineEdit()
        lay_e1.addWidget(self.txt_complemento)

        lay_e.addLayout(lay_e1)

        lay_e2 = QHBoxLayout()
        lay_e2.addWidget(QLabel("Bairro:"))
        self.txt_bairro = QLineEdit()
        lay_e2.addWidget(self.txt_bairro)

        lay_e2.addWidget(QLabel("Cidade:"))
        self.txt_cidade = QLineEdit()
        lay_e2.addWidget(self.txt_cidade)

        lay_e2.addWidget(QLabel("UF:"))
        self.txt_uf = QLineEdit()
        self.txt_uf.setMaximumWidth(50)
        lay_e2.addWidget(self.txt_uf)

        lay_e2.addWidget(QLabel("CEP:"))
        self.txt_cep = QLineEdit()
        lay_e2.addWidget(self.txt_cep)

        lay_e.addLayout(lay_e2)

        box_end.setLayout(lay_e)
        lay_form.addWidget(box_end)

        # 4. FICHA MÉDICA E EMERGÊNCIA
        box_med = QGroupBox("4. Saúde e Contato de Emergência")
        lay_m = QVBoxLayout()

        lay_m1 = QHBoxLayout()
        self.chk_plano = QCheckBox("Possui Plano de Saúde")
        self.chk_plano.toggled.connect(lambda val: self.txt_plano_info.setEnabled(val))
        lay_m1.addWidget(self.chk_plano)

        self.txt_plano_info = QLineEdit()
        self.txt_plano_info.setPlaceholderText("Nome do plano e nº da carteirinha")
        self.txt_plano_info.setEnabled(False)
        lay_m1.addWidget(self.txt_plano_info)

        lay_m.addLayout(lay_m1)

        lay_m2 = QHBoxLayout()
        lay_m2.addWidget(QLabel("Alergias:"))
        self.txt_alergias = QLineEdit()
        lay_m2.addWidget(self.txt_alergias)

        lay_m2.addWidget(QLabel("Medicamentos Contínuos:"))
        self.txt_medicamentos = QLineEdit()
        lay_m2.addWidget(self.txt_medicamentos)

        lay_m.addLayout(lay_m2)

        lay_m3 = QHBoxLayout()
        lay_m3.addWidget(QLabel("Restrições Alimentares:"))
        self.txt_restricoes = QLineEdit()
        lay_m3.addWidget(self.txt_restricoes)

        lay_m3.addWidget(QLabel("Condições Médicas:"))
        self.txt_condicoes = QLineEdit()
        lay_m3.addWidget(self.txt_condicoes)

        lay_m.addLayout(lay_m3)

        lay_em = QHBoxLayout()
        lay_em.addWidget(QLabel("Contato Emergência (Nome):"))
        self.txt_em_nome = QLineEdit()
        lay_em.addWidget(self.txt_em_nome)

        lay_em.addWidget(QLabel("Telefone Emergência:"))
        self.txt_em_tel = QLineEdit()
        lay_em.addWidget(self.txt_em_tel)

        lay_em.addWidget(QLabel("Parentesco:"))
        self.txt_em_parentesco = QLineEdit()
        lay_em.addWidget(self.txt_em_parentesco)

        lay_m.addLayout(lay_em)

        box_med.setLayout(lay_m)
        lay_form.addWidget(box_med)

        # Botões
        lay_btn = QHBoxLayout()
        self.btn_salvar = QPushButton("💾 Salvar Cadastro")
        self.btn_salvar.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold; padding: 10px;")
        self.btn_salvar.clicked.connect(self.salvar_pessoa)

        btn_limpar = QPushButton("🧹 Cancelar / Novo Cadastro")
        btn_limpar.clicked.connect(self.limpar_formulario)

        lay_btn.addWidget(self.btn_salvar)
        lay_btn.addWidget(btn_limpar)
        lay_form.addLayout(lay_btn)

        container_form.setLayout(lay_form)
        scroll.setWidget(container_form)
        scroll.setMaximumHeight(380)

        layout_principal.addWidget(scroll)

        # TABELA DE INTEGRANTES
        box_tabela = QGroupBox("Integrantes Cadastrados (Clique duas vezes para editar)")
        lay_tab = QVBoxLayout()

        self.txt_filtro = QLineEdit()
        self.txt_filtro.setPlaceholderText("Buscar por Nome, Documento ou Categoria...")
        self.txt_filtro.textChanged.connect(self.carregar_dados)
        lay_tab.addWidget(self.txt_filtro)

        self.tabela = QTableWidget()
        self.tabela.setColumnCount(4)
        self.tabela.setHorizontalHeaderLabels(["Nome", "CPF/RG", "Telefone/E-mail", "Vínculo"])
        self.tabela.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tabela.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tabela.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        
        # Conexão do Duplo Clique
        self.tabela.cellDoubleClicked.connect(self.carregar_pessoa_para_edicao)

        lay_tab.addWidget(self.tabela)
        box_tabela.setLayout(lay_tab)

        layout_principal.addWidget(box_tabela)

    def selecionar_foto(self):
        arquivo, _ = QFileDialog.getOpenFileName(self, "Selecionar Foto 3x4", "", "Imagens (*.png *.jpg *.jpeg)")
        if arquivo:
            self.caminho_foto = arquivo
            self.lbl_foto.setText(f"Foto: {arquivo.split('/')[-1]}")

    def carregar_pessoa_para_edicao(self, row, column):
        item_nome = self.tabela.item(row, 0)
        pessoa_id = item_nome.data(Qt.ItemDataRole.UserRole) if item_nome else None

        if not pessoa_id:
            return

        pessoa = PessoaController.buscar_por_id(pessoa_id)
        if not pessoa:
            QMessageBox.warning(self, "Aviso", "Não foi possível carregar os dados da pessoa selecionada.")
            return

        self.pessoa_id_selecionado = pessoa.id

        # Preenche os campos do formulário
        self.txt_nome.setText(pessoa.nome or "")
        if pessoa.data_nascimento:
            self.dt_nascimento.setDate(QDate(pessoa.data_nascimento.year, pessoa.data_nascimento.month, pessoa.data_nascimento.day))
        
        if pessoa.genero:
            self.combo_genero.setCurrentText(pessoa.genero)
        self.txt_nacionalidade.setText(pessoa.nacionalidade or "")
        self.txt_naturalidade.setText(pessoa.naturalidade or "")
        if pessoa.estado_civil:
            self.combo_estado_civil.setCurrentText(pessoa.estado_civil)
        if pessoa.categoria:
            self.combo_categoria.setCurrentText(pessoa.categoria)

        self.caminho_foto = pessoa.foto_path or ""
        self.lbl_foto.setText(f"Foto: {self.caminho_foto.split('/')[-1]}" if self.caminho_foto else "Foto 3x4: Nenhuma selecionada")

        self.txt_cpf.setText(pessoa.cpf_rg or "")
        self.txt_rg.setText(pessoa.rg_orgao_uf or "")
        self.txt_cnh.setText(pessoa.cnh or "")
        self.txt_sus.setText(pessoa.cartao_sus or "")
        self.txt_titulo.setText(pessoa.titulo_eleitor or "")
        self.txt_passaporte.setText(pessoa.passaporte or "")
        self.txt_telefone.setText(pessoa.telefone or "")
        self.txt_email.setText(pessoa.email or "")

        self.txt_rua.setText(pessoa.rua or "")
        self.txt_numero.setText(pessoa.numero or "")
        self.txt_complemento.setText(pessoa.complemento or "")
        self.txt_bairro.setText(pessoa.bairro or "")
        self.txt_cidade.setText(pessoa.cidade or "")
        self.txt_uf.setText(pessoa.estado or "")
        self.txt_cep.setText(pessoa.cep or "")

        self.chk_plano.setChecked(bool(pessoa.possui_plano_saude))
        self.txt_plano_info.setText(pessoa.plano_saude_info or "")
        self.txt_alergias.setText(pessoa.alergias or "")
        self.txt_medicamentos.setText(pessoa.medicamentos_continuos or "")
        self.txt_restricoes.setText(pessoa.restricoes_alimentares or "")
        self.txt_condicoes.setText(pessoa.condicoes_medicas or "")

        self.txt_em_nome.setText(pessoa.contato_emergencia_nome or "")
        self.txt_em_tel.setText(pessoa.contato_emergencia_telefone or "")
        self.txt_em_parentesco.setText(pessoa.contato_emergencia_parentesco or "")

        self.btn_salvar.setText("✏️ Atualizar Cadastro")
        self.btn_salvar.setStyleSheet("background-color: #e67e22; color: white; font-weight: bold; padding: 10px;")

    def salvar_pessoa(self):
        dados = {
            "nome": self.txt_nome.text(),
            "data_nascimento": self.dt_nascimento.text(),
            "genero": self.combo_genero.currentText(),
            "nacionalidade": self.txt_nacionalidade.text(),
            "naturalidade": self.txt_naturalidade.text(),
            "estado_civil": self.combo_estado_civil.currentText(),
            "categoria": self.combo_categoria.currentText(),
            "foto_path": self.caminho_foto,

            "cpf_rg": self.txt_cpf.text(),
            "rg_orgao_uf": self.txt_rg.text(),
            "cnh": self.txt_cnh.text(),
            "cartao_sus": self.txt_sus.text(),
            "titulo_eleitor": self.txt_titulo.text(),
            "passaporte": self.txt_passaporte.text(),
            "telefone": self.txt_telefone.text(),
            "email": self.txt_email.text(),

            "rua": self.txt_rua.text(),
            "numero": self.txt_numero.text(),
            "complemento": self.txt_complemento.text(),
            "bairro": self.txt_bairro.text(),
            "cidade": self.txt_cidade.text(),
            "estado": self.txt_uf.text(),
            "cep": self.txt_cep.text(),

            "possui_plano_saude": self.chk_plano.isChecked(),
            "plano_saude_info": self.txt_plano_info.text(),
            "alergias": self.txt_alergias.text(),
            "medicamentos_continuos": self.txt_medicamentos.text(),
            "restricoes_alimentares": self.txt_restricoes.text(),
            "condicoes_medicas": self.txt_condicoes.text(),
            "contato_emergencia_nome": self.txt_em_nome.text(),
            "contato_emergencia_telefone": self.txt_em_tel.text(),
            "contato_emergencia_parentesco": self.txt_em_parentesco.text(),
        }

        sucesso, msg = PessoaController.salvar_pessoa(dados, self.pessoa_id_selecionado)
        if sucesso:
            QMessageBox.information(self, "Sucesso", msg)
            self.limpar_formulario()
            self.carregar_dados()
        else:
            QMessageBox.critical(self, "Erro", msg)

    def limpar_formulario(self):
        self.pessoa_id_selecionado = None
        self.btn_salvar.setText("💾 Salvar Cadastro")
        self.btn_salvar.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold; padding: 10px;")

        self.txt_nome.clear()
        self.dt_nascimento.setDate(QDate.currentDate())
        self.combo_genero.setCurrentIndex(0)
        self.txt_nacionalidade.setText("Brasileira")
        self.txt_naturalidade.clear()
        self.combo_estado_civil.setCurrentIndex(0)
        self.combo_categoria.setCurrentIndex(0)

        self.caminho_foto = ""
        self.lbl_foto.setText("Foto 3x4: Nenhuma selecionada")

        self.txt_cpf.clear()
        self.txt_rg.clear()
        self.txt_cnh.clear()
        self.txt_sus.clear()
        self.txt_titulo.clear()
        self.txt_passaporte.clear()
        self.txt_telefone.clear()
        self.txt_email.clear()

        self.txt_rua.clear()
        self.txt_numero.clear()
        self.txt_complemento.clear()
        self.txt_bairro.clear()
        self.txt_cidade.clear()
        self.txt_uf.clear()
        self.txt_cep.clear()

        self.chk_plano.setChecked(False)
        self.txt_plano_info.clear()
        self.txt_alergias.clear()
        self.txt_medicamentos.clear()
        self.txt_restricoes.clear()
        self.txt_condicoes.clear()

        self.txt_em_nome.clear()
        self.txt_em_tel.clear()
        self.txt_em_parentesco.clear()

    def carregar_dados(self):
        filtro = self.txt_filtro.text().strip()
        pessoas = PessoaController.listar_pessoas(filtro)

        self.tabela.setRowCount(0)
        for p in pessoas:
            pos = self.tabela.rowCount()
            self.tabela.insertRow(pos)

            nome_item = QTableWidgetItem(getattr(p, 'nome', ''))
            nome_item.setData(Qt.ItemDataRole.UserRole, getattr(p, 'id', None))

            doc = getattr(p, 'cpf_rg', '') or '—'
            tel = getattr(p, 'telefone', '') or '—'
            email = getattr(p, 'email', '') or ''
            contato = f"{tel} | {email}" if email else tel
            cat = getattr(p, 'categoria', '') or '—'

            self.tabela.setItem(pos, 0, nome_item)
            self.tabela.setItem(pos, 1, QTableWidgetItem(doc))
            self.tabela.setItem(pos, 2, QTableWidgetItem(contato))
            self.tabela.setItem(pos, 3, QTableWidgetItem(cat))