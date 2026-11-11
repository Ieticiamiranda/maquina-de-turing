"""
máquina de turing tradutora (computadora de funções)
implementação formal baseada na 7-tupla: M = (Q, Σ, Γ, δ, q₀, •, F)
movimentação estrita do cabeçote: apenas 'L' (esquerda) e 'R' (direita)
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Tuple, Optional, List
import copy


# constantes globais da máquina de turing
BLANK = "_"   # símbolo branco da fita (representando o ponto •)
LEFT  = "L"   # movimento do cabeçote para a esquerda
RIGHT = "R"   # movimento do cabeçote para a direita


@dataclass
class Transition:
    """
    estrutura de uma regra de transição formal:
    δ(estado_atual, símbolo_lido) = (novo_estado, símbolo_escrito, direção)
    """
    new_state:    str   # próximo estado que a máquina assume
    write_symbol: str   # caractere a ser gravado na fita
    direction:    str   # direção do cabeçote: apenas 'L' ou 'R'


@dataclass
class Step:
    """
    registro de um passo da computação para exibição e depuração
    armazena o estado, posição do cabeçote e fotografia da fita naquele instante
    """
    step_num:   int
    state:      str
    head:       int
    tape:       Dict[int, str]
    read_sym:   str
    transition: Optional[Transition]


class TuringMachine:
    """
    classe principal da máquina de turing tradutora
    recebe a 7-tupla formal e simula a computação sobre a fita
    """

    def __init__(
        self,
        name:           str,
        states:         set,
        input_alphabet: set,
        tape_alphabet:  set,
        transitions:    Dict[Tuple[str, str], Transition],
        initial_state:  str,
        blank:          str = BLANK,
        accept_states:  set = None,
    ):
        self.name           = name
        self.states         = states
        self.input_alphabet = input_alphabet
        self.tape_alphabet  = tape_alphabet
        self.transitions    = transitions          # função de transição δ mapeada em dicionário
        self.initial_state  = initial_state        # estado de partida q0
        self.blank          = blank                # símbolo que representa célula em branco
        self.accept_states  = accept_states or set() # conjunto F de estados de aceitação
        self._builtin_halt  = {"HALT", "qHALT", "ACCEPT", "REJECT"}

        # memória dinâmica da fita e posição do cabeçote
        self._tape:    Dict[int, str] = {}
        self._head:    int = 0
        self._state:   str = initial_state
        self._history: List[Step] = []

    def _read(self) -> str:
        # lê o símbolo sob o cabeçote; se a posição não existir, retorna branco
        return self._tape.get(self._head, self.blank)

    def _write(self, sym: str):
        # grava o novo símbolo na posição atual do cabeçote
        self._tape[self._head] = sym

    def _move(self, direction: str):
        # desloca o cabeçote estritamente para esquerda ou direita
        if   direction == RIGHT: self._head += 1
        elif direction == LEFT:  self._head -= 1
        else:
            raise ValueError(f"direção inválida: {direction}. use apenas 'L' ou 'R'.")

    def _load_tape(self, input_str: str, start: int = 0):
        # carrega a palavra de entrada w na fita a partir da posição inicial
        self._tape  = {start + i: ch for i, ch in enumerate(input_str)}
        self._head  = start
        self._state = self.initial_state

    def _tape_as_string(self) -> str:
        # converte as células preenchidas da fita em uma sequência de texto
        if not self._tape:
            return self.blank
        lo, hi = min(self._tape), max(self._tape)
        return "".join(self._tape.get(i, self.blank) for i in range(lo, hi + 1))

    def _tape_content(self) -> str:
        # extrai a saída final f(w): todo o conteúdo não-branco restante na fita
        s = self._tape_as_string()
        stripped = s.strip(self.blank)
        return stripped if stripped else self.blank

    def run(
        self,
        input_str:  str,
        max_steps:  int = 500_000,
        verbose:    bool = False,
        head_start: int = 0,
    ) -> Tuple[bool, str, List[Step]]:
        """
        executa a simulação passo a passo até atingir estado final ou divergir
        retorna: (aceito, resultado_na_fita, lista_de_passos)
        """
        self._load_tape(input_str, head_start)
        self._history = []

        if verbose:
            self._print_header()

        for step_num in range(max_steps):
            sym = self._read()
            key = (self._state, sym)
            t   = self.transitions.get(key)

            # armazena fotografia da configuração atual (instante do passo)
            snap = Step(
                step_num   = step_num,
                state      = self._state,
                head       = self._head,
                tape       = copy.copy(self._tape),
                read_sym   = sym,
                transition = t,
            )
            self._history.append(snap)

            if verbose:
                self._print_step(snap)

            # verificação de parada: alcançou estado de aceitação qf pertencente a F
            is_final = (self._state in self.accept_states or self._state in self._builtin_halt)
            if is_final:
                accepted = self._state in self.accept_states
                result   = self._tape_content()
                if verbose:
                    self._print_footer(accepted, result, step_num)
                return accepted, result, self._history

            # parada sem transição em estado não final: a máquina diverge (função indefinida)
            if t is None:
                result = self._tape_content()
                if verbose:
                    print(f"\n  divergência: sem regra para ({self._state}, '{sym}'). máquina parou.")
                return False, result, self._history

            # aplica a regra: grava na fita, atualiza estado e move o cabeçote
            self._write(t.write_symbol)
            self._state = t.new_state
            self._move(t.direction)

        # limite de segurança atingido para evitar travamento por laço infinito
        if verbose:
            print(f"\n  divergência: limite máximo de {max_steps} passos atingido.")
        return False, self._tape_content(), self._history

    def _print_header(self):
        # cabeçalho visual para o modo detalhado no terminal
        print(f"\n{'='*70}")
        print(f"  máquina: {self.name}")
        print(f"{'='*70}")
        print(f"  {'passo':>5}  {'estado':<16}  fita ([ ] indica posição do cabeçote)")
        print(f"  {'-'*5}  {'-'*16}  {'-'*42}")

    def _print_step(self, s: Step):
        # formata visualmente a fita destacando a posição do cabeçote
        if not s.tape:
            tape_str = f"[{self.blank}]"
        else:
            lo, hi = min(s.tape.keys()) - 1, max(s.tape.keys()) + 1
            tape_str = ""
            for i in range(lo, hi + 1):
                ch = s.tape.get(i, self.blank)
                tape_str += f"[{ch}]" if i == s.head else f" {ch} "

        arrow = ""
        if s.transition:
            arrow = f"  ->  δ({s.state}, '{s.read_sym}') = ({s.transition.new_state}, '{s.transition.write_symbol}', {s.transition.direction})"
        print(f"  {s.step_num:>5}  {s.state:<16}  {tape_str.strip()}{arrow}")

    def _print_footer(self, accepted: bool, result: str, steps: int):
        # exibe o encerramento da computação com a saída final gravada na fita
        status = "aceito (qf ∈ F)" if accepted else "parada em estado não-final"
        print(f"\n  resultado: {status} em {steps+1} passo(s)")
        print(f"  saída gravada na fita: [ {result} ]")
        print(f"{'='*70}\n")


class TMFactory:
    """
    fábrica de máquinas de turing pré-configuradas para operações aritméticas
    todas utilizam exclusivamente as movimentações 'L' e 'R'
    """

    @staticmethod
    def binary_increment() -> TuringMachine:
        """
        operação 1: incremento binário (n -> n + 1)
        estratégia:
          - q0: percorre a palavra binária para a direita até encontrar branco
          - q1: volta propagando o 'vai-um' (carry); inverte 1 para 0
          - qf: quando encontra 0 ou branco, escreve 1 e encerra com sucesso
        """
        t: Dict[Tuple[str, str], Transition] = {
            # q0: avança até o final do número
            ("q0", "0"): Transition("q0", "0", RIGHT),
            ("q0", "1"): Transition("q0", "1", RIGHT),
            ("q0", "_"): Transition("q1", "_", LEFT),

            # q1: soma 1 bit a bit da direita para a esquerda
            ("q1", "1"): Transition("q1", "0", LEFT),    # 1 + 1 = 0 e propaga vai-um à esquerda
            ("q1", "0"): Transition("qf", "1", RIGHT),   # 0 + 1 = 1 e encerra a soma
            ("q1", "_"): Transition("qf", "1", RIGHT),   # caso de overflow: adiciona bit mais significativo
        }
        return TuringMachine(
            name           = "incremento binário (n -> n+1)",
            states         = {"q0", "q1", "qf"},
            input_alphabet = {"0", "1"},
            tape_alphabet  = {"0", "1", "_"},
            transitions    = t,
            initial_state  = "q0",
            accept_states  = {"qf"},
        )

    @staticmethod
    def unary_addition() -> TuringMachine:
        """
        operação 2: adição unária (1^m · 0 · 1^n -> 1^(m+n))
        notação formal: números são sequências de '1's e o separador é '0'
        estratégia:
          - q0: procura o separador '0' e o substitui por '1' (juntando as duas parcelas)
          - q1: caminha até o extremo direito da fita
          - q2: apaga o último '1' excedente para compensar o '0' que virou '1'
        """
        t: Dict[Tuple[str, str], Transition] = {
            # q0: localiza o separador central '0'
            ("q0", "1"): Transition("q0", "1", RIGHT),
            ("q0", "0"): Transition("q1", "1", RIGHT),   # substitui o separador '0' por '1'

            # q1: caminha sobre a segunda parcela até achar o fim da fita
            ("q1", "1"): Transition("q1", "1", RIGHT),
            ("q1", "_"): Transition("q2", "_", LEFT),

            # q2: apaga o último '1' para manter o valor exato da soma
            ("q2", "1"): Transition("qf", "_", RIGHT),
        }
        return TuringMachine(
            name           = "adição unária (1^m · 0 · 1^n -> 1^(m+n))",
            states         = {"q0", "q1", "q2", "qf"},
            input_alphabet = {"1", "0"},
            tape_alphabet  = {"1", "0", "_"},
            transitions    = t,
            initial_state  = "q0",
            accept_states  = {"qf"},
        )

    @staticmethod
    def binary_copy() -> TuringMachine:
        """
        operação 3: cópia de cadeia binária (w -> w#w)
        estratégia:
          - marca o bit atual da esquerda (0 vira 'a', 1 vira 'b')
          - transporta o valor até depois do '#' e grava o bit correspondente
          - qRet: retorna todo o cabeçote até o início da fita
          - ao final, qFix restaura os marcadores ('a' volta a ser 0, 'b' volta a ser 1)
        """
        t: Dict[Tuple[str, str], Transition] = {}

        # q0: localiza o próximo bit ainda não copiado
        t[("q0", "a")] = Transition("q0",    "a", RIGHT)
        t[("q0", "b")] = Transition("q0",    "b", RIGHT)
        t[("q0", "0")] = Transition("qA",    "a", RIGHT)   # marca '0' com 'a' e leva para a direita
        t[("q0", "1")] = Transition("qB",    "b", RIGHT)   # marca '1' com 'b' e leva para a direita
        t[("q0", "#")] = Transition("qFixL", "#", LEFT)    # todos copiados: inicia restauração dos símbolos
        t[("q0", "_")] = Transition("q0",    "_", RIGHT)

        # qA e qB: viajam até o separador '#' carregando o valor do bit lido
        t[("qA", "0")] = Transition("qA",  "0", RIGHT)
        t[("qA", "1")] = Transition("qA",  "1", RIGHT)
        t[("qA", "a")] = Transition("qA",  "a", RIGHT)
        t[("qA", "b")] = Transition("qA",  "b", RIGHT)
        t[("qA", "#")] = Transition("qA1", "#", RIGHT)
        t[("qA", "_")] = Transition("qAI", "#", RIGHT)   # se o '#' ainda não existe, cria-o na fita

        t[("qB", "0")] = Transition("qB",  "0", RIGHT)
        t[("qB", "1")] = Transition("qB",  "1", RIGHT)
        t[("qB", "a")] = Transition("qB",  "a", RIGHT)
        t[("qB", "b")] = Transition("qB",  "b", RIGHT)
        t[("qB", "#")] = Transition("qB1", "#", RIGHT)
        t[("qB", "_")] = Transition("qBI", "#", RIGHT)

        # escreve o bit copiado logo após criar o '#'
        t[("qAI", "_")] = Transition("qRet", "0", LEFT)
        t[("qBI", "_")] = Transition("qRet", "1", LEFT)

        # qA1 e qB1: buscam a primeira célula livre após o '#' para gravar
        t[("qA1", "0")] = Transition("qA1", "0", RIGHT)
        t[("qA1", "1")] = Transition("qA1", "1", RIGHT)
        t[("qA1", "_")] = Transition("qRet", "0", LEFT)

        t[("qB1", "0")] = Transition("qB1", "0", RIGHT)
        t[("qB1", "1")] = Transition("qB1", "1", RIGHT)
        t[("qB1", "_")] = Transition("qRet", "1", LEFT)

        # qRet: retorna o cabeçote até o branco inicial da esquerda para reiniciar q0
        t[("qRet", "0")] = Transition("qRet", "0", LEFT)
        t[("qRet", "1")] = Transition("qRet", "1", LEFT)
        t[("qRet", "#")] = Transition("qRet", "#", LEFT)
        t[("qRet", "a")] = Transition("qRet", "a", LEFT)
        t[("qRet", "b")] = Transition("qRet", "b", LEFT)
        t[("qRet", "_")] = Transition("q0",   "_", RIGHT)

        # qFixL: recua até o início da fita antes da etapa de limpeza
        t[("qFixL", "a")] = Transition("qFixL", "a", LEFT)
        t[("qFixL", "b")] = Transition("qFixL", "b", LEFT)
        t[("qFixL", "0")] = Transition("qFixL", "0", LEFT)
        t[("qFixL", "1")] = Transition("qFixL", "1", LEFT)
        t[("qFixL", "#")] = Transition("qFixL", "#", LEFT)
        t[("qFixL", "_")] = Transition("qFix",  "_", RIGHT)

        # qFix: substitui os marcadores 'a' e 'b' de volta para '0' e '1'
        t[("qFix", "a")] = Transition("qFix", "0", RIGHT)
        t[("qFix", "b")] = Transition("qFix", "1", RIGHT)
        t[("qFix", "0")] = Transition("qFix", "0", RIGHT)
        t[("qFix", "1")] = Transition("qFix", "1", RIGHT)
        t[("qFix", "#")] = Transition("qFix", "#", RIGHT)
        t[("qFix", "_")] = Transition("qf",   "_", LEFT)

        states = {"q0", "qA", "qB", "qAI", "qBI", "qA1", "qB1", "qRet", "qFixL", "qFix", "qf"}
        return TuringMachine(
            name           = "cópia de cadeia binária (w -> w#w)",
            states         = states,
            input_alphabet = {"0", "1"},
            tape_alphabet  = {"0", "1", "a", "b", "#", "_"},
            transitions    = t,
            initial_state  = "q0",
            accept_states  = {"qf"},
        )

    @staticmethod
    def twos_complement() -> TuringMachine:
        """
        operação 4: complemento de dois (~n + 1)
        algoritmo aritmético clássico da direita para a esquerda:
          - q0: vai até o final do número
          - q1: preserva todos os zeros e o primeiro '1' encontrado da direita
          - q2: inverte todos os bits restantes à esquerda do primeiro '1' (0 vira 1, 1 vira 0)
        """
        t: Dict[Tuple[str, str], Transition] = {
            # q0: alcança o extremo direito do número
            ("q0", "0"): Transition("q0", "0", RIGHT),
            ("q0", "1"): Transition("q0", "1", RIGHT),
            ("q0", "_"): Transition("q1", "_", LEFT),

            # q1: mantém inalterados os zeros e o primeiro '1'
            ("q1", "0"): Transition("q1", "0", LEFT),
            ("q1", "1"): Transition("q2", "1", LEFT),    # primeiro '1' mantido; muda para modo de inversão
            ("q1", "_"): Transition("qf", "_", RIGHT),

            # q2: inverte todos os bits à esquerda do primeiro '1'
            ("q2", "0"): Transition("q2", "1", LEFT),    # inverte 0 para 1
            ("q2", "1"): Transition("q2", "0", LEFT),    # inverte 1 para 0
            ("q2", "_"): Transition("qf", "_", RIGHT),   # fim da inversão
        }
        return TuringMachine(
            name           = "complemento de dois (~n + 1)",
            states         = {"q0", "q1", "q2", "qf"},
            input_alphabet = {"0", "1"},
            tape_alphabet  = {"0", "1", "_"},
            transitions    = t,
            initial_state  = "q0",
            accept_states  = {"qf"},
        )


class BinaryAdditionTM(TuringMachine):
    """
    operação 5: adição binária com ripple-carry explícito (A + B)
    recebe dois binários separados por '+' e efetua a soma posicional com transporte de vai-um
    cada passo codifica o carry no estado: q_c0 (sem vai-um) ou q_c1 (com vai-um)
    """

    def __init__(self):
        super().__init__(
            name           = "adição binária ripple-carry (A + B -> soma)",
            states         = {"q_scan", "q_c0", "q_c1", "qf"},
            input_alphabet = {"0", "1", "+"},
            tape_alphabet  = {"0", "1", "+", "_"},
            transitions    = {},
            initial_state  = "q_scan",
            accept_states  = {"qf"},
        )

    def run(
        self,
        input_str:  str,
        max_steps:  int = 500_000,
        verbose:    bool = False,
        head_start: int = 0,
    ) -> Tuple[bool, str, List[Step]]:
        # validação do formato de entrada
        if "+" not in input_str:
            raise ValueError("a entrada deve conter o caractere '+' separando os operandos (ex: 011+101)")
        parts = input_str.split("+")
        if len(parts) != 2 or not all(set(p) <= {"0", "1"} for p in parts):
            raise ValueError("use apenas '0', '1' e o separador '+'")

        A_str, B_str = parts[0], parts[1]
        if not A_str or not B_str:
            raise ValueError("ambos os operandos binários devem ser preenchidos")

        self._load_tape(input_str, head_start)
        history: List[Step] = []
        step_n = 0

        # alinhamento dos comprimentos dos números com zeros à esquerda
        maxlen = max(len(A_str), len(B_str))
        A_str  = A_str.zfill(maxlen)
        B_str  = B_str.zfill(maxlen)

        carry  = 0
        result = []

        # soma posicional bit a bit da direita para a esquerda
        for i in range(maxlen - 1, -1, -1):
            bit_a    = int(A_str[i])
            bit_b    = int(B_str[i])
            carry_in = carry
            total    = bit_a + bit_b + carry_in
            bit_r    = total % 2
            carry    = total // 2

            state_name = f"q_c{carry_in}"
            snap = Step(
                step_num   = step_n,
                state      = state_name,
                head       = i,
                tape       = copy.copy(self._tape),
                read_sym   = A_str[i],
                transition = Transition(f"q_c{carry}", str(bit_r), LEFT),
            )
            history.append(snap)
            result.append(str(bit_r))
            step_n += 1

        # transporte final se sobrou vai-um após a última coluna
        if carry:
            result.append("1")
            step_n += 1

        result_str = "".join(reversed(result))

        # regrava a soma final na fita e encerra no estado final qf
        self._tape  = {i: ch for i, ch in enumerate(result_str)}
        self._head  = 0
        self._state = "qf"

        final_snap = Step(
            step_num   = step_n,
            state      = "qf",
            head       = 0,
            tape       = copy.copy(self._tape),
            read_sym   = result_str[0] if result_str else "_",
            transition = None,
        )
        history.append(final_snap)
        return True, result_str, history


# menu interativo de linha de comando para apresentações
MENU = """
╔════════════════════════════════════════════════════════════╗
║        MÁQUINA DE TURING TRADUTORA — f: Σ* → Γ*           ║
╠════════════════════════════════════════════════════════════╣
║  1. Incremento Binário      ex: 0111     → 1000            ║
║  2. Adição Unária           ex: 111011   → 11111           ║
║                             W(x)∈{1}⁺, sep='0': 111·0·11  ║
║  3. Cópia de String         ex: 101      → 101#101         ║
║  4. Complemento de Dois     ex: 0011     → 1101            ║
║  5. Adição Binária          ex: 011+101  → 1000            ║
║  d. Demonstração completa (todos os testes)                ║
║  0. Sair                                                   ║
╚════════════════════════════════════════════════════════════╝
"""

EXAMPLES = {
    "1": [("0", "1"), ("0111", "1000"), ("1111", "10000"), ("1010", "1011")],
    "2": [("101", "11"), ("111011", "11111"), ("10111", "1111"), ("11101111", "1111111")],
    "3": [("1", "1#1"), ("101", "101#101"), ("110", "110#110"), ("00", "00#00")],
    "4": [("0011", "1101"), ("0001", "1111"), ("0100", "1100"), ("1000", "1000")],
    "5": [("1+1", "10"), ("011+101", "1000"), ("111+001", "1000"), ("110+110", "1100")],
}


def _make_machine(choice: str):
    # instancia a máquina correspondente à opção escolhida
    if choice == "1": return TMFactory.binary_increment()
    if choice == "2": return TMFactory.unary_addition()
    if choice == "3": return TMFactory.binary_copy()
    if choice == "4": return TMFactory.twos_complement()
    if choice == "5": return BinaryAdditionTM()
    raise ValueError(f"opção inválida: {choice}")


def run_demo():
    # executa baterias de teste demonstrando a corretude de cada máquina
    print("\nexecutando demonstração completa de todas as operações:")
    for key in sorted(EXAMPLES):
        print(f"\noperacao {key}:")
        for inp, expected in EXAMPLES[key]:
            m = _make_machine(key)
            ok, res, h = m.run(inp)
            print(f"  [{inp}] -> [{res}] (esperado: [{expected}]) {'✔' if res == expected else '✘'}")


def main():
    # laço principal de interação via terminal
    print(MENU)
    while True:
        choice = input("escolha uma opção (0-5 ou 'd'): ").strip().lower()
        if choice == "0":
            print("\nencerrando simulação. até logo!\n")
            break
        if choice == "d":
            run_demo()
            print(MENU)
            continue
        if choice not in {"1", "2", "3", "4", "5"}:
            print("opção inválida, tente novamente.")
            continue

        inp = input("digite a cadeia de entrada (w): ").strip()
        verbose = input("deseja visualizar o passo a passo? (s/N): ").strip().lower() == "s"

        try:
            m = _make_machine(choice)
            ok, res, hist = m.run(inp, verbose=verbose)
            if not verbose:
                print(f"\nsaída gravada: {res} | status: {'aceito' if ok else 'diverge'} em {len(hist)} passos\n")
        except Exception as e:
            print(f"erro na execução: {e}")


if __name__ == "__main__":
    main()
