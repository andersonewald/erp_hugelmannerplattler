# views/emprestimo_view.py
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, 
    QComboBox, QPushButton, QTableWidget, QTableWidgetItem, 
    QHeaderView, QAbstractItemView, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QTextDocument
from PyQt6.QtPrintSupport import QPrintDialog, QPrinter
from controllers.emprestimo_controller import EmprestimoController


class EmprestimoView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
        self.carregar_dados()

    def _init_ui(self):
        layout_principal = QVBoxLayout(self)

        # Filtros e Ações
        box_filtro = QGroupBox("Consulta de Empréstimos")
        lay_filtro = QHBoxLayout()

        lay_filtro.addWidget(QLabel("Filtrar por Status:"))
        self.combo_status = QComboBox()
        self.combo_status.addItems(["Aberto", "Devolvido", "Todos"])
        self.combo_status.currentTextChanged.connect(self.carregar_dados)
        lay_filtro.addWidget(self.combo_status)

        btn_atualizar = QPushButton("Atualizar")
        btn_atualizar.clicked.connect(self.carregar_dados)
        lay_filtro.addWidget(btn_atualizar)

        # Botão para gerar e imprimir o Termo de Guarda
        btn_imprimir = QPushButton("🖨️ Imprimir Termo de Guarda")
        btn_imprimir.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold; padding: 6px;")
        btn_imprimir.clicked.connect(self.imprimir_termo_guarda)
        lay_filtro.addWidget(btn_imprimir)

        box_filtro.setLayout(lay_filtro)
        layout_principal.addWidget(box_filtro)

        # Tabela (5 Colunas)
        self.tabela = QTableWidget()
        self.tabela.setColumnCount(5)
        self.tabela.setHorizontalHeaderLabels([
            "Pessoa / Integrante", "Materiais Emprestados", 
            "Data Empréstimo", "Previsão Devolução", "Status"
        ])
        self.tabela.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tabela.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tabela.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        self.tabela.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)

        layout_principal.addWidget(self.tabela)

    def carregar_dados(self):
        status_filtro = self.combo_status.currentText()
        emprestimos = EmprestimoController.listar_emprestimos(status_filtro)

        self.tabela.setRowCount(0)
        for emp in emprestimos:
            pos = self.tabela.rowCount()
            self.tabela.insertRow(pos)

            # Armazena o ID e o dicionário completo do empréstimo no UserRole da primeira célula
            item_pessoa = QTableWidgetItem(str(emp.get("pessoa", "N/A")))
            item_pessoa.setData(Qt.ItemDataRole.UserRole, emp)

            self.tabela.setItem(pos, 0, item_pessoa)
            self.tabela.setItem(pos, 1, QTableWidgetItem(str(emp.get("itens", ""))))
            self.tabela.setItem(pos, 2, QTableWidgetItem(str(emp.get("data", ""))))
            self.tabela.setItem(pos, 3, QTableWidgetItem(str(emp.get("previsao", ""))))
            self.tabela.setItem(pos, 4, QTableWidgetItem(str(emp.get("status", ""))))

    def imprimir_termo_guarda(self):
        linha_selecionada = self.tabela.currentRow()
        if linha_selecionada < 0:
            QMessageBox.warning(self, "Aviso", "Selecione um empréstimo na tabela para gerar o Termo de Guarda!")
            return

        # Recupera os dados do empréstimo selecionado
        emp_dados = self.tabela.item(linha_selecionada, 0).data(Qt.ItemDataRole.UserRole)
        if not emp_dados:
            return

        # Template HTML do Termo de Guarda e Responsabilidade
        html_content = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; font-size: 12pt; margin: 30px; }}
                h2 {{ text-align: center; margin-bottom: 5px; }}
                h4 {{ text-align: center; color: #555; margin-top: 0px; margin-bottom: 25px; }}
                .info {{ margin-bottom: 15px; line-height: 1.5; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 15px; margin-bottom: 25px; }}
                th, td {{ border: 1px solid #000; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                .declaracao {{ text-align: justify; margin-top: 20px; line-height: 1.6; }}
                .assinaturas {{ margin-top: 60px; width: 100%; }}
                .linha-ass {{ border-top: 1px solid #000; width: 80%; margin: 0 auto; text-align: center; padding-top: 5px; }}
            </style>
        </head>
        <body>
            <h2>ERP HUGELMANNERPLATTLER</h2>
            <h4>TERMO DE GUARDA E RESPONSABILIDADE DE BENS</h4>

            <div class="info">
                <b>Código do Empréstimo:</b> #{emp_dados.get('id', 'N/A')}<br>
                <b>Responsável / Integrante:</b> {emp_dados.get('pessoa', 'N/A')}<br>
                <b>Data de Retirada:</b> {emp_dados.get('data', 'N/A')}<br>
                <b>Previsão de Devolução:</b> {emp_dados.get('previsao', 'N/A')}
            </div>

            <h3>Relação de Materiais/Patrimônios Emprestados</h3>
            <table>
                <thead>
                    <tr>
                        <th>Descrição dos Itens e Patrimônios</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>{emp_dados.get('itens', 'Nenhum item informado')}</td>
                    </tr>
                </tbody>
            </table>

            <div class="declaracao">
                Declaro ter recebido em perfeito estado de conservação e funcionamento os materiais acima discriminados, 
                assumindo integral responsabilidade pela sua guarda, conservação e devolução nas mesmas condições em que me foram entregues 
                até a data de previsão indicada. Em caso de dano, perda ou extravio, comprometo-me a ressarcir os custos de reparo ou reposição dos bens.
            </div>

            <br><br>
            <p style="text-align: right;">Data: ____ / ____ / ________</p>

            <table style="border: none; margin-top: 50px;">
                <tr style="border: none;">
                    <td style="border: none; text-align: center; width: 50%;">
                        ________________________________________<br>
                        <b>Assinatura do Responsável</b><br>
                        {emp_dados.get('pessoa', '')}
                    </td>
                    <td style="border: none; text-align: center; width: 50%;">
                        ________________________________________<br>
                        <b>Visto da Operação / Controle</b>
                    </td>
                </tr>
            </table>
        </body>
        </html>
        """

        # Prepara a caixa de diálogo de impressão nativa do sistema
        documento = QTextDocument()
        documento.setHtml(html_content)

        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        dialogo = QPrintDialog(printer, self)
        
        if dialogo.exec() == QPrintDialog.DialogCode.Accepted:
            documento.print(printer)