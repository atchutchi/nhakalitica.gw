# Redesenho do rodapé público

## Objectivo

Reorganizar o rodapé público da Kalitica para criar uma hierarquia institucional clara, reduzir o peso visual do logótipo e garantir uma apresentação estável em desktop, tablet e telemóvel.

## Composição aprovada

O rodapé usa uma grelha de três áreas em desktop:

1. Marca: logótipo compacto e descrição institucional curta.
2. Informação: Termos, Privacidade e Código de Conduta numa lista vertical com título visível.
3. Contacto e idioma: endereço de email e selector de português, francês e inglês.

Uma linha inferior separada contém os direitos reservados. Em tablet, a marca ocupa a primeira linha e os dois grupos de utilidade dividem a segunda. Em telemóvel, todos os grupos ficam empilhados.

## Hierarquia e espaçamento

O logótipo mantém a identificação da marca sem dominar o rodapé. Os títulos de grupo distinguem informação legal, contacto e idiomas. O espaçamento usa apenas os tokens de 4, 8, 16, 24, 32 e 48 píxeis definidos no projecto.

## Acessibilidade

As ligações e os botões de idioma têm foco visível, área interactiva adequada e contraste AA. O idioma activo possui indicação visual e `aria-current`. Os títulos visíveis complementam os nomes acessíveis das navegações.

## Critérios de aceitação

- A estrutura apresenta três áreas distintas em ecrãs largos.
- O logótipo deixa de aparecer dentro de um bloco branco dominante.
- As ligações legais aparecem numa lista vertical sob um título visível.
- O contacto e os idiomas formam um grupo próprio.
- O rodapé muda de estrutura em tablet antes de o conteúdo ficar comprimido.
- O telemóvel não apresenta deslocamento horizontal.
- Os testes confirmam a presença dos títulos, das ligações e dos formulários de idioma.
