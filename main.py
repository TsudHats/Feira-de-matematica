import pygame
import sys
import os
import time

pygame.init()

LARGURA, ALTURA = 1920, 1080
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Pacman e Fantasmas")

fonte_grande = pygame.font.SysFont("Arial", 64)
fonte_pequena = pygame.font.SysFont("Arial", 32)
fonte_tempo = pygame.font.SysFont("Arial", 28)
fonte_contagem = pygame.font.SysFont("Arial", 24)

def recurso_caminho(nome_arquivo):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, nome_arquivo)

try:
    fundo_img = pygame.image.load(recurso_caminho('imagens/fundo.png')).convert()
except Exception as e:
    print("Erro ao carregar fundo:", e)
    fundo_img = None

try:
    barco_img = pygame.image.load(recurso_caminho('imagens/barco.png')).convert_alpha()
except Exception as e:
    print("Erro ao carregar barco:", e)
    barco_img = None

try:
    pacman_img = pygame.image.load(recurso_caminho('imagens/pacman.png')).convert_alpha()
except Exception as e:
    print("Erro ao carregar pacman:", e)
    pacman_img = None

try:
    fantasma_img = pygame.image.load(recurso_caminho('imagens/fantasma.png')).convert_alpha()
except Exception as e:
    print("Erro ao carregar fantasma:", e)
    fantasma_img = None

try:
    vitoria_img = pygame.image.load(recurso_caminho('imagens/vitoria.png')).convert_alpha()
except Exception as e:
    print("Erro ao carregar vitoria:", e)
    vitoria_img = None

try:
    som_img = pygame.image.load(recurso_caminho('imagens/som.png')).convert_alpha()
except Exception as e:
    print("Erro ao carregar imagem de som:", e)
    som_img = None

try:
    mutado_img = pygame.image.load(recurso_caminho('imagens/mutado.png')).convert_alpha()
except Exception as e:
    print("Erro ao carregar imagem mutado:", e)
    mutado_img = None

# Carregar música de fundo
try:
    pygame.mixer.music.load(recurso_caminho('musica/musica_de_fundo.mp3'))
    pygame.mixer.music.play(-1)
    pygame.mixer.music.set_volume(0.1)  # Ajusta volume para 30%
except Exception as e:
    print("Erro ao carregar música:", e)

# Carregar efeitos sonoros de game over e vitória
try:
    som_game_over = pygame.mixer.Sound(recurso_caminho('musica/game_over.mp3'))
except Exception as e:
    print("Erro ao carregar som de game over:", e)
    som_game_over = None

try:
    som_vitoria = pygame.mixer.Sound(recurso_caminho('musica/vitoria.mp3'))
except Exception as e:
    print("Erro ao carregar som de vitoria:", e)
    som_vitoria = None

POS_PACMAN_INICIAL = [(-20, 350), (45, 350), (110, 350)]
POS_FANTASMA_INICIAL = [(-20, 550), (45, 550), (110, 550)]

POS_BARCO_INICIAL = [180, 390]
POS_BARCO_FINAL = [1390, 390]
VEL_ANIMACAO = 30

POS_PACMAN_FINAL = [(1710, 350), (1640, 350), (1570, 350)]
POS_FANTASMA_FINAL = [(1710, 550), (1640, 550), (1570, 550)]

sprites_no_barco = []

posicao_sprites_fora_do_barco = ["inicial"] * 6

barco_pos = POS_BARCO_INICIAL.copy()
barco_animando = False
barco_movendo_para = None

animando_ataque = False
fantasmas_anim_pos = [list(pos) for pos in POS_FANTASMA_INICIAL]
fantasmas_atingiram = False
game_over = False
show_restart = False
ilha_em_ataque = None
vitoria = False

inicio_tempo = None
vitorias = 0
derrotas = 0

musica_tocando = True
icone_som = som_img

def tipo_sprite(sprite_index):
    return "pacman" if sprite_index < 3 else "fantasma"

def contar_pacmans_fantasmas_ilha(ilha):
    pacman_count = 0
    fantasma_count = 0

    for i in range(6):
        estado = posicao_sprites_fora_do_barco[i]
        if estado == ilha:
            if tipo_sprite(i) == "pacman":
                pacman_count += 1
            else:
                fantasma_count += 1

    if ilha == "inicial" and barco_pos == POS_BARCO_INICIAL:
        for sprite_index in sprites_no_barco:
            if tipo_sprite(sprite_index) == "pacman":
                pacman_count += 1
            else:
                fantasma_count += 1
    if ilha == "final" and barco_pos == POS_BARCO_FINAL:
        for sprite_index in sprites_no_barco:
            if tipo_sprite(sprite_index) == "pacman":
                pacman_count += 1
            else:
                fantasma_count += 1

    return pacman_count, fantasma_count

def teleportar_sprites_no_barco_para_ilha():
    global sprites_no_barco, posicao_sprites_fora_do_barco, barco_pos
    if barco_pos == POS_BARCO_FINAL:
        ilha_destino = "final"
    else:
        ilha_destino = "inicial"

    for sprite_index in sprites_no_barco:
        posicao_sprites_fora_do_barco[sprite_index] = ilha_destino
    sprites_no_barco.clear()

def verificar_game_over():
    global animando_ataque, game_over, show_restart, ilha_em_ataque, vitoria, vitorias, derrotas

    pacman_init, fantasma_init = contar_pacmans_fantasmas_ilha("inicial")
    pacman_final, fantasma_final = contar_pacmans_fantasmas_ilha("final")

    if fantasma_init > pacman_init > 0 and fantasma_init >= fantasma_final:
        teleportar_sprites_no_barco_para_ilha()
        animando_ataque = True
        game_over = False
        show_restart = False
        ilha_em_ataque = "inicial"
        vitoria = False
        inicializar_animacao_ataque()
        derrotas += 1
    elif fantasma_final > pacman_final > 0:
        teleportar_sprites_no_barco_para_ilha()
        animando_ataque = True
        game_over = False
        show_restart = False
        ilha_em_ataque = "final"
        vitoria = False
        inicializar_animacao_ataque()
        derrotas += 1
    else:
        if pacman_final == 3 and fantasma_final == 3:
            animando_ataque = False
            game_over = False
            show_restart = True
            ilha_em_ataque = None
            vitoria = True
            vitorias += 1
        else:
            animando_ataque = False
            game_over = False
            show_restart = False
            ilha_em_ataque = None
            vitoria = False

def inicializar_animacao_ataque():
    global fantasmas_anim_pos
    if ilha_em_ataque == "inicial":
        for i in range(3):
            if posicao_sprites_fora_do_barco[i + 3] == "inicial":
                fantasmas_anim_pos[i] = list(POS_FANTASMA_INICIAL[i])
            else:
                fantasmas_anim_pos[i] = [-500, -500]
    elif ilha_em_ataque == "final":
        for i in range(3):
            if posicao_sprites_fora_do_barco[i + 3] == "final":
                fantasmas_anim_pos[i] = list(POS_FANTASMA_FINAL[i])
            else:
                fantasmas_anim_pos[i] = [-500, -500]

def reiniciar_jogo():
    global sprites_no_barco, posicao_sprites_fora_do_barco, barco_pos
    global animando_ataque, fantasmas_atingiram, game_over, show_restart, ilha_em_ataque, vitoria, inicio_tempo
    sprites_no_barco.clear()
    posicao_sprites_fora_do_barco[:] = ["inicial"] * 6
    barco_pos[:] = POS_BARCO_INICIAL.copy()
    animando_ataque = False
    fantasmas_atingiram = False
    game_over = False
    show_restart = False
    ilha_em_ataque = None
    vitoria = False
    inicio_tempo = time.time()
    for i in range(3):
        fantasmas_anim_pos[i] = list(POS_FANTASMA_INICIAL[i])
    # Reinicia a música do jogo toda vez que o jogo for reiniciado
    if musica_tocando:
        pygame.mixer.music.stop()
        pygame.mixer.music.play(-1)

def desenhar_texto_centralizado(tela, texto, fonte, cor, y_pos):
    texto_render = fonte.render(texto, True, cor)
    retangulo = texto_render.get_rect(center=(LARGURA // 2, y_pos))
    tela.blit(texto_render, retangulo)

def desenhar_tempo(tela, fonte, tempo_segundos):
    minutos = int(tempo_segundos // 60)
    segundos = int(tempo_segundos % 60)
    texto = f"Tempo: {minutos:02d}:{segundos:02d}"
    texto_render = fonte.render(texto, True, (255, 255, 255))
    tela.blit(texto_render, (10, 10))

def desenhar_contagem_ilhas(tela):
    pacman_init, fantasma_init = contar_pacmans_fantasmas_ilha("inicial")
    pacman_final, fantasma_final = contar_pacmans_fantasmas_ilha("final")
    texto = f"PACMAN & FANTASMAS - MISSIONÁRIOS E CANIBAIS:\n                   INICIO: {{{pacman_init} - {fantasma_init}}}   FINAL: {{{pacman_final} - {fantasma_final}}}"
    linhas = texto.split('\n')
    y_base = 10
    for i, linha in enumerate(linhas):
        render_linha = fonte_contagem.render(linha, True, (255, 255, 255))
        tela.blit(render_linha, (650, y_base + i*22))

def desenhar_vitorias_derrotas(tela):
    texto = f"Vitórias: {vitorias}   Derrotas: {derrotas}"
    texto_render = fonte_contagem.render(texto, True, (255, 255, 255))
    largura_texto = texto_render.get_width()
    tela.blit(texto_render, (LARGURA - largura_texto - 10, ALTURA - 30))

def desenhar_botao_mute(tela):
    global icone_som
    if icone_som:
        tela.blit(icone_som, (LARGURA - 100, 10))  # canto superior direito

def toggle_sprite(index, tipo):
    global sprites_no_barco, posicao_sprites_fora_do_barco, barco_pos
    if tipo == "pacman":
        sprite_index = index
    else:
        sprite_index = index + 3

    # Checa o estado atual do sprite para determinar se pode embarcar/desembarcar
    sprite_state = posicao_sprites_fora_do_barco[sprite_index]

    if barco_pos == POS_BARCO_FINAL:
        # Barco na ilha final: só pode embarcar se estiver na ilha final
        if sprite_state != "final":
            return
    else:
        # Barco na ilha inicial: só pode embarcar se estiver na ilha inicial
        if sprite_state != "inicial":
            return

    if sprite_index in sprites_no_barco:
        sprites_no_barco.remove(sprite_index)
        posicao_sprites_fora_do_barco[sprite_index] = sprite_state  # volta para ilha atual
    elif len(sprites_no_barco) < 2:
        sprites_no_barco.append(sprite_index)
        posicao_sprites_fora_do_barco[sprite_index] = None




def main():
    global barco_animando, barco_pos, barco_movendo_para, posicao_sprites_fora_do_barco
    global animando_ataque, fantasmas_atingiram, game_over, show_restart, ilha_em_ataque, vitoria, inicio_tempo
    global musica_tocando, icone_som
    clock = pygame.time.Clock()
    rodando = True
    
    inicio_tempo = time.time()  # inicializa o temporizador
    game_over_som_tocado = False
    vitoria_som_tocado = False

    while rodando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False
            if game_over or vitoria:
                if evento.type == pygame.KEYDOWN:
                    reiniciar_jogo()
                    game_over_som_tocado = False
                    vitoria_som_tocado = False
                continue
            if animando_ataque:
                continue
                
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    rodando = False
                if evento.key == pygame.K_SPACE:
                    if len(sprites_no_barco) > 0 and not barco_animando:
                        if barco_pos == POS_BARCO_INICIAL:
                            barco_animando = True
                            barco_movendo_para = "final"
                        elif barco_pos == POS_BARCO_FINAL:
                            barco_animando = True
                            barco_movendo_para = "inicial"

            if evento.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                # Verifica se clicou no botão de mute
                if LARGURA - 100 <= mouse_pos[0] <= LARGURA - 40 and 10 <= mouse_pos[1] <= 70:
                    musica_tocando = not musica_tocando
                    if musica_tocando:
                        pygame.mixer.music.unpause()
                        icone_som = som_img
                    else:
                        pygame.mixer.music.pause()
                        icone_som = mutado_img
                    continue

                clicou_no_barco = False
                for idx_no_barco, sprite_index in enumerate(sprites_no_barco):
                    if sprite_index < 3:
                        img = pacman_img
                    else:
                        img = fantasma_img

                    x_desloc = barco_pos[0] + idx_no_barco * (img.get_width() - 8)
                    y_desloc = barco_pos[1] + 20
                    rect = pygame.Rect(x_desloc, y_desloc, img.get_width(), img.get_height())
                    if rect.collidepoint(mouse_pos):
                        if not barco_animando:
                            sprites_no_barco.remove(sprite_index)
                            # Retorna para ilha atual em que o barco está
                            if barco_pos == POS_BARCO_FINAL:
                                posicao_sprites_fora_do_barco[sprite_index] = "final"
                            else:
                                posicao_sprites_fora_do_barco[sprite_index] = "inicial"
                        clicou_no_barco = True
                        break
                if clicou_no_barco:
                    continue

                clicked_sprite_outside = False
                for i, pos in enumerate(POS_PACMAN_FINAL):
                    sprite_idx = i
                    if pacman_img and posicao_sprites_fora_do_barco[sprite_idx] == "final":
                        rect = pygame.Rect(pos[0], pos[1], pacman_img.get_width(), pacman_img.get_height())
                        if rect.collidepoint(mouse_pos):
                            if not barco_animando and barco_pos == POS_BARCO_FINAL:
                                if len(sprites_no_barco) < 2:
                                    sprites_no_barco.append(sprite_idx)
                                    posicao_sprites_fora_do_barco[sprite_idx] = None
                            clicked_sprite_outside = True
                            break
                if clicked_sprite_outside:
                    continue

                for i, pos in enumerate(POS_FANTASMA_FINAL):
                    sprite_idx = i + 3
                    if fantasma_img and posicao_sprites_fora_do_barco[sprite_idx] == "final":
                        rect = pygame.Rect(pos[0], pos[1], fantasma_img.get_width(), fantasma_img.get_height())
                        if rect.collidepoint(mouse_pos):
                            if not barco_animando and barco_pos == POS_BARCO_FINAL:
                                if len(sprites_no_barco) < 2:
                                    sprites_no_barco.append(sprite_idx)
                                    posicao_sprites_fora_do_barco[sprite_idx] = None
                            clicked_sprite_outside = True
                            break
                if clicked_sprite_outside:
                    continue

                if barco_pos == POS_BARCO_FINAL:
                    continue

                # Só permite adicionar sprites ao barco da ilha inicial se o sprite estiver na ilha inicial
                if not barco_animando:
                    for i, pos in enumerate(POS_PACMAN_INICIAL):
                        if pacman_img:
                            rect = pygame.Rect(pos[0], pos[1], pacman_img.get_width(), pacman_img.get_height())
                            if rect.collidepoint(mouse_pos):
                                if posicao_sprites_fora_do_barco[i] == "inicial":
                                    toggle_sprite(i, "pacman")
                                break
                    else:
                        for i, pos in enumerate(POS_FANTASMA_INICIAL):
                            if fantasma_img:
                                rect = pygame.Rect(pos[0], pos[1], fantasma_img.get_width(), fantasma_img.get_height())
                                if rect.collidepoint(mouse_pos):
                                    if posicao_sprites_fora_do_barco[i + 3] == "inicial":
                                        toggle_sprite(i, "fantasma")
                                    break

        if barco_animando:
            if barco_movendo_para == "final":
                if barco_pos[0] < POS_BARCO_FINAL[0]:
                    barco_pos[0] += VEL_ANIMACAO
                    if barco_pos[0] > POS_BARCO_FINAL[0]:
                        barco_pos[0] = POS_BARCO_FINAL[0]
                if barco_pos[1] < POS_BARCO_FINAL[1]:
                    barco_pos[1] += VEL_ANIMACAO
                    if barco_pos[1] > POS_BARCO_FINAL[1]:
                        barco_pos[1] = POS_BARCO_FINAL[1]
                elif barco_pos[1] > POS_BARCO_FINAL[1]:
                    barco_pos[1] -= VEL_ANIMACAO
                    if barco_pos[1] < POS_BARCO_FINAL[1]:
                        barco_pos[1] = POS_BARCO_FINAL[1]
                if barco_pos[0] == POS_BARCO_FINAL[0] and barco_pos[1] == POS_BARCO_FINAL[1]:
                    barco_animando = False
                    barco_movendo_para = None
                    verificar_game_over()
            elif barco_movendo_para == "inicial":
                if barco_pos[0] > POS_BARCO_INICIAL[0]:
                    barco_pos[0] -= VEL_ANIMACAO
                    if barco_pos[0] < POS_BARCO_INICIAL[0]:
                        barco_pos[0] = POS_BARCO_INICIAL[0]
                if barco_pos[1] < POS_BARCO_INICIAL[1]:
                    barco_pos[1] += VEL_ANIMACAO
                    if barco_pos[1] > POS_BARCO_INICIAL[1]:
                        barco_pos[1] = POS_BARCO_INICIAL[1]
                elif barco_pos[1] > POS_BARCO_INICIAL[1]:
                    barco_pos[1] -= VEL_ANIMACAO
                    if barco_pos[1] < POS_BARCO_INICIAL[1]:
                        barco_pos[1] = POS_BARCO_INICIAL[1]
                if barco_pos[0] == POS_BARCO_INICIAL[0] and barco_pos[1] == POS_BARCO_INICIAL[1]:
                    barco_animando = False
                    barco_movendo_para = None
                    verificar_game_over()

        if animando_ataque and ilha_em_ataque is not None:
            fantasmas_ids = []
            pacman_alvos = []

            if ilha_em_ataque == "inicial":
                for i in range(3):
                    if posicao_sprites_fora_do_barco[i + 3] == "inicial":
                        fantasmas_ids.append(i + 3)
                pacman_alvos = [POS_PACMAN_INICIAL[i] for i in range(3) if posicao_sprites_fora_do_barco[i] == "inicial"]
            else:
                for i in range(3):
                    if posicao_sprites_fora_do_barco[i + 3] == "final":
                        fantasmas_ids.append(i + 3)
                pacman_alvos = [POS_PACMAN_FINAL[i] for i in range(3) if posicao_sprites_fora_do_barco[i] == "final"]

            if not pacman_alvos:
                pacman_alvos = [(1000, 500)] * len(fantasmas_ids)

            while len(pacman_alvos) < len(fantasmas_ids):
                pacman_alvos.append(pacman_alvos[-1])

            todos_alcancaram = True
            for i, fant_id in enumerate(fantasmas_ids):
                index = fant_id - 3
                fx, fy = fantasmas_anim_pos[index]
                tx, ty = pacman_alvos[i]

                if abs(fx - tx) > 5:
                    fx += 5 if fx < tx else -5
                    todos_alcancaram = False
                if abs(fy - ty) > 5:
                    fy += 5 if fy < ty else -5
                    todos_alcancaram = False

                fantasmas_anim_pos[index] = [fx, fy]

            if todos_alcancaram:
                animando_ataque = False
                game_over = True
                show_restart = True

        # Aqui tocamos os sons de game over ou vitoria e pausamos a música de fundo
        if game_over and not vitoria:
            if musica_tocando and not game_over_som_tocado:
                pygame.mixer.music.pause()
                if som_game_over:
                    som_game_over.play()
                game_over_som_tocado = True
                vitoria_som_tocado = False
        elif vitoria:
            if musica_tocando and not vitoria_som_tocado:
                pygame.mixer.music.pause()
                if som_vitoria:
                    som_vitoria.play()
                vitoria_som_tocado = True
                game_over_som_tocado = False
        else:
            if musica_tocando and not pygame.mixer.music.get_busy():
                pygame.mixer.music.unpause()
            game_over_som_tocado = False
            vitoria_som_tocado = False

        if fundo_img:
            tela.blit(fundo_img, (0, 0))
        else:
            tela.fill((0, 0, 0))

        if inicio_tempo is not None and not game_over and not vitoria:
            tempo_corrente = time.time() - inicio_tempo
            desenhar_tempo(tela, fonte_tempo, tempo_corrente)
        mensagem = "Pressione ESPAÇO para andar o barco (obrigatório ao menos 1 em cima)"
        fonte_mensagem = pygame.font.SysFont("Arial", 32)
        texto_renderizado = fonte_mensagem.render(mensagem, True, (255, 255, 255))  # branco
        tela.blit(texto_renderizado, (LARGURA // 2 - texto_renderizado.get_width() // 2, ALTURA - 50))
        desenhar_contagem_ilhas(tela)
        desenhar_vitorias_derrotas(tela)
        desenhar_botao_mute(tela)

        if game_over:
            tela.fill((0, 0, 0))
            desenhar_texto_centralizado(tela, "GAME OVER", fonte_grande, (255, 0, 0), ALTURA // 2 - 40)
            if show_restart:
                desenhar_texto_centralizado(tela, "Pressione qualquer tecla para recomeçar", fonte_pequena, (255, 255, 255), ALTURA // 2 + 40)
            pygame.display.flip()
            pygame.mixer.music.pause()
            continue

        if vitoria:
            tela.fill((0, 0, 0))
            if vitoria_img:
                x = LARGURA // 2 - vitoria_img.get_width() // 2
                y = ALTURA // 2 - vitoria_img.get_height() // 2
                tela.blit(vitoria_img, (x, y))
            desenhar_texto_centralizado(tela, "Pressione qualquer tecla para recomeçar", fonte_pequena, (255, 255, 255), ALTURA // 2 + 250)
            pygame.display.flip()
            pygame.mixer.music.pause()
            continue

        for i in range(3):
            sprite_idx = i
            if pacman_img and sprite_idx not in sprites_no_barco:
                estado = posicao_sprites_fora_do_barco[sprite_idx]
                if estado == "inicial":
                    tela.blit(pacman_img, POS_PACMAN_INICIAL[i])
                elif estado == "final":
                    tela.blit(pacman_img, POS_PACMAN_FINAL[i])

        for i in range(3):
            sprite_idx = i + 3
            if fantasma_img and sprite_idx not in sprites_no_barco:
                estado = posicao_sprites_fora_do_barco[sprite_idx]
                if estado == "inicial":
                    if animando_ataque and ilha_em_ataque == "inicial":
                        tela.blit(fantasma_img, fantasmas_anim_pos[i])
                    else:
                        tela.blit(fantasma_img, POS_FANTASMA_INICIAL[i])
                elif estado == "final":
                    if animando_ataque and ilha_em_ataque == "final":
                        tela.blit(fantasma_img, fantasmas_anim_pos[i])
                    else:
                        tela.blit(fantasma_img, POS_FANTASMA_FINAL[i])

        if barco_img:
            tela.blit(barco_img, barco_pos)

        for idx_no_barco, sprite_index in enumerate(sprites_no_barco):
            if sprite_index < 3:
                img = pacman_img
            else:
                img = fantasma_img
            x_desloc = barco_pos[0] + idx_no_barco * (img.get_width() - 8)
            y_desloc = barco_pos[1] + 20
            tela.blit(img, (x_desloc, y_desloc))

        pygame.display.flip()
        clock.tick(30)

if __name__ == "__main__":
    main()

