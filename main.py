# sistema_bancario.py

from abc import ABC, abstractmethod
from datetime import datetime
import textwrap

# ========================= CLASSES BASE =========================

class Cliente:
    def __init__(self, endereco):
        self.endereco = endereco
        self.contas = []

    def realizar_transacao(self, conta, transacao):
        transacao.registrar(conta)

    def adicionar_conta(self, conta):
        self.contas.append(conta)


class PessoaFisica(Cliente):
    def __init__(self, nome, cpf, data_nascimento, endereco):
        super().__init__(endereco)
        self.nome = nome
        self.cpf = cpf
        self.data_nascimento = data_nascimento


class Conta:
    def __init__(self, numero, cliente):
        self.numero = numero
        self.agencia = "0001"
        self.cliente = cliente
        self.saldo = 0.0
        self.historico = Historico()

    def sacar(self, valor):
        if valor <= 0:
            print("@@@ Valor inválido. @@@")
            return False

        if valor > self.saldo:
            print("@@@ Saldo insuficiente. @@@")
            return False

        self.saldo -= valor
        print(f"=== Saque de R$ {valor:.2f} realizado com sucesso! ===")
        return True

    def depositar(self, valor):
        if valor <= 0:
            print("@@@ Valor inválido. @@@")
            return False

        self.saldo += valor
        print(f"=== Depósito de R$ {valor:.2f} realizado com sucesso! ===")
        return True


class ContaCorrente(Conta):
    def __init__(self, numero, cliente, limite=500, limite_saques=3):
        super().__init__(numero, cliente)
        self.limite = limite
        self.limite_saques = limite_saques
        self.saques_realizados = 0

    def sacar(self, valor):
        if self.saques_realizados >= self.limite_saques:
            print("@@@ Limite de saques diários atingido. @@@")
            return False

        if valor > self.limite:
            print("@@@ Valor excede o limite permitido por saque. @@@")
            return False

        if super().sacar(valor):
            self.saques_realizados += 1
            return True

        return False


class Historico:
    def __init__(self):
        self.transacoes = []

    def adicionar_transacao(self, transacao):
        self.transacoes.append({
            "tipo": transacao.__class__.__name__,
            "valor": transacao.valor,
            "data": datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        })


# ===================== CLASSES DE TRANSAÇÃO =====================

class Transacao(ABC):
    @abstractmethod
    def registrar(self, conta):
        pass


class Deposito(Transacao):
    def __init__(self, valor):
        self.valor = valor

    def registrar(self, conta):
        sucesso = conta.depositar(self.valor)
        if sucesso:
            conta.historico.adicionar_transacao(self)


class Saque(Transacao):
    def __init__(self, valor):
        self.valor = valor

    def registrar(self, conta):
        sucesso = conta.sacar(self.valor)
        if sucesso:
            conta.historico.adicionar_transacao(self)


# ======================== FUNÇÃO MENU ========================

def menu():
    opcoes = """
    [d] Depositar
    [s] Sacar
    [e] Extrato
    [nc] Nova conta
    [lc] Listar contas
    [nu] Novo usuário
    [q] Sair
    => """
    return input(textwrap.dedent(opcoes))


# ======================= FUNÇÕES AUXILIARES =======================

def criar_usuario(usuarios):
    cpf = input("CPF: ")
    if any(u.cpf == cpf for u in usuarios):
        print("@@@ CPF já cadastrado. @@@")
        return

    nome = input("Nome: ")
    data_nascimento = input("Data de nascimento (dd-mm-aaaa): ")
    endereco = input("Endereço (logradouro, nro - bairro - cidade/UF): ")

    usuarios.append(PessoaFisica(nome, cpf, data_nascimento, endereco))
    print("=== Usuário criado com sucesso! ===")


def criar_conta(contas, usuarios):
    cpf = input("Informe o CPF do cliente: ")
    cliente = next((u for u in usuarios if u.cpf == cpf), None)

    if cliente:
        numero = len(contas) + 1
        conta = ContaCorrente(numero, cliente)
        contas.append(conta)
        cliente.adicionar_conta(conta)
        print("=== Conta criada com sucesso! ===")
    else:
        print("@@@ Cliente não encontrado. @@@")


def listar_contas(contas):
    for conta in contas:
        print("=" * 40)
        print(f"Agência: {conta.agencia}\nConta: {conta.numero}\nTitular: {conta.cliente.nome}")


def exibir_extrato(conta):
    print("\n================ EXTRATO ================")
    for t in conta.historico.transacoes:
        print(f"{t['tipo']}: R$ {t['valor']:.2f} em {t['data']}")
    print(f"\nSaldo: R$ {conta.saldo:.2f}")
    print("=" * 40)


# ======================== LOOP PRINCIPAL ========================

def main():
    usuarios = []
    contas = []

    while True:
        opcao = menu()

        if opcao == "d":
            cpf = input("Informe o CPF do titular: ")
            cliente = next((u for u in usuarios if u.cpf == cpf), None)

            if not cliente or not cliente.contas:
                print("@@@ Cliente ou conta inexistente. @@@")
                continue

            valor = float(input("Valor do depósito: "))
            transacao = Deposito(valor)
            cliente.realizar_transacao(cliente.contas[0], transacao)

        elif opcao == "s":
            cpf = input("Informe o CPF do titular: ")
            cliente = next((u for u in usuarios if u.cpf == cpf), None)

            if not cliente or not cliente.contas:
                print("@@@ Cliente ou conta inexistente. @@@")
                continue

            valor = float(input("Valor do saque: "))
            transacao = Saque(valor)
            cliente.realizar_transacao(cliente.contas[0], transacao)

        elif opcao == "e":
            cpf = input("Informe o CPF do titular: ")
            cliente = next((u for u in usuarios if u.cpf == cpf), None)

            if cliente and cliente.contas:
                exibir_extrato(cliente.contas[0])
            else:
                print("@@@ Cliente ou conta inexistente. @@@")

        elif opcao == "nu":
            criar_usuario(usuarios)

        elif opcao == "nc":
            criar_conta(contas, usuarios)

        elif opcao == "lc":
            listar_contas(contas)

        elif opcao == "q":
            break

        else:
            print("@@@ Opção inválida. @@@")


if __name__ == "__main__":
    main()
