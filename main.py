import pygame as pg
import time
from pygame import Vector2 as vector
from random import randint

class Fundo:
    def __init__(self, dimensoes_tela):
        # super.__init__()
        imagem_original = pg.image.load('canhao_newton/img/ceu.png').convert_alpha()

        self.imagem = pg.transform.scale(imagem_original, dimensoes_tela)

        self.rect = self.imagem.get_rect(topleft=(0, 0))
    
    def desenhar(self, tela):
        tela.blit(self.imagem, self.rect)

class Corpo:
    def __init__(
            self,
            massa           :float,
            raio            :float,
            posicao         :vector,
            velocidade      :vector,
            aceleracao      :vector,
            sprite          :pg.Surface = None
    ) -> None:
        self.massa          = massa
        self.raio           = raio
        self.posicao        = posicao
        self.velocidade     = velocidade
        self.aceleracao     = aceleracao
        self.sprite         = sprite
        tamanho = self.raio * 2
        self.sprite_red = pg.transform.scale(self.sprite, (tamanho, tamanho))
        self.rect = self.sprite_red.get_rect(center=(int(self.posicao.x), self.posicao.y))

    def desenhar(self, tela: pg.Surface) -> None:
        tela.blit(self.sprite_red, self.rect)


class Simulacao:
    def __init__(self):
        self.FRAMERATE      = 60
        self.VERDE          = (0, 255, 0)
        self.BRANCO         = (255, 255, 255)
        self.PRETO          = (0, 0, 0)
        self.VERMELHO       = (255, 0, 0)
        self.ROXO           = (75,  0, 130)
        self.CINZA          = (240, 240, 240)
        self.CINZA_ESCURO   = (170, 170, 170)

        self.dimensoes_tela = (1200, 800)

        pg.display.set_caption('Canhão de Newton')
        self.tela = pg.display.set_mode(self.dimensoes_tela)
        self.clock = pg.Clock()
        self.jogo_rodando = False

        self.qtd_projeteis_atuais = 0
        self.projeteis = []

        self.sprite_planeta     = pg.image.load('canhao_newton/img/terraDia.png').convert_alpha()
        self.sprite_projetil    = pg.image.load('canhao_newton/img/projetil.png').convert_alpha()
        self.planeta = Corpo(massa=100000,
                             posicao=vector(self.tela.get_width() // 2, self.tela.get_height() // 2),
                             raio=100,
                             velocidade=vector(0, 0),
                             aceleracao=vector(0, 0),
                             sprite=self.sprite_planeta)

        self.fundo = Fundo(self.dimensoes_tela)
    
    def adicionar_projetil(
            self,
            posicao         :vector,
            velocidade      :vector,
            aceleracao      :vector,
            massa           :float,
            raio            :float
        ) -> None:
            projetil = Corpo(massa=massa,
                             posicao=posicao,
                             velocidade=velocidade,
                             aceleracao=aceleracao,
                             raio=raio,
                             sprite=self.sprite_projetil)

            self.projeteis.append(projetil)
            self.qtd_projeteis_atuais += 1

    def desenhar_tudo(self):
        self.fundo.desenhar(self.tela)
        self.planeta.desenhar(self.tela)
        
        for projetil in self.projeteis:
            projetil.desenhar(self.tela)

    def event_loop(self):
        for evento in pg.event.get():
            if evento.type == pg.QUIT:
                self.jogo_rodando = False
            if evento.type == pg.KEYDOWN:
                if evento.key == pg.K_SPACE:
                    self.adicionar_projetil(massa=100000,
                                            posicao=vector(
                                                randint(0, self.dimensoes_tela[0] - 100), randint(0, self.dimensoes_tela[1] - 100)
                                            ),
                                            raio=10,
                                            velocidade=vector(0, 0),
                                            aceleracao=vector(0, 0))

    def run(self):
        last_time = time.time()
        self.jogo_rodando = True
        while self.jogo_rodando:
            delta_time = last_time - time.time()
            last_time = time.time()
            self.event_loop()
            self.desenhar_tudo()

            pg.display.flip()
            self.clock.tick(self.FRAMERATE)


def main():
    pg.init()
    simulacao = Simulacao()
    simulacao.run()

if __name__ == '__main__':
    main()
