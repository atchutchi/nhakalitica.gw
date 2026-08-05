# Auditoria da versão de produção

Data: 5 de Agosto de 2026

Estado: parte pública concluída. Área privada bloqueada por falta de uma credencial válida de membro aprovado.

## Âmbito verificado

- Página inicial em português, inglês e francês.
- Sobre nós.
- Tipos de adesão.
- Como funciona.
- Início de sessão e respectivo estado de erro.
- Estado de registos temporariamente encerrados.
- Termos de Utilização como amostra do padrão legal.
- Página inicial e navegação em telemóvel.
- Refluxo horizontal nas larguras testadas.

## Pontos fortes

- A arquitectura pública é clara e consistente.
- Sobre nós, Tipos de adesão e Como funciona apresentam boa hierarquia visual.
- O início de sessão tem campos identificados, recuperação de palavra-passe e mensagem de erro visível.
- O conteúdo mantém-se legível em português, inglês e francês.
- A versão móvel não apresenta deslocamento horizontal.
- O rodapé reorganizado mantém a hierarquia em desktop e telemóvel.

## Problemas prioritários

### 1. Mensagem de registos encerrados fora do primeiro ecrã

Ao abrir `/conta/criar/`, o visitante vê primeiro um painel azul quase vazio. O título, a explicação e a acção aparecem abaixo do painel, depois de uma deslocação vertical. O estado essencial deve aparecer imediatamente e não depois de uma área que parece sem conteúdo.

Prioridade: crítica para a demonstração.

Evidência: `06-registo.png` e `06b-registo-mensagem.png`.

### 2. Contraste insuficiente no cartão azul da página inicial

O título “Como funciona a adesão” usa azul escuro sobre fundo azul escuro. O problema repete-se em português, inglês e francês. O texto do título deve ser branco ou usar outro tom que cumpra o contraste AA.

Prioridade: alta.

Evidência: `01-home.png`, `10-home-english.png` e `11-home-francais.png`.

### 3. Estado do menu móvel pouco claro

Quando o menu está aberto, o botão mantém o nome acessível “Abrir menu”. Deve mudar para “Fechar menu”. O foco desloca-se para a primeira ligação, mas o contorno laranja não corresponde ao foco turquesa definido no design system.

Prioridade: média.

Evidência: `09-menu-mobile.png`.

## Limites da auditoria

A área privada, o directório, os perfis, os favoritos, as mensagens, as notificações e a administração não foram capturados porque a credencial de demonstração disponível no código de testes não corresponde à credencial configurada em produção. Não foram feitas tentativas adicionais.

As imagens permitem avaliar hierarquia, legibilidade, fluxo e riscos visíveis. Não provam conformidade integral com WCAG. Essa confirmação exige testes de teclado, nomes acessíveis, estados dinâmicos e contraste calculado.

## Evidência capturada

1. `01-home.png`
2. `02-sobre.png`
3. `03-tipos-adesao.png`
4. `04-como-funciona.png`
5. `05-login.png`
6. `06-registo.png`
7. `06b-registo-mensagem.png`
8. `07-termos.png`
9. `08-home-mobile.png`
10. `09-menu-mobile.png`
11. `10-home-english.png`
12. `11-home-francais.png`
