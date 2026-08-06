# Auditoria da versão de produção

Data: 5 de Agosto de 2026

Estado: auditoria concluída, 16 problemas corrigidos e versão final validada em produção a 6 de Agosto de 2026.

## Resultado da correcção

Os 16 problemas prioritários ficaram corrigidos e cobertos por testes automatizados. A validação integral executou 299 testes sem falhas. Depois da publicação foram ainda executados 27 testes de moderação para a correcção do overflow mobile e do versionamento do CSS administrativo.

- A página inicial apresenta o encerramento dos registos antes das acções do hero e não oferece “Pedir adesão” enquanto o registo público estiver desactivado.
- O título do cartão azul usa branco calculado como `rgb(255, 255, 255)`.
- Os menus público e privado alternam os nomes acessíveis “Abrir menu” e “Fechar menu” e usam foco turquesa.
- O painel distingue perfil publicado, perfil aprovado mas oculto, perfil em revisão, perfil com correcções e perfil em rascunho.
- A navegação de definições marca apenas a secção actual com `aria-current="page"` e deixou de criar overflow global.
- Mensagens vazias apresentam uma acção para o Directório.
- A comparação só fica disponível com pelo menos dois favoritos.
- As respostas de permissão e formulário expirado usam páginas Kalitica e não expõem detalhes técnicos.
- A página de Áreas liga directamente a `info@nhakalitica.gw` e explica a revisão da sugestão.
- A Administração Kalitica inclui regresso à rede, saída por POST, navegação activa e filtros com nomes acessíveis.
- A revisão de perfis mostra apenas transições válidas. Um perfil aprovado apresenta “Suspender” e não apresenta “Aprovar publicação”.
- A Auditoria transforma as linhas em cartões no mobile e o filtro pode encolher sem provocar deslocamento horizontal.
- “Membros” abre uma página própria da Administração Kalitica com pesquisa, filtros, detalhe de conta, adesão e perfil.
- A recuperação de uma conta dentro dos 30 dias exige POST, mantém o perfil privado em rascunho e grava auditoria na mesma transacção.

## Validação final em produção

Produção validada em `https://nhakaliticagw-production.up.railway.app/` depois dos commits `44067a6`, `c9a1a2d` e `d598cdb`.

- `/saude/` respondeu `{"status": "ok"}` depois de cada deployment concluído.
- Home pública a 375 px: largura do documento dentro do viewport, aviso antes das acções, zero ligações “Pedir adesão” e menu com os dois nomes acessíveis.
- Painel do membro a 375 px: perfil publicado anunciado como visível e menu privado com os dois nomes acessíveis.
- Definições a 375 px: apenas “A minha conta” com `aria-current="page"` e sem overflow.
- Mensagens a 375 px: estado vazio com ligação `/pesquisar/`.
- Favoritos a 375 px: zero favoritos e comparação ausente.
- Áreas a 375 px: ligação `mailto:info@nhakalitica.gw` e nota traduzida confirmada em inglês e francês.
- Administração a 1440 px: perfil aprovado com apenas a acção “Suspender” e largura do documento igual ao viewport.
- Membros a 1440 px e 375 px: quatro contas de demonstração, quatro filtros nomeados, secção activa e ausência de overflow.
- Detalhe de Membro a 375 px: secções Conta, Adesão e Perfil profissional, sem acção de recuperação para uma conta activa.
- Auditoria a 375 px: `admin.css?v=20260806-1`, filtro em grelha com colunas de 179,9 px e 90,3 px e largura do documento igual a 375 px.

A captura visual do browser integrado voltou a expirar durante a validação final. Por esse motivo, a confirmação final combina estrutura acessível, estilos calculados, medições de viewport, respostas HTTP e os testes automatizados. Não foram executadas decisões administrativas nem recuperações de conta em produção.

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
- Painel administrativo, candidaturas, perfis, denúncias e auditoria.
- Estados vazios e estados aprovados das filas administrativas.
- Detalhe de uma candidatura aprovada e acções disponíveis.
- Detalhe de um perfil aprovado e acções disponíveis.
- Ligação entre a administração Kalitica e a administração Django de membros.

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

### 11. Administração sem saída directa ou regresso à rede

O cabeçalho administrativo mostra apenas o endereço da conta. Não existe uma acção visível para sair, regressar ao painel do membro ou abrir o Directório. A única saída indirecta passa pela administração Django através de “Membros”, o que não é um percurso claro nem adequado para uma operação frequente.

Prioridade: alta.

Evidência: `28-admin-painel.png`, `29-admin-candidaturas.png` e `31-admin-perfis.png`.

### 12. Filtros administrativos sem nome acessível

Os selectores de estado em Candidaturas, Perfis e Denúncias não têm `label` nem nome acessível. Um leitor de ecrã anuncia apenas “combobox”, sem explicar se o controlo filtra candidaturas, perfis ou denúncias.

Prioridade: alta para acessibilidade.

Evidência: passos `29-admin-candidaturas.png` e `31-admin-perfis.png`, confirmados pela estrutura acessível capturada no browser.

### 13. Perfil aprovado continua a oferecer “Aprovar publicação”

O detalhe de um perfil que já está aprovado continua a apresentar a acção “Aprovar publicação”. A acção redundante não corresponde ao estado actual e aumenta o risco de uma decisão administrativa repetida. Neste estado devem existir apenas acções válidas, como pedir correcções, suspender ou outra transição explicitamente permitida.

Prioridade: alta.

Evidência: estrutura acessível do detalhe `/administracao/perfis/1/`. A captura visual desta página bloqueou repetidamente no browser e não foi aceite como evidência gráfica.

### 14. Tabela de auditoria força deslocamento horizontal

Na largura intermédia auditada, a tabela mantém uma largura mínima de 800 px. A coluna “Contexto” fica fora do ecrã e surge uma barra de deslocamento horizontal dentro do cartão. Um registo de auditoria precisa de permitir leitura rápida sem esconder a informação que explica a decisão.

Prioridade: média.

Evidência: `27-admin-auditoria.png`.

### 15. Gestão de membros quebra a experiência Kalitica

A ligação “Membros” abre a administração Django padrão. O destino usa outra estrutura visual, apresenta nomenclatura técnica e mistura português com rótulos em inglês, como “Accounts”, “Legal acceptances” e “Membership decisions”. A equipa deixa de ter uma experiência administrativa coerente e fica exposta a operações técnicas que não fazem parte do fluxo normal de revisão.

Prioridade: média.

Evidência: estrutura acessível de `/admin/accounts/user/`. A captura visual deixou de estar disponível após a falha de captura descrita nos limites.

### 16. Navegação administrativa não indica a secção activa

A barra lateral mantém o mesmo aspecto em Painel, Candidaturas, Perfis, Denúncias e Auditoria. O administrador não recebe indicação visual nem `aria-current` sobre a secção onde se encontra.

Prioridade: baixa.

Evidência: `27-admin-auditoria.png`, `28-admin-painel.png`, `29-admin-candidaturas.png` e `31-admin-perfis.png`.

## Limites da auditoria

A administração foi auditada com uma conta de demonstração com privilégios de staff. Nenhuma candidatura, perfil, denúncia, utilizador ou registo foi alterado durante a auditoria.

As capturas das páginas de detalhe de perfil, denúncias e administração Django falharam repetidamente depois de o browser deixar de conseguir capturar a superfície. A estrutura acessível e os destinos foram inspeccionados, mas estas páginas ficam registadas como lacunas de evidência visual. A validação final deve repetir as capturas depois das correcções.

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
29. `27-admin-auditoria.png`
30. `28-admin-painel.png`
31. `29-admin-candidaturas.png`
32. `29b-admin-candidaturas-aprovadas.png`
33. `30-admin-candidatura-detalhe.png`
34. `30b-admin-candidatura-accoes.png`
35. `31-admin-perfis.png`
36. `31b-admin-perfis-aprovados.png`
