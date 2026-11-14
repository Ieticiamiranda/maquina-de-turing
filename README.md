# ── .✦ Implementação de Máquina de Turing (Computadora de Funções)

*Este repositório reúne implementações desenvolvidas em **Python**, como parte da disciplina de **Linguagens Formais e Teoria dos Autômatos**, lecionada pelo Prof. Isaac de Lima Oliveira FIlho. O objetivo é demonstrar MT como tradutora, com operações aritméticas e manipulações de cadeias por meio de transformações posicionais sobre a fita.*

## ᯓ Fundamentação Teórica

A máquina é formalmente definida pela 7-tupla canônica:
$$M = (Q, \Sigma, \Gamma, \delta, q_0, B, F)$$

* **$Q$:** Conjunto finito de estados.
* **$\Sigma$:** Alfabeto de entrada ($B \notin \Sigma$).
* **$\Gamma$:** Alfabeto da fita ($\Sigma \subset \Gamma$ e $B \in \Gamma$).
* **$\delta$:** Função parcial de transição: $\delta: Q \times \Gamma \to Q \times \Gamma \times \{L, R\}$.
* **$q_0$:** Estado inicial ($q_0 \in Q$).
* **$B$:** Símbolo branco (representado por `_`).
* **$F$:** Conjunto de estados de aceitação ($F \subseteq Q$).

## ᯓ Funcionalidades e Operações Implementadas:

- **Incremento Binário ($n \to n + 1$):** Adiciona 1 a uma palavra binária tratando a propagação de transporte (*carry*) e expansão da fita em caso de *overflow*.
- **Adição Unária ($1^m \cdot 0 \cdot 1^n \to 1^{m+n}$):** Soma dois números representados em notação unária separados por `0`.
- **Duplicação de Cadeia Binária ($w \to w \# w$):** Duplica uma palavra binária arbitrária através de marcadores no alfabeto de fita auxiliar $\Gamma \setminus \Sigma = \{a, b, \#, \_\}$.
- **Complemento de Dois ($\sim n + 1$):** Inverte o valor binário em passada única retroativa preservando zeros e o primeiro bit `1`.
- **Adição Binária ($A + B \to \text{Soma}$):** Efetua a soma posicional de dois números binários com memória de transporte (*ripple-carry*) codificada diretamente nos estados.
- **Integração com JFLAP:** Exportador nativo que converte as máquinas definidas no código para arquivos `.jff` (XML) com posicionamento circular trigonométrico dos estados.
- **Interface Gráfica Interativa (Web):** Execução visual da fita e do cabeçote no navegador através de servidor HTTP local nativo.

---

## ᯓ Dependências e Pré-requisitos:

O projeto foi construído utilizando **exclusivamente a biblioteca padrão do Python**, sem necessidade de instalar pacotes via `pip`.

* **Obrigatório:**
  * **Python 3.8** ou superior instalado no sistema.
* **Opcionais:**
  * **Navegador Web** moderno (Google Chrome, Firefox, Edge...) para abrir a interface gráfica.
  * **Java JRE** e **[JFLAP](https://www.jflap.org/)** caso queira abrir e simular visualmente os arquivos `.jff` gerados na pasta `jflap/`.

---

## ᯓ  Como Executar:

1. Clone o repositório e navegue até a pasta do projeto:

```bash
gitclone https://github.com/Ieticiamiranda/maquina-de-turing.git
cd maquina-de-turing/turing
```

---

- ### No Linux / macOS ˚. ᵎᵎ

#### 1. Simulação Interativa via Terminal (CLI)
Executa o menu interativo com modo detalhado (passo a passo da fita) e bateria de testes automatizados:
```bash
python3 turing.py
```
> **Dica:** No menu, digite `d` para rodar a demonstração automática de todos os testes de uma só vez.

#### 2. Gerar Arquivo para o JFLAP (`.jff`)
Gera o arquivo XML compatível com o software JFLAP dentro da pasta `jflap/`:
```bash
python3 jflap.py
```

#### 3. Iniciar a Interface Gráfica no Navegador
Inicia um servidor HTTP local nativo (porta 8085) e abre automaticamente a interface visual:
```bash
python3 web_turing.py
```

---

- ### No Windows ˚. ᵎᵎ

Abra o **Prompt de Comando (CMD)** ou o **PowerShell** na pasta do projeto:

#### 1. Simulação Interativa via Terminal (CLI)
```powershell
python turing.py
```
*(ou `py turing.py` dependendo de como o Python foi instalado).*

#### 2. Gerar Arquivo para o JFLAP (`.jff`)
```powershell
python jflap.py
```

#### 3. Iniciar a Interface Gráfica no Navegador
```powershell
python web_turing.py
```
---

*Para dúvidas ou sugestões, entre em contato: **leticiamiranda.tech@gmail.com***  

***Obrigado por visitar este repositório! ⋆˙⟡***
