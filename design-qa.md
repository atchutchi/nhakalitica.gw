# Design QA

## Artefactos comparados

- Verdade visual do cabeçalho: `C:\Users\binta\AppData\Local\Temp\codex-clipboard-171f1432-fc34-4a06-afd9-a7a98c0efa50.png`
- Verdade visual da marca no hero: `C:\Users\binta\AppData\Local\Temp\codex-clipboard-3bc1d80d-5aa3-40cf-92dd-c3d13a8bd507.png`
- Implementação do cabeçalho: `C:\Users\binta\Documents\Nha Kalitica Networking Society\.playwright-cli\element-2026-07-26T20-59-52-077Z.png`
- Implementação do hero: `C:\Users\binta\Documents\Nha Kalitica Networking Society\.playwright-cli\element-2026-07-26T20-59-53-869Z.png`
- Implementação mobile: `C:\Users\binta\Documents\Nha Kalitica Networking Society\.playwright-cli\page-2026-07-26T20-58-57-485Z.png`
- URL testado: `http://127.0.0.1:8017/`

## Normalização

- Cabeçalho de referência: 1635 por 156 píxeis.
- Cabeçalho implementado: 1636 por 137 píxeis num viewport CSS de 1636 por 900, densidade 1.
- Referência do símbolo no hero: 687 por 457 píxeis. É um recorte isolado do lado visual do hero e não uma página completa.
- Hero implementado: 1636 por 597 píxeis num viewport CSS de 1636 por 900, densidade 1.
- Mobile implementado: 390 por 844 píxeis num viewport CSS de 390 por 844, densidade 1.
- A diferença de um píxel na largura do cabeçalho foi tratada como arredondamento do viewport. O hero foi comparado como região focada porque a referência não inclui texto nem a grelha completa.

## Estado e interacções verificadas

- Página pública sem autenticação em desktop e mobile.
- Cabeçalho completo, selector de idioma, navegação, botões e símbolo do hero.
- Menu mobile visível como controlo de 44 píxeis.
- Início de sessão com a conta de Atchutchi Ferreira.
- Redireccionamento para o painel aprovado.
- Abertura do perfil publicado com experiências, idiomas e currículo.
- Consola do browser sem erros ou avisos.

## Comparação visual

### Vista completa

A composição continua fiel ao sistema aprovado. A hierarquia tipográfica, a grelha de duas colunas, a paleta Kalitica, os controlos e a linha de confiança não sofreram alterações. O símbolo vegetal ganhou presença sem competir com o título. Em mobile o símbolo decorativo continua oculto para preservar a hierarquia e evitar deslocamento horizontal.

### Regiões focadas

O cabeçalho foi comparado no mesmo viewport aproximado da referência. O activo original é apresentado por inteiro, sem translação vertical nem recorte do topo. O símbolo do hero usa o mesmo ficheiro raster e mantém cores, proporção, nitidez e fundo branco. A escala aumentou sem esticar a imagem.

## Superfícies de fidelidade

- Tipografia: Outfit, pesos, espaçamento, quebra do título e hierarquia mantidos.
- Espaçamento e ritmo: altura do cabeçalho ajustada ao logótipo completo. O hero mantém separação clara entre texto, imagem e linha de confiança.
- Cores e tokens: não houve mudança de paleta. O verde azul, azul institucional e cores do símbolo coincidem com os activos existentes.
- Qualidade da imagem: o activo Kalitica original é usado no cabeçalho e no hero. Não existem substituições em SVG, CSS ou elementos desenhados por código.
- Conteúdo: texto, chamadas para acção, idiomas e regras de adesão mantidos.

## Histórico da iteração

### Comparação inicial

- P2 no cabeçalho: `overflow: hidden` e `translateY(-17px)` cortavam parte do activo.
- P2 no hero: a largura fixa de 520 píxeis deixava o símbolo com pouca presença visual.

### Correcções aplicadas

- O cabeçalho passou a usar altura automática, `overflow: visible` e `transform: none`.
- O contentor de navegação ganhou altura suficiente para mostrar o activo completo.
- O símbolo do hero passou para uma largura responsiva entre 680 e 760 píxeis.
- Os pontos de quebra do cabeçalho, menu e símbolo foram reajustados.

### Evidência posterior

- A captura do cabeçalho mostra folhas, palavra Kalitica e assinatura Networking Society sem corte.
- A captura do hero mostra o símbolo maior, proporcional e centrado.
- A captura mobile mostra o logótipo completo e sem deslocamento horizontal.
- O detector Impeccable devolveu zero ocorrências no âmbito de layout e zero ocorrências gerais nos ficheiros alterados.

## Findings

Não existem diferenças P0, P1 ou P2 accionáveis no âmbito pedido.

## Implementation Checklist

- [x] Corrigir o recorte do logótipo no cabeçalho.
- [x] Aumentar o símbolo no hero.
- [x] Validar desktop e mobile.
- [x] Confirmar início de sessão e perfil aprovado.
- [x] Confirmar consola sem erros.
- [x] Confirmar testes automatizados e detector visual.

final result: passed
