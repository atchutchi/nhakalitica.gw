---
name: Kalitica Networking Society
description: Rede profissional privada da Guiné-Bissau e da diáspora
colors:
  primary-teal: "#2B7A77"
  primary-teal-deep: "#1E5A57"
  institutional-navy: "#0B3D61"
  mint: "#5AB59F"
  turquoise: "#22B8C7"
  leaf-green: "#78D84B"
  surface: "#FFFFFF"
  surface-soft: "#F6FAF9"
  surface-mint: "#E9F7F3"
  ink: "#0A1720"
  muted: "#536763"
  border: "#D7E5E1"
  success: "#1F8A5B"
  warning: "#9A6500"
  danger: "#B42318"
typography:
  display:
    fontFamily: "Outfit, Segoe UI, sans-serif"
    fontSize: "3.5rem"
    fontWeight: 700
    lineHeight: 1.05
    letterSpacing: "-0.03em"
  headline:
    fontFamily: "Outfit, Segoe UI, sans-serif"
    fontSize: "2rem"
    fontWeight: 700
    lineHeight: 1.15
  title:
    fontFamily: "Outfit, Segoe UI, sans-serif"
    fontSize: "1.25rem"
    fontWeight: 650
    lineHeight: 1.3
  body:
    fontFamily: "Outfit, Segoe UI, sans-serif"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.55
  label:
    fontFamily: "Outfit, Segoe UI, sans-serif"
    fontSize: "0.875rem"
    fontWeight: 600
    lineHeight: 1.35
rounded:
  sm: "6px"
  md: "10px"
  lg: "14px"
  pill: "999px"
spacing:
  xs: "4px"
  sm: "8px"
  md: "16px"
  lg: "24px"
  xl: "32px"
  xxl: "48px"
components:
  button-primary:
    backgroundColor: "{colors.primary-teal}"
    textColor: "{colors.surface}"
    typography: "{typography.label}"
    rounded: "{rounded.sm}"
    padding: "12px 20px"
    height: "44px"
  button-secondary:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.institutional-navy}"
    typography: "{typography.label}"
    rounded: "{rounded.sm}"
    padding: "11px 19px"
    height: "44px"
  input:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    typography: "{typography.body}"
    rounded: "{rounded.sm}"
    padding: "10px 12px"
    height: "44px"
---

# Design System: Kalitica Networking Society

## Overview

**Creative North Star: "A Mesa Profissional da Guiné"**

A interface é um espaço de trabalho privado onde cada pessoa entra com uma identidade confirmada e uma ligação reconhecida à Guiné-Bissau. A apresentação pública tem presença institucional. A aplicação privada é mais densa, previsível e orientada para pesquisa, candidatura e revisão.

O sistema segue fielmente os quatro painéis aprovados em `output/mockups`. A página pública usa áreas abertas e o símbolo vegetal da Kalitica como elemento de marca. A aplicação usa navegação compacta, filtros estáveis, listas claras e superfícies planas. A experiência não imita o CVLink, embora preserve os seus fluxos funcionais.

Características principais:

- Verde azul institucional com azul profundo e acentos retirados do logótipo.
- Tipografia Outfit numa escala controlada e legível.
- Página pública expressiva e aplicação privada contida.
- Estados de aprovação, privacidade e segurança sempre explícitos.
- Mesma estrutura visual em português, francês e inglês.

## Colors

A paleta combina o verde azul da Kalitica com azul institucional, menta e pequenas notas de turquesa e verde folha.

### Primary

- **Verde Kalitica:** acções primárias, selecção actual, ligações importantes e estados activos.
- **Azul Institucional:** cabeçalhos administrativos, autenticação e áreas que exigem maior peso e confiança.

### Secondary

- **Menta de Rede:** fundos seleccionados, confirmação e superfícies de apoio.
- **Turquesa de Ligação:** ícones e detalhes de orientação. Nunca substitui a acção primária.
- **Verde Folha:** detalhe de marca e ilustração do logótipo. Não serve para texto pequeno.

### Neutral

- **Branco de Superfície:** fundo de formulários, listas e conteúdo principal.
- **Névoa Verde:** fundo geral da aplicação e separação de zonas.
- **Tinta Profunda:** texto principal e títulos.
- **Verde Cinzento:** texto secundário com contraste verificado.
- **Linha Suave:** divisores e contornos estruturais.

**The Reserved Accent Rule.** O verde principal identifica acção, selecção e progresso. Nunca é espalhado como decoração em todos os componentes.

**The State Is Meaning Rule.** Verde, âmbar e vermelho só representam sucesso, correcção e erro quando existe um estado real.

## Typography

**Display Font:** Outfit com Segoe UI como alternativa

**Body Font:** Outfit com Segoe UI como alternativa

**Character:** Uma única família sustenta a marca e a aplicação. Os títulos são seguros e compactos. Os controlos mantêm uma escala fixa para reduzir ruído.

### Hierarchy

- **Display:** peso 700, máximo de 3.5rem, linha 1.05. Reservado à página pública.
- **Headline:** peso 700, 2rem, linha 1.15. Títulos principais de página.
- **Title:** peso 650, 1.25rem, linha 1.3. Secções e blocos funcionais.
- **Body:** peso 400, 1rem, linha 1.55. Texto com máximo de 70 caracteres por linha quando é corrido.
- **Label:** peso 600, 0.875rem, linha 1.35. Campos, botões, filtros e estado.

**The Product Scale Rule.** Não usar títulos fluidos dentro da aplicação. Painéis, formulários e tabelas usam tamanhos fixos.

**The Accent Integrity Rule.** Nenhum texto deve apresentar artefactos de codificação em português, francês ou inglês.

## Elevation

O sistema é plano por defeito. Fundos tonais e linhas suaves criam estrutura. Sombras pequenas aparecem apenas em menus suspensos, diálogo, cabeçalho fixo e resposta ao hover. Um componente não combina contorno decorativo com sombra larga.

- **Elevação de menu:** `0 8px 16px rgba(11, 61, 97, 0.12)`. Apenas para conteúdo que flutua sobre a página.
- **Elevação de estado:** `0 3px 8px rgba(11, 61, 97, 0.10)`. Hover de elementos accionáveis sem contorno forte.

**The Flat By Default Rule.** Se uma superfície continua compreensível com fundo e espaçamento, não recebe sombra.

## Components

### Buttons

- **Shape:** cantos controlados de 6px e altura mínima de 44px.
- **Primary:** Verde Kalitica sobre branco. Apenas uma acção primária dominante por região.
- **Hover e focus:** escurecimento para Verde Kalitica Profundo e anel de foco de 3px com separação de 2px.
- **Secondary:** fundo branco, texto Azul Institucional e contorno de 1px.
- **Destructive:** vermelho reservado a recusa, suspensão e desactivação, sempre com confirmação.

### Chips

- **Style:** fundos tonais suaves, raio completo e texto curto.
- **State:** filtros seleccionados usam Verde Kalitica. Efectivo e Observador usam identificadores discretos sem criar hierarquia de acesso.

### Cards / Containers

- **Corner Style:** 10px para blocos funcionais e máximo de 14px para composição pública.
- **Background:** branco ou Névoa Verde.
- **Shadow Strategy:** plano por defeito.
- **Border:** Linha Suave de 1px quando necessário.
- **Internal Padding:** 16px em mobile e 24px em desktop.

### Inputs / Fields

- **Style:** altura mínima de 44px, fundo branco, contorno de 1px e raio de 6px.
- **Focus:** contorno Verde Kalitica mais anel externo visível.
- **Error / Disabled:** erro inclui texto explicativo. O estado desactivado mantém legibilidade e não depende apenas da cor.

### Navigation

A página pública usa barra horizontal com logótipo, ligações, selector PT FR EN e acções Entrar e Pedir adesão. A aplicação privada usa navegação superior no membro e navegação lateral no administrador. Em mobile, a navegação recolhe para um painel com foco gerido e alvos de toque de 44px.

### Application Timeline

A candidatura apresenta uma sequência real de passos. O estado actual, os passos concluídos e as correcções necessárias têm texto, ícone e cor. A linha temporal nunca sugere aprovação antes da decisão administrativa.

### Professional Result Row

Cada resultado apresenta fotografia, nome, profissão, localização de acordo com a privacidade, competências principais, tipo de membro e acções Ver perfil e Guardar. As linhas suportam leitura rápida e não se transformam em cartões de marketing.

## Do's and Don'ts

### Do:

- **Do** seguir os quatro painéis em `output/mockups` como contrato de composição, densidade e hierarquia.
- **Do** manter contraste WCAG AA, foco visível e alvos de toque de 44px.
- **Do** usar espaços de 4, 8, 16, 24, 32 e 48px.
- **Do** mostrar claramente bloqueio, revisão manual, privacidade e estado da candidatura.
- **Do** testar português, francês e inglês em desktop, tablet e mobile.
- **Do** usar listas e tabelas quando a tarefa exige comparação ou densidade.

### Don't:

- **Don't** parecer uma cópia visual do CVLink, um portal público de currículos, uma plataforma europeia de emprego ou uma página genérica de software.
- **Don't** usar laranja como cor principal, gradientes roxos, glassmorphism ou texto em gradiente.
- **Don't** usar cartões com raio superior a 16px, sombras largas ou grelhas repetidas sem necessidade funcional.
- **Don't** expor pesquisa, perfis, telefone, email, localização detalhada ou currículo a pessoas não aprovadas.
- **Don't** mostrar preços, pagamentos, dívidas ou subscrições no lançamento.
- **Don't** usar movimento decorativo, esconder conteúdo atrás de animações ou ignorar movimento reduzido.
- **Don't** usar dados inventados como se fossem membros, candidaturas ou actividade reais em produção.
