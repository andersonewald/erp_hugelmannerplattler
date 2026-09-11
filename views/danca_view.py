# views/danca_view.py
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, 
    QLineEdit, QTextEdit, QPushButton, QTableWidget, QTableWidgetItem, 
    QHeaderView, QAbstractItemView, QMessageBox
)
from PyQt6.QtCore import Qt
from controllers.danca_controller import DancaController


class DancaView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.danca_id_selecionado = None
        self._init_ui()
        self.carregar_dados()

    def _init_ui(self):
        layout_principal = QVBoxLayout(self)

        # FORMULÁRIO DE CADASTRO
        box_form = QGroupBox("Cadastrar / Editar Dança")
        lay_form = QVBoxLayout()

        # Linha 1: Nome e Origem
        lay_l1 = QHBoxLayout()
        lay_l1.addWidget(QLabel("Nome da Dança:*"))
        self.txt_nome = QLineEdit()
        self.txt_nome.setPlaceholderText("Ex: Kronentanz, Sternpolka...")
        lay_l1.addWidget(self.txt_nome)

        lay_l1.addWidget(QLabel("Origem / Região:"))
        self.txt_origem = QLineEdit()
        self.txt_origem.setPlaceholderText("Ex: Baviera - Alemanha, Áustria...")
        lay_l1.addWidget(self.txt_origem)

        lay_form.addLayout(lay_l1)

        # Linha 2: Detalhamento Histórico (Campo de Texto Longo)
        lay_form.addWidget(QLabel("Detalhamento Histórico e Significado:"))
        self.txt_historico = QTextEdit()
        self.txt_historico.setPlaceholderText("Digite aqui a história, significado das figuras, particularidades das vestimentas ou orientações da dança...")
        self.txt_historico.setMaximumHeight(120)
        lay_form.addWidget(self.txt_historico)

        # Botões de Ação
        lay_botoes = QHBoxLayout()
        lay_botoes.addStretch()

        self.btn_salvar = QPushButton("💾 Salvar Dança")
        self.btn_salvar.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold; padding: 8px 15px;")
        self.btn_salvar.clicked.connect(self.salvar_danca)
        lay_botoes.addWidget(self.btn_salvar)

        btn_limpar = QPushButton("🧹 Cancelar / Limpar")
        btn_limpar.clicked.connect(self.limpar_formulario)
        lay_botoes.addWidget(btn_limpar)

        lay_form.addLayout(lay_botoes)
        box_form.setLayout(lay_form)
        layout_principal.addWidget(box_form)

        # TABELA DE CONSULTA
        box_tabela = QGroupBox("Repertório de Danças Cadastradas (Duplo clique para editar)")
        lay_tab = QVBoxLayout()

        # Filtro de Busca
        lay_filtro = QHBoxLayout()
        lay_filtro.addWidget(QLabel("Buscar Dança:"))
        self.txt_filtro = QLineEdit()
        self.txt_filtro.setPlaceholderText("Buscar por Nome ou Origem...")
        self.txt_filtro.textChanged.connect(self.carregar_dados)
        lay_filtro.addWidget(self.txt_filtro)
        lay_tab.addLayout(lay_filtro)

        # Tabela
        self.tabela = QTableWidget()
        self.tabela.setColumnCount(3)
        self.tabela.setHorizontalHeaderLabels(["Nome da Dança", "Origem", "Histórico / Resumo"])
        self.tabela.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tabela.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tabela.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        self.tabela.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)
        self.tabela.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)

        self.tabela.cellDoubleClicked.connect(self.carregar_danca_para_edicao)

        lay_tab.addWidget(self.tabela)
        box_tabela.setLayout(lay_tab)
        layout_principal.addWidget(box_tabela)

    def salvar_danca(self):
        dados = {
            "nome": self.txt_nome.text(),
            "origem": self.txt_origem.text(),
            "detalhamento_historico": self.txt_historico.toPlainText()
        }

        sucesso, msg = DancaController.salvar_danca(dados, self.danca_id_selecionado)
        if sucesso:
            QMessageBox.information(self, "Sucesso", msg)
            self.limpar_formulario()
            self.carregar_dados()
        else:
            QMessageBox.critical(self, "Erro", msg)

    def carregar_danca_para_edicao(self, row, column):
        item_nome = self.tabela.item(row, 0)
        danca_id = item_nome.data(Qt.ItemDataRole.UserRole) if item_nome else None

        if not danca_id:
            return

        danca = DancaController.buscar_por_id(danca_id)
        if not danca:
            QMessageBox.warning(self, "Aviso", "Não foi possível carregar os dados da dança selecionada.")
            return

        self.danca_id_selecionado = danca.id
        self.txt_nome.setText(danca.nome or "")
        self.txt_origem.setText(danca.origem or "")
        self.txt_historico.setPlainText(danca.detalhamento_historico or "")

        self.btn_salvar.setText("✏️ Atualizar Dança")
        self.btn_salvar.setStyleSheet("background-color: #e67e22; color: white; font-weight: bold; padding: 8px 15px;")

    def limpar_formulario(self):
        self.danca_id_selecionado = None
        self.txt_nome.clear()
        self.txt_origem.clear()
        self.txt_historico.clear()

        self.btn_salvar.setText("💾 Salvar Dança")
        self.btn_salvar.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold; padding: 8px 15px;")

    def carregar_dados(self):
        filtro = self.txt_filtro.text().strip()
        dancas = DancaController.listar_dancas(filtro)

        self.tabela.setRowCount(0)
        for d in dancas:
            pos = self.tabela.rowCount()
            self.tabela.insertRow(pos)

            nome_item = QTableWidgetItem(getattr(d, 'nome', ''))
            nome_item.setData(Qt.ItemDataRole.UserRole, getattr(d, 'id', None))

            origem = getattr(d, 'origem', '') or '—'
            historico = getattr(d, 'detalhamento_historico', '') or '—'
            
            # Limita a visualização do histórico na tabela para não ocupar muito espaço visual
            resumo_historico = historico if len(historico) <= 80 else f"{historico[:77]}..."

            self.tabela.setItem(pos, 0, nome_item)
            self.tabela.setItem(pos, 1, QTableWidgetItem(origem))
            self.tabela.setItem(pos, 2, QTableWidgetItem(resumo_historico))