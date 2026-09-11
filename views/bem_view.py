# views/bem_view.py
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, 
    QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, 
    QHeaderView, QAbstractItemView
)
from PyQt6.QtCore import Qt
from controllers.bem_controller import BemController

class BemView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
        self.carregar_dados()

    def _init_ui(self):
        layout_principal = QVBoxLayout()

        # Filtros
        box_filtro = QGroupBox("Consulta do Patrimônio")
        lay_filtro = QHBoxLayout()

        lay_filtro.addWidget(QLabel("Filtrar Patrimônio:"))
        self.txt_filtro = QLineEdit()
        self.txt_filtro.setPlaceholderText("Buscar por Código, Nome ou Categoria...")
        self.txt_filtro.textChanged.connect(self.carregar_dados)
        lay_filtro.addWidget(self.txt_filtro)

        btn_atualizar = QPushButton("Atualizar")
        btn_atualizar.clicked.connect(self.carregar_dados)
        lay_filtro.addWidget(btn_atualizar)

        box_filtro.setLayout(lay_filtro)
        layout_principal.addWidget(box_filtro)

        # Tabela (6 Colunas - Sem ID)
        self.tabela = QTableWidget()
        self.tabela.setColumnCount(6)
        self.tabela.setHorizontalHeaderLabels([
            "Código", "Nome do Material", "Categoria", 
            "Valor Estimado (R$)", "Conservação", "Status"
        ])
        self.tabela.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tabela.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tabela.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)

        layout_principal.addWidget(self.tabela)
        self.setLayout(layout_principal)

    def carregar_dados(self):
        filtro = self.txt_filtro.text().strip()
        bens = BemController.listar_todos(filtro)

        self.tabela.setRowCount(0)
        for b in bens:
            pos = self.tabela.rowCount()
            self.tabela.insertRow(pos)

            # Código do Patrimônio com o ID oculto via UserRole
            item_codigo = QTableWidgetItem(getattr(b, 'codigo_patrimonio', ''))
            item_codigo.setData(Qt.ItemDataRole.UserRole, getattr(b, 'id', None))

            valor = getattr(b, 'valor_estimado', 0.0) or 0.0

            self.tabela.setItem(pos, 0, item_codigo)
            self.tabela.setItem(pos, 1, QTableWidgetItem(getattr(b, 'nome', '') or ''))
            self.tabela.setItem(pos, 2, QTableWidgetItem(getattr(b, 'categoria', '') or ''))
            self.tabela.setItem(pos, 3, QTableWidgetItem(f"R$ {valor:.2f}"))
            self.tabela.setItem(pos, 4, QTableWidgetItem(getattr(b, 'estado_conservacao', '') or ''))
            self.tabela.setItem(pos, 5, QTableWidgetItem(getattr(b, 'status', '') or ''))