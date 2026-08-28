# Santa Bot

Sistema de IDs para Discord.

- `/id` entrega o próximo ID.
- Começa em `00` e vai até `1000`.
- Se o membro usar `/id` novamente, recebe o mesmo ID.
- A mensagem de ID é pública para todos no canal.
- O ID é salvo em `ids.json`.
- `/meuid` mostra o ID do membro.
- `/idstatus` mostra o status para administradores.

## Railway

Crie a variável:

`TOKEN` = token do seu bot.

O bot precisa da permissão **Gerenciar Apelidos** e o cargo dele deve estar acima dos cargos que ele precisa alterar.

No Discord Developer Portal, ative **Server Members Intent**.
