import glfw
from OpenGL.GL import *
from OpenGL.GLUT import *
import math, sys

W, H = 1100, 700
COR = {
    "bg": (0.10, 0.12, 0.20),
    "painel_esq": (0.14, 0.17, 0.28),
    "painel_dir": (0.11, 0.14, 0.22),
    "grid": (0.20, 0.24, 0.38),
    "grid_borda": (0.28, 0.34, 0.52),
    "FRENTE": (0.20, 0.72, 0.40),
    "DIREITA": (0.20, 0.55, 0.90),
    "ESQUERDA": (0.85, 0.60, 0.10),
    "SE_PAREDE": (0.80, 0.30, 0.70),
    "SENAO": (0.65, 0.22, 0.60),
    "REPITA": (0.85, 0.35, 0.20),
    "FIM": (0.45, 0.48, 0.58),
    "btn_run": (0.15, 0.75, 0.35),
    "btn_clear": (0.75, 0.25, 0.25),
    "btn_step": (0.20, 0.55, 0.80),
    "sucesso": (0.15, 0.80, 0.40),
    "erro": (0.85, 0.25, 0.25),
    "destaque": (1.00, 0.85, 0.20),
    "branco": (1.00, 1.00, 0.95),
    "texto_esc": (0.65, 0.70, 0.85),
    "robo": (0.30, 0.75, 0.95),
    "objetivo": (1.00, 0.80, 0.10),
    "parede": (0.40, 0.45, 0.60),
    "chao": (0.22, 0.26, 0.40),
}

FASES = [
    {
        "titulo": "Fase 1 - Sequencia",
        "descricao": ["Coloque os comandos na ordem certa", "para levar o robo ate a estrela!"],
        "conceito": "SEQUENCIA: os comandos rodam um apos o outro.",
        "dica": "Dica: FRENTE anda 1 passo na direcao que o robo esta olhando!",
        "grade": 5, "robo": (0,2), "dir": "D", "objetivo": (4,2),
        "paredes": [], "blocos": ["FRENTE","DIREITA","ESQUERDA"], "max_blocos": 6,
    },
    {
        "titulo": "Fase 2 - Direcoes",
        "descricao": ["O caminho tem curvas!", "Vire o robo antes de andar."],
        "conceito": "SEQUENCIA: gire e ande na ordem certa.",
        "dica": "Dica: DIREITA gira o robo 90 graus para a direita dele!",
        "grade": 5, "robo": (0,4), "dir": "D", "objetivo": (4,0),
        "paredes": [], "blocos": ["FRENTE","DIREITA","ESQUERDA"], "max_blocos": 10,
    },
    {
        "titulo": "Fase 3 - Se... Entao",
        "descricao": ["Ha paredes no caminho!", "Use SE PAREDE para desviar."],
        "conceito": "CONDICIONAL: SE algo for verdade, faca outra coisa.",
        "dica": "Dica: SE PAREDE { ... } SENAO { ... } FIM",
        "grade": 5, "robo": (0,2), "dir": "D", "objetivo": (4,2),
        "paredes": [(2,2),(2,1),(2,3)],
        "blocos": ["FRENTE","DIREITA","ESQUERDA","SE_PAREDE","SENAO","FIM"],
        "max_blocos": 15,
    },
    {
        "titulo": "Fase 4 - Labirinto",
        "descricao": ["Desvie das paredes!", "Encontre o caminho ate a estrela."],
        "conceito": "SEQUENCIA: planeje cada passo com cuidado.",
        "dica": "Dica: observe bem o mapa antes de montar o programa!",
        "grade": 5, "robo": (0,0), "dir": "D", "objetivo": (4,4),
        "paredes": [(2,0),(2,1),(1,3),(1,4)],
        "blocos": ["FRENTE","DIREITA","ESQUERDA"],
        "max_blocos": 20,
    },
    {
        "titulo": "Fase 5 - Desvio Esperto",
        "descricao": ["Ha uma parede bloqueando!", "Use SE PAREDE para decidir o que fazer."],
        "conceito": "CONDICIONAL: o robo decide o caminho sozinho!",
        "dica": "Dica: SE PAREDE vire, SENAO siga em frente!",
        "grade": 5, "robo": (0,2), "dir": "D", "objetivo": (4,2),
        "paredes": [(2,2),(2,3)],
        "blocos": ["FRENTE","DIREITA","ESQUERDA","SE_PAREDE","SENAO","FIM"],
        "max_blocos": 15,
    },
    {
        "titulo": "Fase 6 - Desafio Final",
        "descricao": ["Use tudo que aprendeu!", "Paredes + loops + condicionais."],
        "conceito": "TUDO JUNTO: sequencia, loop e condicional!",
        "dica": "Dica: planeje o caminho antes de montar!",
        "grade": 6, "robo": (0,0), "dir": "D", "objetivo": (5,5),
        "paredes": [(2,0),(2,1),(2,2),(4,3),(4,4)],
        "blocos": ["FRENTE","DIREITA","ESQUERDA","SE_PAREDE","SENAO","REPITA","FIM"],
        "max_blocos": 18,
    },
]

# Estado global
fase_atual = 0
programa = []
executando = False
passo_atual = 0
robo_pos = (0, 0)
robo_dir = "D"
msg = ""
msg_cor = "branco"
msg_timer = 0.0
sucesso = False
animacao_t = 1.0
estrela_t = 0.0
exec_stack = []
scroll_offset = 0  # Scroll para o programa

# Layout
PAL_X1, PAL_X2 = 0, 340
GRADE_X1 = 350
GRADE_X2 = 740
PROG_X1, PROG_X2 = 750, 1100

# Área de topo (título + descrição + conceito + dica + msg)
# Reservamos 160 px no topo da região central
TOPO_H = 160
TOPO_Y = H - TOPO_H        # y onde começa o topo (em coords OpenGL: baixo→cima)
GRADE_Y1 = 60
# A grade ocupa de GRADE_Y1 até TOPO_Y
# Topo ocupa de TOPO_Y até H

BTN_H = 46
BTN_W = 140
BTN_RUN = (10,  10, BTN_W, BTN_H)
BTN_CLEAR = (10,  62, BTN_W, BTN_H)
BTN_NEXT = (160, 62, BTN_W, BTN_H)

# Primitivas 2D 
def set_cor(c, alpha=1.0):
    r, g, b = COR[c] if isinstance(c, str) else c
    glColor4f(r, g, b, alpha)

def retangulo(x, y, w, h, cor, alpha=1.0, raio=6):
    set_cor(cor, alpha)
    glBegin(GL_QUADS)
    glVertex2f(x+raio,y);     glVertex2f(x+w-raio,y)
    glVertex2f(x+w-raio,y+h); glVertex2f(x+raio,  y+h)
    glEnd()
    glBegin(GL_QUADS)
    glVertex2f(x,  y+raio);   glVertex2f(x+w,y+raio)
    glVertex2f(x+w,y+h-raio); glVertex2f(x,  y+h-raio)
    glEnd()
    for cx,cy,a0,a1 in [(x+raio,y+raio,180,270),(x+w-raio,y+raio,270,360), (x+w-raio,y+h-raio,0,90),(x+raio,y+h-raio,90,180)]:
        glBegin(GL_TRIANGLE_FAN)
        glVertex2f(cx,cy)
        for ang in range(int(a0),int(a1)+1,10):
            a=math.radians(ang)
            glVertex2f(cx+raio*math.cos(a),cy+raio*math.sin(a))
        glEnd()

def borda_ret(x,y,w,h,cor,esp=2):
    glLineWidth(esp); set_cor(cor)
    glBegin(GL_LINE_LOOP)
    glVertex2f(x,y);glVertex2f(x+w,y);glVertex2f(x+w,y+h);glVertex2f(x,y+h)
    glEnd()

def txt(x,y,s,cor="branco",fonte=None):
    if fonte is None: fonte=GLUT_BITMAP_HELVETICA_18
    set_cor(cor); glRasterPos2f(x,y)
    for c in s: glutBitmapCharacter(fonte,ord(c))

def txt12(x,y,s,cor="branco"):
    txt(x,y,s,cor,GLUT_BITMAP_HELVETICA_12)

def txt_c(cx,y,s,cor="branco",fonte=None):
    if fonte is None: fonte=GLUT_BITMAP_HELVETICA_18
    txt(cx-len(s)*5,y,s,cor,fonte)

def circulo(cx,cy,r,cor,segs=32):
    set_cor(cor)
    glBegin(GL_TRIANGLE_FAN); glVertex2f(cx,cy)
    for i in range(segs+1):
        a=2*math.pi*i/segs
        glVertex2f(cx+r*math.cos(a),cy+r*math.sin(a))
    glEnd()

def linha(x0,y0,x1,y1,cor,esp=1.5):
    glLineWidth(esp); set_cor(cor)
    glBegin(GL_LINES); glVertex2f(x0,y0); glVertex2f(x1,y1); glEnd()

# Grade 
def _celula(col, lin, fase):
    N = fase["grade"]
    tam = min((GRADE_X2-GRADE_X1-20)//N, (TOPO_Y-GRADE_Y1-20)//N)
    ox = GRADE_X1 + ((GRADE_X2-GRADE_X1) - N*tam)//2
    oy = GRADE_Y1 + ((TOPO_Y  -GRADE_Y1) - N*tam)//2
    return ox+col*tam, oy+(N-1-lin)*tam, tam

def desenhar_grade(fase, rpx, rpy):
    N = fase["grade"]
    retangulo(GRADE_X1, GRADE_Y1, GRADE_X2-GRADE_X1, TOPO_Y-GRADE_Y1, "painel_esq", raio=10)
    for lin in range(N):
        for col in range(N):
            px,py,tam = _celula(col,lin,fase)
            retangulo(px+2,py+2,tam-4,tam-4,"chao",raio=4)
            if (col,lin) in fase["paredes"]:
                retangulo(px+2,py+2,tam-4,tam-4,"parede",raio=4)
                set_cor("grid_borda"); glLineWidth(1)
                for gy in range(4):
                    y_=py+4+gy*(tam-4)//4
                    glBegin(GL_LINES)
                    glVertex2f(px+2,y_); glVertex2f(px+tam-2,y_)
                    glEnd()
            borda_ret(px+1,py+1,tam-2,tam-2,"grid_borda",1)

    # estrela (objetivo)
    ox,oy,tam = _celula(fase["objetivo"][0],fase["objetivo"][1],fase)
    cx=ox+tam//2; cy=oy+tam//2
    pulse=1.0+0.12*math.sin(estrela_t*3)
    r=(tam//2-6)*pulse
    set_cor("objetivo")
    glBegin(GL_TRIANGLE_FAN); glVertex2f(cx,cy)
    for i in range(11):
        a=math.pi/2+i*math.pi/5
        rv=r*0.42 if i%2==0 else r*0.18
        glVertex2f(cx+rv*math.cos(a),cy+rv*math.sin(a))
    glEnd()

    # robô
    desenhar_robo(rpx, rpy, tam, robo_dir)

def desenhar_robo(px, py, tam, d):
    cx=px+tam//2; cy=py+tam//2; r=tam//2-8

    # corpo
    retangulo(cx-r,cy-r,r*2,r*2,"robo",raio=6)

    # olhos (direção)
    olhos={
        "D":[(r*.35, r*.22),(r*.35,-r*.22)],
        "E":[(-r*.35,r*.22),(-r*.35,-r*.22)],
        "C":[(r*.22, r*.35),(-r*.22, r*.35)],
        "B":[(r*.22,-r*.35),(-r*.22,-r*.35)],
    }
    for dx,dy in olhos.get(d,[]):
        circulo(cx+dx,cy+dy,r*.18,"branco")
        circulo(cx+dx*1.1,cy+dy*1.1,r*.09,(0.1,0.1,0.1))

# Paleta (esquerda) 
BLOCO_LABELS = {
    "FRENTE":"FRENTE","DIREITA":"GIRAR ->","ESQUERDA":"GIRAR <-",
    "SE_PAREDE":"SE PAREDE","SENAO":"SENAO","REPITA":"REPITA(3)","FIM":"FIM",
}
BLOCO_DESC = {
    "FRENTE":"Anda 1 passo","DIREITA":"Vira a direita",
    "ESQUERDA":"Vira a esquerda","SE_PAREDE":"Se ha parede a frente",
    "SENAO":"Senao (caso contrario)","REPITA":"Repete 3 vezes","FIM":"Fim do bloco",
}
_paleta_rects = {}

def desenhar_paleta(fase):
    blocos=fase["blocos"]
    BW,BH=300,44; BX=20
    # O painel de blocos começa logo abaixo do topo da grade
    # e termina acima dos botões (que ficam em y=10..120)
    BY_start = TOPO_Y - 15

    retangulo(PAL_X1,0,PAL_X2,H,"painel_esq",raio=0)

    # título do painel
    txt_c(PAL_X2//2, H-26, "BLOCOS", "destaque")
    linha(10,H-34,PAL_X2-10,H-34,"grid_borda")

    for i,nome in enumerate(blocos):
        by = BY_start-(i+1)*(BH+8)
        if by < 130: break
        retangulo(BX,by,BW,BH,nome,raio=8)
        borda_ret(BX,by,BW,BH,"branco",1)
        txt(BX+12, by+BH//2+6,  BLOCO_LABELS[nome],"branco")
        txt12(BX+12,by+10, BLOCO_DESC[nome],(0.85,0.85,0.85))
        _paleta_rects[nome]=(BX,by,BW,BH)

    # botões de controle
    for (bx,by,bw,bh),label,cor in [
        (BTN_RUN,  "RODAR",  "btn_run"),
        (BTN_CLEAR,"LIMPAR", "btn_clear"),
        (BTN_NEXT, "PROXIMA","btn_run" if sucesso else "parede"),
    ]:
        retangulo(bx,by,bw,bh,cor,raio=8)
        borda_ret(bx,by,bw,bh,"branco",1)
        txt(bx+12,by+bh//2+6,label,"branco")

# Programa (direita) COM SCROLL 
_prog_rects=[]
PROG_SCROLL_AREA = (PROG_X1, 105, PROG_X2-PROG_X1, H-220)  # Área visível do programa

def desenhar_programa(fase):
    global _prog_rects, scroll_offset
    _prog_rects=[]
    
    # Fundo do painel
    retangulo(PROG_X1,0,PROG_X2-PROG_X1,H,"painel_dir",raio=0)
    linha(PROG_X1,0,PROG_X1,H,"grid_borda",2)

    # Título
    txt_c((PROG_X1+PROG_X2)//2, H-26,"MEU PROGRAMA","destaque")
    linha(PROG_X1+10,H-34,PROG_X2-10,H-34,"grid_borda")

    # Contador de blocos
    BW,BH=PROG_X2-PROG_X1-30,38; BX=PROG_X1+15
    max_b=fase["max_blocos"]
    cnt_cor="sucesso" if len(programa)<=max_b else "erro"
    txt12(BX, 95, f"Blocos: {len(programa)}/{max_b}", cnt_cor)

    # Área de scroll - recorta para mostrar apenas a parte visível
    x_area, y_area, w_area, h_area = PROG_SCROLL_AREA
    
    # Calcula altura total do conteúdo
    total_height = len(programa) * (BH + 5) + 20
    max_scroll = max(0, total_height - h_area + 20)
    
    # Ajusta scroll para não ultrapassar
    scroll_offset = max(0, min(scroll_offset, max_scroll))
    
    # Desenha a barra de scroll se necessário
    if max_scroll > 0:
        bar_x = PROG_X2 - 12
        bar_y = y_area + 4
        bar_h = h_area - 8
        bar_w = 8
        
        # Fundo da barra
        retangulo(bar_x, bar_y, bar_w, bar_h, "grid", alpha=0.3, raio=4)
        
        # Posição do thumb
        thumb_ratio = scroll_offset / max_scroll if max_scroll > 0 else 0
        thumb_h = max(30, bar_h * (h_area / (total_height + 20)))
        thumb_y = bar_y + thumb_ratio * (bar_h - thumb_h)
        
        # Thumb da barra
        retangulo(bar_x, thumb_y, bar_w, thumb_h, "destaque", alpha=0.6, raio=4)

    # Desenha apenas os comandos visíveis
    visible_start = max(0, int(scroll_offset / (BH + 5)) - 1)
    visible_end = min(len(programa), visible_start + int(h_area / (BH + 5)) + 3)
    
    for i in range(visible_start, visible_end):
        # Calcula posição com scroll
        y_pos = y_area + h_area - 20 - (i+1) * (BH + 5) + scroll_offset
        if y_pos + BH < y_area or y_pos > y_area + h_area:
            continue
            
        depth=0
        for c in programa[:i]:
            if c in("SE_PAREDE","REPITA"): depth+=1
            if c=="FIM": depth=max(0,depth-1)
        indent=depth*18
        
        ativo=executando and i==passo_atual
        alfa=1.0 if not executando else (1.0 if ativo else 0.45)
        
        cmd = programa[i]
        retangulo(BX+indent, y_pos, BW-indent, BH, cmd, alfa, raio=6)
        if ativo:
            borda_ret(BX+indent-2, y_pos-2, BW-indent+4, BH+4, "destaque", 3)
        txt(BX+indent+10, y_pos+BH//2+6, BLOCO_LABELS[cmd], "branco")
        
        # Botão X para remover (apenas se não estiver executando)
        if not executando and i >= 0:
            rx=BX+BW-26; ry=y_pos+9; rw=18; rh=20
            retangulo(rx, ry, rw, rh, "btn_clear", raio=4)
            txt12(rx+4, ry+14, "x", "branco")
            _prog_rects.append((rx, ry, rw, rh, i))

    if not programa:
        txt_c((PROG_X1+PROG_X2)//2, y_area + h_area//2 + 12, "Clique nos blocos", "texto_esc")
        txt_c((PROG_X1+PROG_X2)//2, y_area + h_area//2 - 10, "para montar seu programa!", "texto_esc")
    
    # Desenha borda da área de scroll
    borda_ret(x_area, y_area, w_area, h_area, "grid_borda", 1)

# Topo central (título, descrição, conceito, dica, msg)
def desenhar_topo(fase):
    # fundo do topo
    retangulo(PAL_X2, TOPO_Y, GRADE_X2-PAL_X2, TOPO_H, "painel_esq", raio=0)
    linha(PAL_X2, TOPO_Y, GRADE_X2, TOPO_Y, "grid_borda", 2)

    CX = (PAL_X2+GRADE_X2)//2   # centro horizontal da grade

    # linha 1 — título  (y mais alto = topo)
    txt_c(CX, H-26, fase["titulo"], "destaque", GLUT_BITMAP_HELVETICA_18)

    # linha 2 e 3 — descrição
    txt_c(CX, H-50, fase["descricao"][0], "branco")
    if len(fase["descricao"]) > 1:
        txt_c(CX, H-70, fase["descricao"][1], "branco")

    # linha 4 — conceito (caixinha)
    cy_conceito = TOPO_Y + 62
    retangulo(PAL_X2+10, cy_conceito, GRADE_X2-PAL_X2-20, 24, "grid", raio=5)
    txt(PAL_X2+18, cy_conceito+15, fase["conceito"], "destaque", GLUT_BITMAP_HELVETICA_12)

    # linha 5 — dica
    txt12(PAL_X2+10, TOPO_Y+38, fase["dica"], "texto_esc")

    # mensagem de feedback (erro / sucesso)
    if msg and msg_timer > 0:
        alfa = min(1.0, msg_timer)
        cy_msg = TOPO_Y + 92
        cor_fundo = "btn_run" if msg_cor == "sucesso" else "btn_clear"
        retangulo(PAL_X2+10, cy_msg, GRADE_X2-PAL_X2-20, 28, cor_fundo, alfa*0.9, raio=7)
        txt_c(CX, cy_msg+18, msg, "branco")

# Lógica de execução 
DIR_ORDER=["C","D","B","E"]

def girar(d,s):
    i=DIR_ORDER.index(d)
    return DIR_ORDER[(i+(1 if s=="D" else -1))%4]

def frente_de(col,lin,d):
    return {"D":(col+1,lin),"E":(col-1,lin),"C":(col,lin-1),"B":(col,lin+1)}[d]

def tem_parede(col,lin,d,fase):
    nc,nl=frente_de(col,lin,d); N=fase["grade"]
    if nc<0 or nc>=N or nl<0 or nl>=N: return True
    return (nc,nl) in fase["paredes"]

def expandir_bloco(seq):
    out = []
    i = 0
    while i < len(seq):
        cmd = seq[i]
        if cmd in ("FRENTE", "DIREITA", "ESQUERDA"):
            out.append(cmd)
            i += 1
        elif cmd == "SE_PAREDE":
            i += 1
            se_bloco = []
            senao_bloco = []
            depth = 0
            modo = "se"
            
            while i < len(seq):
                c = seq[i]
                if c in ("SE_PAREDE", "REPITA"):
                    depth += 1
                elif c == "FIM":
                    if depth == 0:
                        i += 1
                        break
                    depth -= 1
                elif c == "SENAO" and depth == 0:
                    modo = "senao"
                    i += 1
                    continue
                
                if modo == "se":
                    se_bloco.append(c)
                else:
                    senao_bloco.append(c)
                i += 1
            
            out.append(("SE_PAREDE", se_bloco, senao_bloco))
        elif cmd == "REPITA":
            i += 1
            bloco = []
            depth = 0
            
            while i < len(seq):
                c = seq[i]
                if c in ("SE_PAREDE", "REPITA"):
                    depth += 1
                elif c == "FIM":
                    if depth == 0:
                        i += 1
                        break
                    depth -= 1
                bloco.append(c)
                i += 1
            
            # Expande e repete 3 vezes
            bloco_expandido = expandir_bloco(bloco)
            for _ in range(3):
                out.extend(bloco_expandido)
        else:
            i += 1
    return out

def resolver_condicionais(insts, col, lin, d, fase):
    out = []
    for inst in insts:
        if isinstance(inst, tuple) and inst[0] == "SE_PAREDE":
            _, se_bloco, senao_bloco = inst
            # Verifica se tem parede à frente
            if tem_parede(col, lin, d, fase):
                sub = resolver_condicionais(se_bloco, col, lin, d, fase)
            else:
                sub = resolver_condicionais(senao_bloco, col, lin, d, fase)
            
            # Executa os comandos do bloco escolhido
            for s in sub:
                out.append(s)
                # Atualiza posição/direção para próximas condicionais
                if s == "FRENTE":
                    nc, nl = frente_de(col, lin, d)
                    if 0 <= nc < fase["grade"] and 0 <= nl < fase["grade"] and (nc, nl) not in fase["paredes"]:
                        col, lin = nc, nl
                elif s == "DIREITA":
                    d = girar(d, "D")
                elif s == "ESQUERDA":
                    d = girar(d, "E")
        else:
            out.append(inst)
            # Atualiza posição/direção para próximas condicionais
            if inst == "FRENTE":
                nc, nl = frente_de(col, lin, d)
                if 0 <= nc < fase["grade"] and 0 <= nl < fase["grade"] and (nc, nl) not in fase["paredes"]:
                    col, lin = nc, nl
            elif inst == "DIREITA":
                d = girar(d, "D")
            elif inst == "ESQUERDA":
                d = girar(d, "E")
    return out

def iniciar_execucao():
    global exec_stack, executando, passo_atual, sucesso
    global robo_pos, robo_dir, msg, msg_cor, msg_timer, animacao_t
    
    fase = FASES[fase_atual]
    robo_pos = fase["robo"]
    robo_dir = fase["dir"]
    sucesso = False
    animacao_t = 1.0

    # Expande o programa (REPITA)
    expanded = expandir_bloco(programa[:])
    
    # Resolve condicionais
    col0, lin0 = fase["robo"]
    exec_stack = resolver_condicionais(expanded, col0, lin0, fase["dir"], fase)
    executando = True
    passo_atual = 0

def executar_passo():
    global robo_pos, robo_dir, passo_atual, executando
    global msg, msg_cor, msg_timer, sucesso, animacao_t
    if not exec_stack: 
        executando = False
        return
    
    fase = FASES[fase_atual]
    inst = exec_stack.pop(0)
    col, lin = robo_pos
    
    if inst == "FRENTE":
        nc, nl = frente_de(col, lin, robo_dir)
        N = fase["grade"]
        if nc < 0 or nc >= N or nl < 0 or nl >= N or (nc, nl) in fase["paredes"]:
            executando = False
            msg = "Ops! O robo bateu na parede!"
            msg_cor = "erro"
            msg_timer = 3.0
            return
        animacao_t = 0.0
        robo_pos = (nc, nl)
    elif inst == "DIREITA":
        robo_dir = girar(robo_dir, "D")
    elif inst == "ESQUERDA":
        robo_dir = girar(robo_dir, "E")
    
    if robo_pos == fase["objetivo"]:
        executando = False
        sucesso = True
        msg = "Parabens! Voce chegou la!"
        msg_cor = "sucesso"
        msg_timer = 5.0

# Mouse 
def mouse_cb(win,button,action,mods):
    global programa, executando, fase_atual, sucesso
    global msg, msg_cor, msg_timer, robo_pos, robo_dir, scroll_offset
    global exec_stack
    if action != glfw.PRESS or button != glfw.MOUSE_BUTTON_LEFT: return
    mx,my=glfw.get_cursor_pos(win); my=H-my
    fase=FASES[fase_atual]

    bx,by,bw,bh=BTN_RUN
    if bx<=mx<=bx+bw and by<=my<=by+bh:
        if not executando: iniciar_execucao()
        return

    bx,by,bw,bh=BTN_CLEAR
    if bx<=mx<=bx+bw and by<=my<=by+bh:
        programa.clear(); executando=False; sucesso=False
        robo_pos=fase["robo"]; robo_dir=fase["dir"]; msg=""; msg_timer=0
        scroll_offset = 0  # Reset scroll
        return

    bx,by,bw,bh=BTN_NEXT
    if bx<=mx<=bx+bw and by<=my<=by+bh and sucesso:
        if fase_atual<len(FASES)-1:
            fase_atual+=1; programa.clear(); sucesso=False
            nova=FASES[fase_atual]
            robo_pos=nova["robo"]; robo_dir=nova["dir"]; msg=""; msg_timer=0
            scroll_offset = 0  # Reset scroll
        return

    if not executando:
        for nome,(px,py,pw,ph) in _paleta_rects.items():
            if px<=mx<=px+pw and py<=my<=py+ph:
                if len(programa)<fase["max_blocos"]: 
                    programa.append(nome)
                    # Auto-scroll para mostrar o novo comando
                    BW=PROG_X2-PROG_X1-30
                    BH=38
                    total_height = len(programa) * (BH + 5) + 20
                    x_area, y_area, w_area, h_area = PROG_SCROLL_AREA
                    max_scroll = max(0, total_height - h_area + 20)
                    if max_scroll > 0:
                        scroll_offset = max_scroll
                else: 
                    msg="Programa cheio!"; msg_cor="erro"; msg_timer=2.0
                return
        
        # Clique no X para remover bloco
        for (px,py,pw,ph,idx) in _prog_rects:
            if px<=mx<=px+pw and py<=my<=py+ph:
                if idx < len(programa):
                    programa.pop(idx)
                    # Ajusta scroll se necessário
                    BW=PROG_X2-PROG_X1-30
                    BH=38
                    total_height = len(programa) * (BH + 5) + 20
                    x_area, y_area, w_area, h_area = PROG_SCROLL_AREA
                    max_scroll = max(0, total_height - h_area + 20)
                    scroll_offset = min(scroll_offset, max_scroll)
                return

def scroll_cb(win, xoffset, yoffset):
    global scroll_offset
    
    # Verifica se o mouse está sobre a área do programa
    mx, my = glfw.get_cursor_pos(win)
    my = H - my
    
    x_area, y_area, w_area, h_area = PROG_SCROLL_AREA
    if x_area <= mx <= x_area + w_area and y_area <= my <= y_area + h_area:
        # Calcula o scroll
        scroll_step = 38  # Altura de um bloco + espaçamento
        scroll_offset -= yoffset * scroll_step
        
        # Limita o scroll
        BW = PROG_X2 - PROG_X1 - 30
        BH = 38
        total_height = len(programa) * (BH + 5) + 20
        max_scroll = max(0, total_height - h_area + 20)
        scroll_offset = max(0, min(scroll_offset, max_scroll))

# Main loop 
EXEC_DELAY=0.55
_exec_acc=0.0

def main():
    global msg_timer, estrela_t, animacao_t, _exec_acc, executando

    if not glfw.init(): sys.exit("GLFW falhou")
    win=glfw.create_window(W,H,"CodeBot",None,None)
    if not win: glfw.terminate(); sys.exit()
    glfw.make_context_current(win)
    glfw.set_mouse_button_callback(win, mouse_cb)
    glfw.set_scroll_callback(win, scroll_cb)  # Adiciona callback do scroll
    glutInit()

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glMatrixMode(GL_PROJECTION); glLoadIdentity()
    glOrtho(0,W,0,H,-1,1)
    glMatrixMode(GL_MODELVIEW); glLoadIdentity()

    fase=FASES[fase_atual]
    global robo_pos, robo_dir
    robo_pos=fase["robo"]; robo_dir=fase["dir"]
    rpx,rpy,_=_celula(*robo_pos,fase)

    t_ant=glfw.get_time()
    while not glfw.window_should_close(win):
        t=glfw.get_time(); dt=min(t-t_ant,0.05); t_ant=t
        estrela_t+=dt
        if msg_timer>0: msg_timer=max(0,msg_timer-dt)
        if animacao_t<1.0: animacao_t=min(1.0,animacao_t+dt*7)

        if executando and exec_stack:
            _exec_acc+=dt
            if _exec_acc>=EXEC_DELAY: _exec_acc=0.0; executar_passo()
        elif executando and not exec_stack:
            executando=False
            if robo_pos!=FASES[fase_atual]["objetivo"] and not sucesso:
                global msg,msg_cor
                msg="Nao chegou la... tente de novo!"; msg_cor="erro"; msg_timer=3.0

        fase=FASES[fase_atual]
        px0,py0,tam=_celula(*robo_pos,fase)
        rpx=rpx+(px0-rpx)*min(1.0,animacao_t)
        rpy=rpy+(py0-rpy)*min(1.0,animacao_t)
        if animacao_t>=1.0: rpx=px0; rpy=py0

        glClearColor(*COR["bg"],1); glClear(GL_COLOR_BUFFER_BIT)
        desenhar_paleta(fase)
        desenhar_topo(fase)
        desenhar_grade(fase,int(rpx),int(rpy))
        desenhar_programa(fase)

        glfw.swap_buffers(win)
        glfw.poll_events()

    glfw.terminate()

if __name__=="__main__":
    main()