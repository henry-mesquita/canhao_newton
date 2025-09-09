import pygame as pg
import time
from pygame import Vector2 as vector
from random import randint

class Fundo:
    def __init__(self, dimensoes_tela):
        imagem_original = pg.image.load('canhao_newton/img/ceu.png').convert_alpha()

        self.imagem = pg.transform.scale(imagem_original, dimensoes_tela)

        self.rect = self.imagem.get_rect(topleft=(0, 0))
    
    def desenhar(self, tela):
        tela.blit(self.imagem, self.rect)

class Canhao:
    def __init__(self, dimensoes_tela, x, y):
        imagem_original = pg.image.load('canhao_newton/img/canhao.png').convert_alpha()
        
        self.imagem = pg.transform.scale(imagem_original, (60, 60))
        
        self.rect = self.imagem.get_rect(center=(x, y))
    
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
        self.rect.center = self.posicao
        tela.blit(self.sprite_red, self.rect)


class Simulacao:
    def __init__(self):
        self.FRAMERATE                  = 30
        self.VERDE                      = (0, 255, 0)
        self.BRANCO                     = (255, 255, 255)
        self.PRETO                      = (0, 0, 0)
        self.VERMELHO                   = (255, 0, 0)
        self.ROXO                       = (75,  0, 130)
        self.CINZA                      = (240, 240, 240)
        self.CINZA_ESCURO               = (170, 170, 170)

        self.dimensoes_tela             = (1400, 800)
        self.CONSTANTE_GRAVITACIONAL    = 0.5

        pg.display.set_caption('Canhão de Newton')
        self.tela = pg.display.set_mode(self.dimensoes_tela)
        self.clock = pg.Clock()
        self.jogo_rodando = False

        self.projeteis = []

        self.sprite_planeta     = pg.image.load('canhao_newton/img/terraNoite.png').convert_alpha()
        self.sprite_projetil    = pg.image.load('canhao_newton/img/projetil.png').convert_alpha()
        self.fundo = Fundo(self.dimensoes_tela)
        self.planeta = Corpo(massa=90_000,
                             posicao=vector(self.tela.get_width() // 2, self.tela.get_height() // 2),
                             raio=200,
                             velocidade=vector(0, 0),
                             aceleracao=vector(0, 0),
                             sprite=self.sprite_planeta)
        
        x_canhao = self.planeta.posicao.x - 20
        y_canhao = self.planeta.posicao.y - self.planeta.raio - 5
        self.canhao = Canhao(self.dimensoes_tela, x_canhao, y_canhao)

        self.velocidade_inicial = 0

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
            self.velocidade_inicial += 0.5
    
    def atualizar_projeteis(self):
        x_planeta       = self.planeta.posicao.x
        y_planeta       = self.planeta.posicao.y
        massa_planeta   = self.planeta.massa
        if self.projeteis:
            for projetil in self.projeteis:
                x_projetil      = projetil.posicao.x
                y_projetil      = projetil.posicao.y
                massa_projetil  = projetil.massa
                
                distancia = (self.planeta.posicao - projetil.posicao).length()

                if distancia < 1:
                    distancia = 1

                forca_gravitacional = self.CONSTANTE_GRAVITACIONAL * massa_planeta * massa_projetil / (distancia**2)

                cosseno = (x_planeta - x_projetil) / distancia
                seno    = (y_planeta - y_projetil) / distancia

                forca   = vector()
                forca.x = forca_gravitacional * cosseno
                forca.y = forca_gravitacional * seno

                projetil.aceleracao.x = forca.x / massa_projetil
                projetil.aceleracao.y = forca.y / massa_projetil

                projetil.velocidade   += projetil.aceleracao
                projetil.posicao      += projetil.velocidade

                distancia = (self.planeta.posicao - projetil.posicao).length()
                if distancia < self.planeta.raio + projetil.raio:
                    projetil.posicao = vector(x_projetil, y_projetil)
                    projetil.aceleracao.x = 0
                    projetil.aceleracao.y = 0
                    projetil.velocidade.x = 0
                    projetil.velocidade.y = 0

    def desenhar_tudo(self):
        self.fundo.desenhar(self.tela)
        self.planeta.desenhar(self.tela)
        self.canhao.desenhar(self.tela)
        
        for projetil in self.projeteis:
            projetil.desenhar(self.tela)

    def event_loop(self):
        for evento in pg.event.get():
            if evento.type == pg.QUIT:
                self.jogo_rodando = False
            if evento.type == pg.KEYDOWN:
                if evento.key == pg.K_SPACE:
                    x = self.planeta.posicao.x + 20
                    y = self.planeta.posicao.y - self.planeta.raio - 20
                    self.adicionar_projetil(massa=1,
                                            posicao=vector(x, y),
                                            raio=5,
                                            velocidade=vector(self.velocidade_inicial, 0),
                                            aceleracao=vector(0, -0.05))

    def run(self):
        self.jogo_rodando = True
        while self.jogo_rodando:
            self.event_loop()
            self.atualizar_projeteis()
            self.desenhar_tudo()

            pg.display.flip()
            self.clock.tick(self.FRAMERATE)

def main():
    pg.init()
    simulacao = Simulacao()
    simulacao.run()

if __name__ == '__main__':
    main()
