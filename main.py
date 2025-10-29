import pygame as pg
import time
from pygame import Vector2
import os
from typing import Optional
from dataclasses import dataclass

class Sprite:
    def __init__(
        self,
        caminho_sprite:     str,
        transform_scale:    tuple[int, int],
        x:                  int,
        y:                  int,
        convert_alpha:      bool
    ) -> None:
        """
        Inicializa a classe Sprite

        Args:
            caminho_sprite (str): O caminho da imagem que será desenhada.
            transform_scale (tuple[int, int]): As dimensões que serão redefinidas.
            x (int): Coordenada X de onde o Sprite deverá ser desenhado.
            y (int): Coordenada Y de onde o Sprite deverá ser desenhado.
            convert_alpha (bool): Deverá ser True caso a imagem não tiver fundo.
        Returns:
            None
        """
        self.caminho_sprite: str = caminho_sprite

        # CONVERT_ALPHA SE FOR IMAGEM SEM FUNDO
        if convert_alpha:
            self.imagem_original: pg.Surface = pg.image.load(caminho_sprite).convert_alpha()
        else:
            self.imagem_original: pg.Surface = pg.image.load(caminho_sprite).convert()

        # REDIMENSIONA A IMAGEM
        self.imagem: pg.Surface = pg.transform.scale(self.imagem_original, transform_scale)

        self.rect: pg.Rect = self.imagem.get_rect(center=(x, y))
        self.posicao: Vector2 = Vector2(x, y)
    
    def desenhar(self, tela: pg.Surface, posicao_final: Vector2) -> None:
        """
        Desenha o sprite na tela.

        Args:
            tela (pg.Surface): Superfície na qual será desenhado o Sprite.
        Returns:
            None
        """
        self.rect.center = posicao_final        
        tela.blit(self.imagem, self.rect)

class Corpo:
    def __init__(
        self,
        massa:              float,
        raio:               float,
        posicao:            Vector2,
        velocidade:         Vector2,
        aceleracao:         Vector2,
        sprite:             Optional[pg.Surface] = None
    ) -> None:
        """
        Inicializa a classe Corpo.

        Args:
            massa (float): Massa do corpo.
            raio (float): Raio do corpo.
            posicao (Vector2): Posição inicial do Corpo.
            velocidade (Vector2): Velocidade inicial do Corpo.
            aceleracao (Vector2): Aceleração inicial do Corpo.
            sprite (Optional[pg.Surface]): Sprite do corpo.
        Returns:
            None
        """
        self.massa: float           = massa
        self.raio: float            = raio
        self.posicao: Vector2       = posicao
        self.velocidade: Vector2    = velocidade
        self.aceleracao: Vector2    = aceleracao
        self.sprite: pg.Surface     = sprite
        self.diametro: float        = self.raio * 2
        self.sprite_red: pg.Surface = pg.transform.scale(self.sprite, (self.diametro, self.diametro))
        self.rect: pg.Rect          = self.sprite_red.get_rect(center=self.posicao)

    def desenhar(self, tela: pg.Surface, posicao_final: Vector2) -> None:
        """
        Desenha o corpo na tela.

        Args:
            tela (pg.Surface): Superfície na qual será desenhado o Corpo.
        Returns:
            None
        """
        self.rect.center = posicao_final
        tela.blit(self.sprite_red, self.rect)

@dataclass
class Camera:
    posicao:        Vector2
    velocidade:     int

class Simulacao:
    def __init__(self) -> None:
        """
        Inicializa a classe Simulacao.

        Returns:
            None
        """
        # CORES
        self.ROXO_ESCURO: tuple[int, int, int]    = (75, 0, 130)
        self.VERDE: tuple[int, int, int]          = (0, 255, 0)

        # ATRIBUTOS DA SIMULACAO
        self.CONSTANTE_GRAVITACIONAL: int = 100
        self.FRAMERATE: int = 100
        self.DIMENSOES_TELA: tuple[int, int] = (1600, 900)
        self.fonte: pg.Font = pg.font.SysFont(None, 25)
        self.tela: pg.Surface = pg.display.set_mode(self.DIMENSOES_TELA, pg.FULLSCREEN)
        self.clock = pg.time.Clock()
        self.jogo_rodando: bool = False
        pg.display.set_caption('Canhão de Newton')

        self.projeteis: list[Corpo]             = []
        self.rastro: list[Vector2]              = []
        self.velocidade_inicial_projetil: int   = 0

        BASE_DIR: str = os.path.dirname(os.path.abspath(__file__))
        IMG_DIR: str = os.path.join(BASE_DIR, 'img')

        # CAMINHO RELATIVO DAS IMAGENS QUE NAO TEM FISICA
        self.caminho_planeta: str    = os.path.join(IMG_DIR, 'terraNoite.png')
        self.caminho_projetil: str   = os.path.join(IMG_DIR, 'esfera.png')
        self.caminho_torre: str      = os.path.join(IMG_DIR, 'torre.png')
        self.caminho_canhao: str     = os.path.join(IMG_DIR, 'canhao.png')
        self.caminho_fundo: str      = os.path.join(IMG_DIR, 'ceu.png')
        

        # CARREGA OS SPRITES DOS CORPOS DA SIMULACAO
        self.sprite_planeta: str     = pg.image.load(self.caminho_planeta).convert_alpha()
        self.sprite_projetil: str    = pg.image.load(self.caminho_projetil).convert_alpha()

        # ALTERA O ICONE DA JANELA
        pg.display.set_icon(self.sprite_planeta)
        
        x_camera = self.DIMENSOES_TELA[0] // 2
        y_camera = self.DIMENSOES_TELA[1] // 2

        # CRIA UM OBJETO PARA A CAMERA
        self.camera = Camera(
            posicao=Vector2(x_camera, y_camera),
            velocidade=5,
        )

        x_planeta: int = self.tela.get_width() // 2
        y_planeta: int = self.tela.get_height() // 2

        # CRIA UM OBJETO PARA O PLANETA
        self.planeta: Corpo = Corpo(
            massa=100_000,
            posicao=Vector2(x_planeta, y_planeta),
            raio=250,
            velocidade=Vector2(0, 0),
            aceleracao=Vector2(0, 0),
            sprite=self.sprite_planeta
        )
        
        # CRIA UM OBJETO PARA O FUNDO
        self.fundo: Sprite = Sprite(
            caminho_sprite=self.caminho_fundo,
            transform_scale=self.DIMENSOES_TELA,
            convert_alpha=True,
            x=self.DIMENSOES_TELA[0] // 2,
            y=self.DIMENSOES_TELA[1] // 2
        )

        # CRIA UM OBJETO PARA A TORRE
        self.torre: Sprite = Sprite(
            caminho_sprite=self.caminho_torre,
            transform_scale=(250, 250),
            convert_alpha=True,
            x=self.planeta.posicao.x,
            y=self.planeta.posicao.y - self.planeta.raio
        )

        x_canhao: int = self.planeta.posicao.x - 10
        y_canhao: int = self.planeta.posicao.y - self.planeta.raio - 30

        # CRIA UM OBJETO PARA O CANHAO
        self.canhao: Sprite = Sprite(
            caminho_sprite=self.caminho_canhao,
            transform_scale=(40, 40),
            convert_alpha=True,
            x=x_canhao,
            y=y_canhao
        )

    def calcular_posicao_sprite(
            self,
            pos_sprite:     Vector2,
            pos_camera:     Vector2,
            resolucao_tela: tuple[int, int]
    ) -> Vector2:
        """
        Desenha o corpo na tela.

        Args:
            pos_sprite (Vector2): Posição antiga do sprite.
            pos_camera (Vector2): Posição atual da câmera.
            resolucao_tela (tuple[int, int]): Resolução da tela.
        Returns:
            Vector2(x_tela, y_tela): As coordenadas redefinidas de acordo com a câmera.
        """
        x_sprite: int           = pos_sprite.x
        y_sprite: int           = pos_sprite.y
        x_camera: int           = pos_camera.x
        y_camera: int           = pos_camera.y
        largura_tela: int       = resolucao_tela[0]
        altura_tela: int        = resolucao_tela[1]

        x_tela: int = (x_sprite - x_camera) + largura_tela // 2
        y_tela: int = (y_sprite - y_camera) + altura_tela // 2

        return Vector2(x_tela, y_tela)
    
    def atualizar_projeteis(self, dt: float) -> None:
        """
        Realiza os cálculos físicos e atualiza os projéteis a cada frame da simulação.

        Args:
            dt (float): Delta time
        Returns:
            None
        """
        x_planeta       = self.planeta.posicao.x
        y_planeta       = self.planeta.posicao.y
        massa_planeta   = self.planeta.massa
        if self.projeteis:
            for i, projetil in enumerate(self.projeteis):
                x_projetil          = projetil.posicao.x
                y_projetil          = projetil.posicao.y
                massa_projetil      = projetil.massa

                distancia = (self.planeta.posicao - projetil.posicao).length()

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
                
                if i == len(self.projeteis) - 1:
                    self.rastro.append(projetil.posicao.copy())

    def adicionar_projetil(
        self,
        posicao:        Vector2,
        velocidade:     Vector2,
        aceleracao:     Vector2,
        massa:          float,
        raio:           float
    ) -> None:
        """
        Adicina um projetil a lista de projeteis.

        Args:
            posicao (Vector2): Posição onde o projetil será desenhado.
            velocidade (Vector2): Velocidade inicial do projetil.
            aceleracao (Vector2): Aceleração inicial do projetil.
            massa (float): Massa do projetil.
            raio (float): Raio do projetil.
        Returns:
            None
        """
        projetil = Corpo(
            massa=massa,
            posicao=posicao,
            velocidade=velocidade,
            aceleracao=aceleracao,
            raio=raio,
            sprite=self.sprite_projetil
        )

        self.rastro.clear()
        self.projeteis.append(projetil)
        self.velocidade_inicial_projetil += 5
    
    def desenhar_rastro(self):
        """
        Desenha o rastro do ultimo projetil lançado.

        Returns:
            None
        """
        if self.projeteis:
            ultimo_projetil: Corpo = self.projeteis[-1]

            for posicao in self.rastro:
                posicao_final = self.calcular_posicao_sprite(
                    pos_sprite=posicao,
                    pos_camera=self.camera.posicao,
                    resolucao_tela=((self.tela.get_width(), self.tela.get_height()))
                )

                center = posicao_final
                pg.draw.circle(center=center,
                               color=self.ROXO_ESCURO,
                               radius=ultimo_projetil.raio // 2,
                               width=2,
                               surface=self.tela)
    
    def desenhar_tudo(self) -> None:
        """
        Desenha tudo na tela.

        Returns:
            None
        """
        x_fundo: int = self.DIMENSOES_TELA[0] // 2
        y_fundo: int = self.DIMENSOES_TELA[1] // 2

        resolucao_tela: tuple[int, int]     = (self.tela.get_width(), self.tela.get_height())
        posicao_camera: Vector2             = self.camera.posicao

        self.fundo.desenhar(
            tela=self.tela,
            posicao_final=Vector2(x_fundo, y_fundo)
        )

        posicao_final_planeta = self.calcular_posicao_sprite(
            pos_sprite=(self.planeta.posicao),
            pos_camera=posicao_camera,
            resolucao_tela=resolucao_tela
        )

        self.planeta.desenhar(self.tela, posicao_final_planeta)

        self.desenhar_rastro()
        
        posicao_final_torre = self.calcular_posicao_sprite(
            pos_sprite=self.torre.posicao,
            pos_camera=posicao_camera,
            resolucao_tela=resolucao_tela
        )
        
        self.torre.desenhar(self.tela, posicao_final_torre)

        posicao_final_canhao = self.calcular_posicao_sprite(
            pos_sprite=self.canhao.posicao,
            pos_camera=posicao_camera,
            resolucao_tela=resolucao_tela
        )

        self.canhao.desenhar(self.tela, posicao_final_canhao)
        
        for projetil in self.projeteis:
            posicao_final_projetil = self.calcular_posicao_sprite(
                pos_sprite=(projetil.posicao),
                pos_camera=posicao_camera,
                resolucao_tela=resolucao_tela
            )
            projetil.desenhar(self.tela, posicao_final_projetil)
    
    def escrever_textos(self) -> None:
        """
        Escreve todas as informações na tela.

        Returns:
            None
        """
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
        """
        Verifica quais teclas foram apertadas e realiza ações de acordo com elas.

        Returns:
            None
        """
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
            
        keys = pg.key.get_pressed()
        if keys[pg.K_w]:
            self.camera.posicao.y -= self.camera.velocidade
        if keys[pg.K_d]:
            self.camera.posicao.x += self.camera.velocidade
        if keys[pg.K_s]:
            self.camera.posicao.y += self.camera.velocidade
        if keys[pg.K_a]:
            self.camera.posicao.x -= self.camera.velocidade

    def run(self) -> None:
        """
        Game Loop da simulação.

        Returns:
            None
        """
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
        """
        Escreve um texto na tela.

        Args:
            info (str): String que será escrita na tela.
            x (int): Coordenada X do texto.
            y (int): Coordenada Y do texto.
        """
        superficie_texto = self.fonte.render(str(info), True, self.VERDE)
        retangulo_texto = superficie_texto.get_rect(topleft=(x, y))
        pg.draw.rect(self.tela, 'Black', retangulo_texto)
        self.tela.blit(superficie_texto, retangulo_texto)

def main() -> None:
    """
    Função principal que roda a simulação.

    Returns:
        None
    """
    pg.init()
    simulacao = Simulacao()
    simulacao.run()
    pg.quit()

if __name__ == '__main__':
    main()
