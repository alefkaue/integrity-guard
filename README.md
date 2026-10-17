# integrity-guard

Monitoramento de integridade de arquivos com SHA-256. Projeto independente de portfólio voltado a **Blue Team / resposta a incidentes**.

Cria um inventário SHA-256 e compara arquivos adicionados, alterados e removidos.
    Rejeita links simbólicos e arquivos especiais e detecta alterações durante a leitura.
    Valida o formato do inventário antes da comparação.

## Executar

Requer Python 3.11 ou superior. Usa somente a biblioteca padrão; não precisa instalar pacotes.

```console
git clone https://github.com/alefkaue/integrity-guard.git
cd integrity-guard
python integrity_guard.py baseline examples/site baseline.json
python integrity_guard.py check examples/site baseline.json
```

As ferramentas escrevem JSON em stdout. Use `--help` para consultar opções. Exemplos são sintéticos e não contêm dados reais.

## Testes

```console
python -m unittest discover -s tests -v
```

A automação executa a suíte em Windows e Linux, com Python 3.11 e 3.13.

## Decisões e limites

Veja [a arquitetura](docs/architecture.md) para o modelo de ameaça, decisões e limitações. Este é um laboratório educacional: os resultados exigem contexto e validação humana. Não substitui um SIEM, EDR ou avaliação completa de segurança.

## Exercício para demonstração

Execute o exemplo, explique cada campo do JSON e altere a entrada para observar a mudança no resultado. Os testes documentam casos de detecção e de comportamento esperado.

## Desenvolvimento

Código inicial desenvolvido com assistência de IA. O repositório explicita o escopo e usa dados sintéticos para permitir revisão e reprodução. Sugestões e correções podem ser propostas por issues e pull requests. Licença MIT.
