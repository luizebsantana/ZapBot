SEARCH_BAR = '//div[@data-tab="3" and @role="textbox"]'
LIST_CONTAINER = '//div[@id="pane-side"]'
LIST = './/div[@aria-label="Lista de conversas" or @aria-label="Resultados da pesquisa."]/div/div/div'
LIST_ITEM_NAME = './/div[@aria-colindex="2"]/div[1]'
LIST_ITEM_TIME = './/div[@aria-colindex="2"]/div[2]'
LIST_ITEM_NAO_LIDA = './/*[contains(@aria-label, "não lida")]'
SEARCH_CANCEL_BUTTON = '//button[@aria-label="Lista de conversas"]/../span/button'

ARCHIVED_OPEN_BUTTON = '//div[@id="pane-side"]/button[@aria-label="Arquivadas "]'
ARCHIVED_BACK_BUTTON = '//header//button[@aria-label="Voltar"]'
ARCHIVED_MENU_HEADER = '//h1[contains(text(),"Arquivada")]'

CHAT_CONTAINER = '//div[@id="main"]//div[contains(@aria-label, "Lista de mensagens.")]/..'
CHAT_NAME = '//div[@id="main"]/header/div[2]/div[1]'
CHAT = '//div[@id="main"]//div[contains(@aria-label, "Lista de mensagens.")]/div'

MENSAGE_BOX = '//div[@title="Mensagem"]'
SEND_BUTTON = '//button/span[@data-icon="send"]'


