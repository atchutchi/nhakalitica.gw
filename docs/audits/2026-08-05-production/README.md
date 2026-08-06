# Auditoria da versão de produção

Data: 5 de Agosto de 2026

Estado: área pública e experiência de membro aprovado concluídas. Administração pendente de uma sessão de staff.

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
- Painel do membro em desktop e telemóvel.
- Directório, filtros e resultados.
- Perfil de outro membro e respectivas acções privadas.
- Áreas profissionais.
- Favoritos, mensagens e notificações nos estados vazios.
- Menu da conta e navegação privada móvel.
- Perfil próprio, edição do perfil e definições da conta.
- Fluxo de desactivação com retenção de 30 dias.
- Bloqueio do acesso administrativo para um membro sem privilégios.

## Pontos fortes

- A arquitectura pública é clara e consistente.
- Sobre nós, Tipos de adesão e Como funciona apresentam boa hierarquia visual.
- O início de sessão tem campos identificados, recuperação de palavra-passe e mensagem de erro visível.
- O conteúdo mantém-se legível em português, inglês e francês.
- A versão móvel não apresenta deslocamento horizontal.
- O rodapé reorganizado mantém a hierarquia em desktop e telemóvel.
- O directório organiza bem os filtros e os resultados nas larguras testadas.
- Os perfis explicam de forma clara quando os contactos e documentos podem ser partilhados.
- O menu da conta apresenta perfil, conta, segurança e saída de forma compreensível.
- A desactivação explica a consequência imediata, o prazo de recuperação e a retenção legal.
- Um membro comum recebe correctamente uma resposta 403 ao tentar abrir a administração.

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

### 4. Estado contraditório do perfil próprio

O painel informa que o perfil está visível na rede e o directório inclui o próprio membro nos resultados. Contudo, a pré-visualização afirma que o perfil ainda não aparece na pesquisa. O texto transmite um estado falso e pode levar o membro a procurar uma acção que não é necessária.

Prioridade: alta.

Evidência: `12-painel-membro.png`, `13-directorio.png` e `20-meu-perfil.png`.

### 5. Navegação de definições marca sempre “A minha conta”

Ao editar o perfil, “A minha conta” continua visualmente seleccionada. A navegação também cria uma barra de deslocamento horizontal permanente na largura intermédia e deixa a opção activa parcialmente cortada.

Prioridade: alta.

Evidência: `21-editar-perfil.png` e `22-editar-conta.png`.

### 6. Página de mensagens inconsistente e pouco orientadora

O estado vazio apresenta dois cartões grandes sem acção para procurar membros. O rótulo laranja não pertence à paleta funcional definida e a página tem mais sombra e espaço vazio do que os restantes ecrãs privados.

Prioridade: média.

Evidência: `17-mensagens.png`.

### 7. Comparação disponível sem favoritos

“Comparar membros” permanece com aparência activa quando a lista está vazia. Deve ficar desactivado com explicação ou não aparecer até existir um número suficiente de membros.

Prioridade: média.

Evidência: `16-favoritos.png`.

### 8. Acesso negado sem recuperação

O bloqueio administrativo está correcto, mas devolve uma página técnica “403 Forbidden” sem marca Kalitica, explicação em português ou ligação para regressar ao painel.

Prioridade: média.

Evidência: `24-admin-bloqueado.png`.

### 9. Estado do menu privado móvel pouco claro

Tal como no menu público, o botão mantém o nome acessível “Abrir menu” quando está expandido. O contorno de foco laranja também diverge do foco turquesa do design system.

Prioridade: média.

Evidência: `26-menu-privado-mobile.png`.

### 10. Sugestão de nova área sem acção

A página de áreas pede ao membro que contacte a equipa para sugerir uma área, mas não oferece ligação de email ou botão de contacto.

Prioridade: baixa.

Evidência: `15-areas.png`.

## Limites da auditoria

A administração ainda não foi auditada porque a sessão actual pertence a um membro sem privilégios. O controlo de acesso foi confirmado pela resposta 403.

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
13. `12-painel-membro.png`
14. `13-directorio.png`
15. `14-perfil-membro.png`
16. `14b-perfil-contacto.png`
17. `15-areas.png`
18. `16-favoritos.png`
19. `17-mensagens.png`
20. `18-notificacoes.png`
21. `19-menu-conta.png`
22. `20-meu-perfil.png`
23. `21-editar-perfil.png`
24. `22-editar-conta.png`
25. `23-desactivar-conta.png`
26. `24-admin-bloqueado.png`
27. `25-painel-mobile.png`
28. `26-menu-privado-mobile.png`
