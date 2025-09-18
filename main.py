import pygame as pg
import time
from pygame import Vector2
import os
from typing import Optional

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
        self.caminho_sprite: str = caminho_sprite

        if convert_alpha:
            self.imagem_original: pg.Surface = pg.image.load(caminho_sprite).convert_alpha()
        else:
            self.imagem_original: pg.Surface = pg.image.load(caminho_sprite).convert()

        self.imagem: pg.Surface = pg.transform.scale(self.imagem_original, transform_scale)

        if topleft:
            self.rect: pg.Rect = self.imagem.get_rect(topleft=(x, y))
        else:
            self.rect: pg.Rect = self.imagem.get_rect(center=(x, y))

        self.x: int = x
        self.y: int = y
    
    def desenhar(self, tela: pg.Surface) -> None:
        tela.blit(self.imagem, self.rect)

class Corpo:
    def __init__(
        self,
        massa               :float,
        raio                :float,
        posicao             :Vector2,
        velocidade          :Vector2,
        aceleracao          :Vector2,
        sprite              :Optional[pg.Surface] = None
    ) -> None:
        self.massa: float           = massa
        self.raio: float            = raio
        self.posicao: Vector2       = posicao
        self.velocidade: Vector2    = velocidade
        self.aceleracao: Vector2    = aceleracao
        self.sprite: pg.Surface     = sprite
        self.diametro: float        = self.raio * 2
        self.sprite_red: pg.Surface = pg.transform.scale(self.sprite, (self.diametro, self.diametro))
        self.rect: pg.Rect          = self.sprite_red.get_rect(center=(int(self.posicao.x), self.posicao.y))

    def desenhar(self, tela: pg.Surface) -> None:
        self.rect.center = self.posicao
        tela.blit(self.sprite_red, self.rect)

class Simulacao:
    def __init__(self) -> None:
        self.FRAMERATE: int = 100

        self.ROXO_ESCURO: tuple[int, int, int]    = (75, 0, 130)
        self.VERDE: tuple[int, int, int]          = (0, 255, 0)
        self.fonte: pg.Font = pg.font.SysFont(None, 25)

        pg.display.set_caption('Canhão de Newton')
        self.dimensoes_tela: tuple[int, int] = (1600, 900)
        self.tela: pg.Surface = pg.display.set_mode(self.dimensoes_tela, pg.FULLSCREEN)
        self.clock = pg.Clock()
        self.jogo_rodando: bool = False

        self.projeteis: list[Corpo] = []
        self.CONSTANTE_GRAVITACIONAL: int = 100
        self.velocidade_inicial_projetil: int = 0

        BASE_DIR: str = os.path.dirname(os.path.abspath(__file__))

        IMG_DIR: str = os.path.join(BASE_DIR, 'img')

        self.caminho_planeta: str    = os.path.join(IMG_DIR, 'terraNoite.png')
        self.caminho_projetil: str   = os.path.join(IMG_DIR, 'projetil.png')
        self.caminho_torre: str      = os.path.join(IMG_DIR, 'torre.png')
        self.caminho_canhao: str     = os.path.join(IMG_DIR, 'canhao.png')
        self.caminho_fundo: str      = os.path.join(IMG_DIR, 'ceu.png')

        self.sprite_planeta: str     = pg.image.load(self.caminho_planeta).convert_alpha()
        self.sprite_projetil: str    = pg.image.load(self.caminho_projetil).convert_alpha()

        x_planeta: int = self.tela.get_width() // 2
        y_planeta: int = self.tela.get_height() // 2

        self.planeta: Corpo = Corpo(
            massa=100_000,
            posicao=Vector2(x_planeta, y_planeta),
            raio=250,
            velocidade=Vector2(0, 0),
            aceleracao=Vector2(0, 0),
            sprite=self.sprite_planeta
        )
        
        self.fundo: Sprite = Sprite(
            caminho_sprite=self.caminho_fundo,
            transform_scale=self.dimensoes_tela,
            convert_alpha=True,
            x=0,
            y=0,
            topleft=True
        )

        self.torre: Sprite = Sprite(
            caminho_sprite=self.caminho_torre,
            transform_scale=(250, 250),
            convert_alpha=True,
            x=self.planeta.posicao.x,
            y=self.planeta.posicao.y - self.planeta.raio,
            topleft=False
        )

        x_canhao: int = self.planeta.posicao.x - 10
        y_canhao: int = self.planeta.posicao.y - self.planeta.raio - 30

        self.canhao: Sprite = Sprite(
            caminho_sprite=self.caminho_canhao,
            transform_scale=(40, 40),
            convert_alpha=True,
            x=x_canhao,
            y=y_canhao,
            topleft=False
        )
    
    def atualizar_projeteis(self, dt: float) -> None:
        x_planeta: int          = self.planeta.posicao.x
        y_planeta: int          = self.planeta.posicao.y
        massa_planeta: float    = self.planeta.massa
        if self.projeteis:
            for projetil in self.projeteis:
                x_projetil: int         = projetil.posicao.x
                y_projetil: int         = projetil.posicao.y
                massa_projetil: float   = projetil.massa
                
                distancia: int = (self.planeta.posicao - projetil.posicao).length()

                if distancia < 1:
                    distancia = 1

                produto_massas      = massa_planeta * massa_projetil
                produto_distancia   = distancia * distancia

                forca_gravitacional = self.CONSTANTE_GRAVITACIONAL * produto_massas / produto_distancia

                cosseno = (x_planeta - x_projetil) / distancia
                seno    = (y_planeta - y_projetil) / distancia

                forca   = Vector2()
                forca.x = forca_gravitacional * cosseno
                forca.y = forca_gravitacional * seno

                projetil.aceleracao.x = forca.x / massa_projetil
                projetil.aceleracao.y = forca.y / massa_projetil

                projetil.velocidade   += projetil.aceleracao * dt
                projetil.posicao      += projetil.velocidade * dt

                distancia = (self.planeta.posicao - projetil.posicao).length()
                if distancia < (self.planeta.raio + projetil.raio) * 0.98:
                    projetil.posicao = Vector2(x_projetil, y_projetil)
                    projetil.aceleracao.x = 0
                    projetil.aceleracao.y = 0
                    projetil.velocidade.x = 0
                    projetil.velocidade.y = 0

    def adicionar_projetil(
        self,
        posicao         :Vector2,
        velocidade      :Vector2,
        aceleracao      :Vector2,
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
        self.velocidade_inicial_projetil += 5

    def desenhar_tudo(self) -> None:
        self.fundo.desenhar(self.tela)
        self.planeta.desenhar(self.tela)
        self.torre.desenhar(self.tela)
        self.canhao.desenhar(self.tela)
        
        for projetil in self.projeteis:
            projetil.desenhar(self.tela)
    
    def escrever_textos(self) -> None:
        self.escrever_texto(
            info=f'Projetil Atual: {len(self.projeteis)}',
            x=10,
            y=10
        )
        if self.projeteis:
            posicao_str_x = int(self.projeteis[len(self.projeteis) - 1].posicao.x)
            posicao_str_y = int(self.projeteis[len(self.projeteis) - 1].posicao.y)
            self.escrever_texto(
                info=f'Posição:     ({posicao_str_x:^5},{posicao_str_y:^5})',
                x=10,
                y=30
            )
            velocidade_str_x = int(self.projeteis[len(self.projeteis) - 1].velocidade.x)
            velocidade_str_y = int(self.projeteis[len(self.projeteis) - 1].velocidade.y)
            self.escrever_texto(
                info=f'Velocidade:  ({velocidade_str_x:^5},{velocidade_str_y:^5})',
                x=10,
                y=50
            )
            aceleracao_str_x = int(self.projeteis[len(self.projeteis) - 1].aceleracao.x)
            aceleracao_str_y = int(self.projeteis[len(self.projeteis) - 1].aceleracao.y)
            self.escrever_texto(
                info=f'Aceleração:  ({aceleracao_str_x:^5},{aceleracao_str_y:^5})',
                x=10,
                y=70
            )
            massa_projetil_atual = int(self.projeteis[len(self.projeteis) - 1].massa)
            self.escrever_texto(
                info=f'Massa do projétil: {massa_projetil_atual}',
                x=10,
                y=90
            )
            self.escrever_texto(
                info=f'Massa do planeta: {int(self.planeta.massa)}',
                x=10,
                y=110
            )

    def event_loop(self) -> None:
        for evento in pg.event.get():
            if evento.type == pg.QUIT:
                self.jogo_rodando = False
            if evento.type == pg.KEYDOWN:
                if evento.key == pg.K_SPACE:
                    x = self.planeta.posicao.x + 10
                    y = self.planeta.posicao.y - self.planeta.raio - 35
                    self.adicionar_projetil(
                        massa=300,
                        posicao=Vector2(x, y),
                        raio=6,
                        velocidade=Vector2(self.velocidade_inicial_projetil, 0),
                        aceleracao=Vector2(0, 0)
                    )

    def run(self) -> None:
        last_time = time.time()
        self.jogo_rodando = True
        while self.jogo_rodando:
            current_time = time.time()
            delta_time = current_time - last_time
            last_time = current_time
            self.event_loop()
            self.atualizar_projeteis(delta_time)
            self.desenhar_tudo()
            self.escrever_textos()

            pg.display.flip()
            self.clock.tick(self.FRAMERATE)
    
    def escrever_texto(self, info: str, x: int, y: int):
        superficie_texto = self.fonte.render(str(info), True, self.VERDE)
        retangulo_texto = superficie_texto.get_rect(topleft=(x, y))
        pg.draw.rect(self.tela, 'Black', retangulo_texto)
        self.tela.blit(superficie_texto, retangulo_texto)

def main() -> None:
    pg.init()
    simulacao = Simulacao()
    simulacao.run()
    pg.quit()

if __name__ == '__main__':
    main()
