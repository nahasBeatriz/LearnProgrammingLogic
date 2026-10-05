# CodeBot

Ambiente interativo de ensino de lógica de programação com programação visual por blocos, desenvolvido com Python, OpenGL e GLFW.

## Sobre o projeto

O CodeBot é um jogo educacional em que o jogador conduz um robô virtual por labirintos usando blocos de comandos, aprendendo na prática os fundamentos do pensamento computacional: sequências, condicionais e laços de repetição.

O projeto foi desenvolvido como trabalho final da disciplina de **Computação Gráfica** do Bacharelado em Ciência da Computação.

## Funcionalidades

- **6 fases progressivas** com dificuldade crescente
- **Programação por blocos** com paleta interativa clicável
- **Execução animada** do robô na grade
- **Estruturas de controle** suportadas:
  - `FRENTE` — anda 1 passo na direção atual
  - `GIRAR →` / `GIRAR ←` — gira o robô 90°
  - `SE PAREDE { } SENÃO { } FIM` — condicional baseada em obstáculo à frente
  - `REPITA(3) { } FIM` — repete o bloco 3 vezes
- **Feedback visual** em tempo real (erro, sucesso, destaque do comando em execução)
- **Limite de blocos por fase** para incentivar soluções concisas
- **Scroll** no painel do programa para programas mais longos
- Botão de remoção individual de blocos (`x`)

## Requisitos

- Python 3.8+
- [GLFW](https://pypi.org/project/glfw/)
- [PyOpenGL](https://pypi.org/project/PyOpenGL/)

## Instalação

```bash
# Crie e ative o ambiente virtual
python -m venv venv

# Linux
source venv/bin/activate

# Windows
venv\Scripts\activate

# Instale as dependências
pip install glfw PyOpenGL PyOpenGL_accelerate
```

> **Linux:** pode ser necessário instalar dependências do sistema:
> ```bash
> sudo apt install freeglut3-dev
> ```

## Como executar

```bash
# Ative o ambiente virtual (se ainda não estiver ativo)
source venv/bin/activate  # Linux
# ou
venv\Scripts\activate     # Windows

python codebot.py
```

## Como jogar

1. Analise o mapa: veja onde o robô está, onde fica a estrela e quais células são paredes.
2. Clique nos blocos da **paleta esquerda** para montar seu programa no **painel direito**.
3. Clique em **RODAR** para executar.
4. Se o robô bater na parede ou não chegar à estrela, clique em **LIMPAR** e tente novamente.
5. Ao resolver a fase, o botão **PRÓXIMA** fica disponível.

### Estrutura de um programa com condicional

```
SE PAREDE
  DIREITA
FIM
FRENTE
```

### Estrutura de um programa com repetição

```
REPITA(3)
  FRENTE
FIM
```

## Estrutura das fases

| Fase | Título              | Conceito principal          |
|------|---------------------|-----------------------------|
| 1    | Sequência           | Comandos em ordem           |
| 2    | Direções            | Girar antes de andar        |
| 3    | Se... Então         | Condicional com parede      |
| 4    | Labirinto           | Sequência com planejamento  |
| 5    | Desvio Esperto      | Condicional para desviar    |
| 6    | Desafio Final       | Tudo junto                  |

## Arquitetura técnica

- Renderização 2D via **OpenGL** (quads, triângulos, primitivas customizadas)
- Janela gerenciada pelo **GLFW**
- Texto renderizado via **GLUT bitmap fonts**
- Lógica de execução por pilha (`exec_stack`) com expansão de `REPITA` e resolução de `SE_PAREDE` em pré-processamento
- Animação suave do robô via interpolação linear por frame (`animacao_t`)
