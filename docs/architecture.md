# Arquitetura e limites

A coleta lê arquivos em blocos de 1 MiB e produz caminhos relativos com separador POSIX. A comparação usa conjuntos para inclusões/remoções e SHA-256 para alterações de conteúdo. Retorno CLI: 0 baseline criado ou sem mudanças, 1 mudanças, 2 erro. A criação usa modo exclusivo: não sobrescreve inventário existente.

O inventário precisa estar fora da árvore e protegido separadamente contra alterações. Não tem assinatura; um invasor com acesso ao inventário pode falsificá-lo. SHA-256 não atesta autoria nem identifica malware. Permissões, ACLs e timestamps não são monitorados. Links simbólicos e arquivos especiais causam erro. Há verificações de identidade/tamanho/tempos durante leitura, mas não há snapshot atômico nem proteção completa contra corrida em uma árvore ativamente hostil, junctions/reparse points ou atacante com privilégios. Use em diretório estável e confiável ou snapshot do sistema de arquivos. Não promete ser um EDR.

Demonstração: crie o baseline, altere examples/site/index.html e execute check. Depois adicione/remova um arquivo. Próxima evolução: inventários assinados e suporte explícito a metadados.
