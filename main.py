import pygame as pg
import time
from pygame import Vector2 as vector

class Sprite:
    def __init__(
        self,
        caminho_sprite      :str,
        transform_scale     :tuple[int, int],
        x                   :int,
        y                   :int,
        convert_alpha       :bool,
        topleft             :bool
    ) -> None:
        self.caminho_sprite = caminho_sprite

        if convert_alpha:
            self.imagem_original = pg.image.load(caminho_sprite).convert_alpha()
        else:
            self.imagem_original = pg.image.load(caminho_sprite).convert()

        self.imagem = pg.transform.scale(self.imagem_original, transform_scale)

        if topleft:
            self.rect = self.imagem.get_rect(topleft=(x, y))
        else:
            self.rect = self.imagem.get_rect(center=(x, y))

        self.x = x
        self.y = y
    
    def desenhar(self, tela: pg.Surface) -> None:
        tela.blit(self.imagem, self.rect)

class Corpo:
    def __init__(
        self,
        massa               :float,
        raio                :float,
        posicao             :vector,
        velocidade          :vector,
        aceleracao          :vector,
        sprite              :pg.Surface = None
    ) -> None:
        self.massa          = massa
        self.raio           = raio
        self.posicao        = posicao
        self.velocidade     = velocidade
        self.aceleracao     = aceleracao
        self.sprite         = sprite
        self.diametro       = self.raio * 2
        self.sprite_red     = pg.transform.scale(self.sprite, (self.diametro, self.diametro))
        self.rect           = self.sprite_red.get_rect(center=(int(self.posicao.x), self.posicao.y))

    def desenhar(self, tela: pg.Surface) -> None:
        self.rect.center = self.posicao
        tela.blit(self.sprite_red, self.rect)

class Simulacao:
    def __init__(self) -> None:
        self.FRAMERATE = 60

        pg.display.set_caption('Canhão de Newton')
        self.dimensoes_tela = (1600, 900)
        self.tela = pg.display.set_mode(self.dimensoes_tela, pg.FULLSCREEN)
        self.clock = pg.Clock()
        self.jogo_rodando = False

        self.projeteis = []
        self.CONSTANTE_GRAVITACIONAL = 2
        self.velocidade_inicial_projetil = 0

        self.sprite_planeta     = pg.image.load('canhao_newton/img/terraNoite.png').convert_alpha()
        self.sprite_projetil    = pg.image.load('canhao_newton/img/projetil.png').convert_alpha()

        x_planeta = self.tela.get_width() // 2
        y_planeta = self.tela.get_height() // 2

        self.planeta = Corpo(
            massa=90_000,
            posicao=vector(x_planeta, y_planeta),
            raio=250,
            velocidade=vector(0, 0),
            aceleracao=vector(0, 0),
            sprite=self.sprite_planeta
        )
        
        self.fundo = Sprite(
            caminho_sprite='canhao_newton/img/ceu.png',
            transform_scale=self.dimensoes_tela,
            convert_alpha=True,
            x=0,
            y=0,
            topleft=True
        )

        self.torre = Sprite(
            caminho_sprite='canhao_newton/img/torre.png',
            transform_scale=(250, 250),
            convert_alpha=True,
            x=self.planeta.posicao.x,
            y=self.planeta.posicao.y - self.planeta.raio,
            topleft=False
        )

        x_canhao = self.planeta.posicao.x - 10
        y_canhao = self.planeta.posicao.y - self.planeta.raio - 30

        self.canhao = Sprite(
            caminho_sprite='canhao_newton/img/canhao.png',
            transform_scale=(40, 40),
            convert_alpha=True,
            x=x_canhao,
            y=y_canhao,
            topleft=False
        )
    
    def atualizar_projeteis(self) -> None:
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

                produto_massas      = massa_planeta * massa_projetil
                produto_distancia   = distancia * distancia

                forca_gravitacional = self.CONSTANTE_GRAVITACIONAL * produto_massas / produto_distancia

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
                if distancia < (self.planeta.raio + projetil.raio) * 0.98:
                    projetil.posicao = vector(x_projetil, y_projetil)
                    projetil.aceleracao.x = 0
                    projetil.aceleracao.y = 0
                    projetil.velocidade.x = 0
                    projetil.velocidade.y = 0

    def desenhar_tudo(self) -> None:
        self.fundo.desenhar(self.tela)
        self.planeta.desenhar(self.tela)
        self.torre.desenhar(self.tela)
        self.canhao.desenhar(self.tela)
        
        for projetil in self.projeteis:
            projetil.desenhar(self.tela)

    def event_loop(self) -> None:
        for evento in pg.event.get():
            if evento.type == pg.QUIT:
                self.jogo_rodando = False
            if evento.type == pg.KEYDOWN:
                if evento.key == pg.K_SPACE:
                    x = self.planeta.posicao.x + 10
                    y = self.planeta.posicao.y - self.planeta.raio - 35
                    self.adicionar_projetil(
                        massa=50,
                        posicao=vector(x, y),
                        raio=4,
                        velocidade=vector(self.velocidade_inicial_projetil, 0),
                        aceleracao=vector(0, -0.05)
                    )
    def adicionar_projetil(
            self,
            posicao         :vector,
            velocidade      :vector,
            aceleracao      :vector,
            massa           :float,
            raio            :float
        ) -> None:
            projetil = Corpo(
                massa=massa,
                posicao=posicao,
                velocidade=velocidade,
                aceleracao=aceleracao,
                raio=raio,
                sprite=self.sprite_projetil
            )

            self.projeteis.append(projetil)
            self.velocidade_inicial_projetil += 0.5

    def run(self) -> None:
        self.jogo_rodando = True
        while self.jogo_rodando:
            self.event_loop()
            self.atualizar_projeteis()
            self.desenhar_tudo()

            pg.display.flip()
            self.clock.tick(self.FRAMERATE)

def main() -> None:
    pg.init()
    simulacao = Simulacao()
    simulacao.run()
    pg.quit()

if __name__ == '__main__':
    main()
