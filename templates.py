import streamlit as st
import pandas as pd
from views import *
from datetime import datetime
import base64


#use no terminal antes
#streamlit cache clear

def gerar_txt_venda(venda_id, nome_cliente, itens_venda):
    """Gera conteúdo TXT formatado para a venda"""
    cabecalho = f"""
==================================
COMPROVANTE DE ORÇAMENTO - ID: {venda_id}
Cliente: {nome_cliente}
Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}
=================================="""
    
    corpo = []
    total_venda = 0
    
    for item in itens_venda:
        linha = f"{item.descricao[:30]:<30} \n| {item.quantidade:>3.0f}x R${item.preco:>7.2f} = R${item.quantidade * item.preco:>8.2f}"
        corpo.append(linha)
        total_venda += item.quantidade * item.preco
    
    rodape = f"""
==================================
TOTAL DO ORÇAMENTO: R${total_venda:.2f}
=================================="""
    
    return cabecalho + "\n" + "\n".join(corpo) + rodape

def limpar_pagina():
    st.cache_data.clear()  # Limpa o cache
    st.session_state['sessao_Atual'] = "Lista de Vendas"
    st.rerun()

# Inicializa o estado da sessão
if "sessao_Atual" not in st.session_state:
    st.session_state["sessao_Atual"] = "Vendas"



st.title('Orçamentos')

# Menu lateral
menu = st.sidebar.selectbox(
    'Escolha uma Opção',
    ['Lista de Vendas', 'Produtos','Vendas','Atualização de Venda','Atualizar Precos','Importacao DeepSeek'],
    index=['Lista de Vendas', 'Produtos','Vendas','Atualização de Venda','Atualizar Precos','Importacao DeepSeek'].index(st.session_state["sessao_Atual"])
)

# Atualiza o session state com base na seleção do menu lateral
if menu != st.session_state["sessao_Atual"]:
    st.session_state["sessao_Atual"] = menu
    st.session_state["id_venda_atual"] = None  
    st.rerun()  # Recarrega a aplicação


# Botões para alternar entre as seções
#col1, col2 = st.columns(2)
#with col1:
#    if st.button('Vendas'):
#        st.session_state["sessao_Atual"] = "sessao_Vendas"

#with col2:
#    if st.button('Produtos'):
#        st.session_state['sessao_Atual'] = "sessao_Produtos"
    # Adicione aqui o conteúdo específico de Vendas

#pagina Cadastro de Produtos
if st.session_state['sessao_Atual'] == "Produtos":
    st.write("Conteúdo da seção de Produtos")
    with st.form('Cadastrar novo Produto'):
        codigo_field = st.text_input('Digite o código do produto')
        codigoInterno_field = st.text_input('Codigo interno do Produto')
        descricao_field = st.text_input('Descrição do Produto')
        preco_field = st.text_input('Preço do Produto R$')
        botao_salvar = st.form_submit_button('Salvar Produto')
        if botao_salvar:
            produto=Produtos(codigo=codigo_field,codInterno=codigoInterno_field,descricao=descricao_field, preco=float(preco_field))
            gravacao = incluir_produto(produto)
            if gravacao:
                st.write('Produto cadastrado')
            else:
                st.write(f'Erro {gravacao}')

######################################################################

#pagina incluir items
if st.session_state["sessao_Atual"] == "Vendas":
    id_venda_atual = ultima_venda()
    if id_venda_atual == 'sem vendas':
        id_venda_atual = 1
    st.session_state["id_venda_atual"] = id_venda_atual
    st.write(f'Incluir itens na venda {id_venda_atual}')
    st.write('Procurar')
    procura_field =''
    procura_field = st.text_input('Digite o código do produto')
    st.write('Incluir')
    if procura_field:
        produto = consultar_produtos(procura_field)
        if (len(produto)) != 1:
            for i, item in enumerate(produto):  # Usar enumerate para obter um índice único
                
                col1, col2, col3, col4, col5, col6 = st.columns([1, 1, 1, 0.5, 0.5, 1])
                with col1:
                    codigo_field = st.text_input('Codigo', value=(item.codigo+' '+item.codInterno), key=f'codigo_{i}')
                with col2:
                    descricao_field = st.text(item.descricao)
                    #descricao_field = st.text_input('Descricao', value=item.descricao, key=f'descricao_{i}')
                with col3:
                    quantidade_field = st.number_input('Qtd', step=1, value=1, key=f'quantidade_{i}')
                with col4:
                    preco_field = st.text_input('Preço', value=item.preco, key=f'preco_{i}')
                with col5:
                    total_field = st.text_input('Total', value=quantidade_field * float(preco_field), key=f'total_{i}')
                with col6:
                    st.write('incluir')
                    # Adicionar uma key única para o botão de inclusão
                    botao_salvar = st.button('✅', key=f'botao_{i}')
                #usa o conteiner para mostrar a mensagem sem está dentro da coluna
                # if deve estar um tab antes da criação do botao
                if botao_salvar:
                    with st.container():
                        # Criar o objeto Vendas_item e incluir na venda
                        #venda_item = Vendas_item(numero_venda=id_venda_atual,codigo=codigo_field,descricao=descricao_field,preco=float(preco_field),quantidade=quantidade_field,total=float(total_field))
                        venda_item = Vendas_item(numero_venda=id_venda_atual,codigo=codigo_field,descricao=item.descricao,preco=float(preco_field),quantidade=quantidade_field,total=float(total_field))
                        incluir_venda_item(venda_item)
                    st.success('Item incluído')
        else:
            col1,col2,col3,col4,col5,col6 = st.columns([1, 1, 1, 0.5, 0.5, 1])
            with col1:
                codigo_field = st.text_input('Codigo',value=(produto[0].codigo+' '+produto[0].codInterno))
            with col2:
                descricao_field = st.text(produto[0].descricao)
                #descricao_field = st.text_input('Descricao',value=produto[0].descricao)
            with col3:
                quantidade_field = st.number_input('Qtd',step=1,value=1)
            with col4:
                preco_field = st.text_input('Preço',value=produto[0].preco)
            with col5:
                total_field = st.text_input('Total',value=quantidade_field * float(preco_field))
            with col6:
                    st.write('incluir')
                    botao_salvar = st.button('✅')
            # usa o conteiner para mostrar a mensagem sem está dentro da coluna
            # if deve estar um tab antes da criação do botao
            if botao_salvar:
                with st.container():
                    venda_item = Vendas_item(numero_venda=id_venda_atual,codigo=codigo_field,descricao=produto[0].descricao,preco=float(preco_field),quantidade=quantidade_field,total=float(total_field))
                    #venda_item = Vendas_item(numero_venda=id_venda_atual,codigo=codigo_field,descricao=descricao_field,preco=float(preco_field),quantidade=quantidade_field,total=float(total_field))
                    incluir_venda_item(venda_item)
                st.success('Item incluído ')
    st.divider()
    st.header('Itens do Orcamento')
    itens_venda = consultar_venda_items(id_venda_atual)
    print(itens_venda)
    totalVenda = 0
    if itens_venda != 'Venda não existe':
        for linha in itens_venda:
            totalVenda+=float(linha.total)
            col1,col2,col3,col4,col5,col6 = st.columns([2,3,1,1,1,1])
            with col1:
                st.write(linha.codigo)
            with col2:
                st.write(linha.descricao)
            with col3:
                st.write(linha.preco)
            with col4:
                st.write(linha.quantidade)
            with col5:
                st.write(linha.total)
                #st.write(linha.id,linha.codigo,linha.descricao,linha.preco,linha.quantidade,'Valor',linha.total)
            with col6:
                apagarItem= st.button(f"🗑️", key=linha.id)
                if apagarItem:
                    apagar_venda_item(linha.id)
                    st.write('item Excluído')
                    st.rerun()
    
    st.header('Total do Orçamento')
    st.header('Valor Total Orçamento       R${:.2f}'.format(totalVenda))
    st.divider()

    st.header('Recebimento')
    nome_cliente = st.text_input('Nome do Cliente. Deixa em branco se quiser')
    tipo_pagamento=st.selectbox('Escolha o Metodo de Pagamento',['Dinheiro','Pix','Cartão de Débito','Cartão de Crédito'])
    if tipo_pagamento == 'Dinheiro':
        valor_pago = st.text_input('Dinheiro Recebibo')
        if valor_pago:
            valor_pagoF = float(valor_pago)
            st.header('Troco     R${:.2f}'.format(valor_pagoF-totalVenda))
            if nome_cliente != '':
                confirmar_venda = st.button('Confimar Venda')
                if confirmar_venda:
                    venda = Vendas(nome_cliente=nome_cliente,Total_venda=totalVenda,forma_pagamento=tipo_pagamento)
                    incluir_venda(venda)
                    st.write('Recebimento em Dinheiro')
                    limpar_pagina()
            else:
                confirmar_venda = st.button('Confimar Venda')
                if confirmar_venda:
                    venda = Vendas(Total_venda=totalVenda,forma_pagamento=tipo_pagamento)
                    incluir_venda(venda)
                    st.write('Recebimento em Dinheiro')
                    limpar_pagina()
        else:
            st.write('Aguardando Pagamento')
    else:
        if nome_cliente != '':
            confirmar_venda = st.button('Confimar Venda')
            if confirmar_venda:
                venda = Vendas(nome_cliente=nome_cliente,Total_venda=totalVenda,forma_pagamento=tipo_pagamento)
                st.write(f'Recebimento em {tipo_pagamento}')
                incluir_venda(venda)
                st.write(venda)
                limpar_pagina()
        else:
            confirmar_venda = st.button('Confimar Venda')
            if confirmar_venda:
                venda = Vendas(Total_venda=totalVenda,forma_pagamento=tipo_pagamento)
                st.write(f'Recebimento em {tipo_pagamento}')
                incluir_venda(venda)
                st.write(venda)
                limpar_pagina()
                
#pagina lista de Vendas
if st.session_state['sessao_Atual'] == "Lista de Vendas":
    st.write('lista de vendas')
    
    st.divider()
    col1,col2,col3,col4,col5,col6,col7= st.columns([0.3,1,1,1,1,1,1])
    with col1:
        st.write('**id**')
    with col2:
        st.write('**Cliente**')
    with col3:
        st.write('**Total venda**')
    with col4:
        st.write('**Pagamento**')
    with col5:
        st.write('**data**')
    with col6:
        st.write('**Excluir**')
    with col7:
        st.write('**Imprimir**')
    
    vendas = listar_vendas()
    if vendas != 'Sem Vendas':
        for venda in reversed(vendas):
            
            col1,col2,col3,col4,col5,col6,col7,col8= st.columns([0.3,2,1,1,1,1.5,1,1])
            with col1:
                st.text(venda.id)
            with col2:
                st.write(f'**{venda.nome_cliente}**')
            with col3:
                st.write('{:.2f}'.format(venda.Total_venda))
            with col4:
                st.write(venda.forma_pagamento)
            with col5:
                st.write(venda.data)
            with col6:
                subcol1, subcol2 = st.columns([1, 3])  # Ajuste a proporção conforme necessário
                with subcol1:
                    apagarVenda = st.button(f"🗑️", key=f'apagar_{venda.id}')
                with subcol2:
                    senha = st.text_input('Senha', type="password", key=f"sen_{venda.id}", label_visibility="collapsed")
            if apagarVenda and senha == 'maciel1':
                itens_venda = consultar_venda_items(venda.id)
                for item in itens_venda:
                    st.write(f'apagar{item.id}')
                    apagar_venda_item(item.id)
                apagar = apagar_vendas(venda.id)
                st.write(apagar)
                st.success('Venda Excluida')
                limpar_pagina()
                        
            with col7:
                listarItems = st.button(f'items', key=f'listar_{venda.id}')
            if listarItems:
                with st.container():
                    itens_venda = consultar_venda_items(venda.id)
                    totalVenda = 0
                    if itens_venda != 'Venda não existe':
                        for linha in itens_venda:
                            totalVenda+=float(linha.total)
                            col1,col2,col3,col4,col5,col6 = st.columns([2,3,1,1,1,1])
                            with col1:
                                st.write(linha.codigo)
                            with col2:
                                st.write(linha.descricao)
                            with col3:
                                st.write(linha.preco)
                            with col4:
                                st.write(linha.quantidade)
                            with col5:
                                st.write(linha.total)
                            #st.write(linha.id,linha.codigo,linha.descricao,linha.preco,linha.quantidade,'Valor',linha.total)
                    st.header(f'total R${totalVenda}')
            st.divider()
            
           
            with col8:
                listarItems = st.button('🖨️', key=f'imprimir_{venda.id}')
            if listarItems:
                with st.container():
                    st.write('Gerar txt')
                    itens_venda = consultar_venda_items(venda.id)
                    if itens_venda != 'Venda não existe':
                        conteudo_txt = gerar_txt_venda(
                            venda_id=venda.id,
                            nome_cliente=venda.nome_cliente,
                            itens_venda=itens_venda
                        )
                        
                        # Cria link para download
                        st.download_button(
                            label="Baixar Comprovante",
                            data=conteudo_txt,
                            file_name=f"comprovante_venda_{venda.id}.txt",
                            mime="text/plain"
                        )
                        
                        # Mostra pré-visualização
                        st.subheader("Pré-visualização do Comprovante:")
                        st.code(conteudo_txt, language='text')
                    else:
                        st.error("Venda não encontrada!")

#pagina atualizacao de venda
if st.session_state['sessao_Atual'] == "Atualização de Venda":
    st.write('Atualização de Venda')
    vendas = listar_vendas()
    opcoes_vendas = [' ']  # Opção vazia
    mapeamento_vendas = {}  # Guarda a relação {texto_exibido: id_venda}

    for venda in vendas:
        texto_exibido = f"{venda.id}      -{venda.nome_cliente}     -R${venda.Total_venda:.2f}  -{venda.forma_pagamento}"
        opcoes_vendas.append(texto_exibido)
        mapeamento_vendas[texto_exibido] = venda.id  # Mapeia o texto para o ID

    # Exibe o selectbox
    venda_selecionada = st.selectbox('Selecione a Venda para Editar', opcoes_vendas)

    # Pega apenas o ID da venda selecionada
    if venda_selecionada != ' ':
        id_venda = mapeamento_vendas[venda_selecionada]
        st.write(f"ID da venda selecionada: {id_venda}")
        
        id_venda_atual = id_venda
        if id_venda_atual == 'sem vendas':
            id_venda_atual = 1
        st.session_state["id_venda_atual"] = id_venda_atual
        st.write(f'Incluir itens na venda {id_venda_atual}')
        st.write('Procurar')
        procura_field =''
        procura_field = st.text_input('Digite o código do produto')
        st.write('Incluir')
        if procura_field:
            produto = consultar_produtos(procura_field)
            if (len(produto)) != 1:
                for i, item in enumerate(produto):  # Usar enumerate para obter um índice único
                    
                    col1, col2, col3, col4, col5, col6 = st.columns([1, 1, 1, 0.5, 0.5, 1])
                    with col1:
                        codigo_field = st.text_input('Codigo', value=(item.codigo+' '+item.codInterno), key=f'codigo_{i}')
                    with col2:
                        descricao_field = st.text(item.descricao)
                        #descricao_field = st.text_input('Descricao', value=item.descricao, key=f'descricao_{i}')
                    with col3:
                        quantidade_field = st.number_input('Qtd', step=1, value=1, key=f'quantidade_{i}')
                    with col4:
                        preco_field = st.text_input('Preço', value=item.preco, key=f'preco_{i}')
                    with col5:
                        total_field = st.text_input('Total', value=quantidade_field * float(preco_field), key=f'total_{i}')
                    with col6:
                        st.write('incluir')
                        # Adicionar uma key única para o botão de inclusão
                        botao_salvar = st.button('✅', key=f'botao_{i}')
                    #usa o conteiner para mostrar a mensagem sem está dentro da coluna
                    # if deve estar um tab antes da criação do botao
                    if botao_salvar:
                        with st.container():
                            # Criar o objeto Vendas_item e incluir na venda
                            #venda_item = Vendas_item(numero_venda=id_venda_atual,codigo=codigo_field,descricao=descricao_field,preco=float(preco_field),quantidade=quantidade_field,total=float(total_field))
                            venda_item = Vendas_item(numero_venda=id_venda_atual,codigo=codigo_field,descricao=item.descricao,preco=float(preco_field),quantidade=quantidade_field,total=float(total_field))
                            incluir_venda_item(venda_item)
                        st.success('Item incluído')
            else:
                col1,col2,col3,col4,col5,col6 = st.columns([1, 1, 1, 0.5, 0.5, 1])
                with col1:
                    codigo_field = st.text_input('Codigo',value=(produto[0].codigo+' '+produto[0].codInterno))
                with col2:
                    descricao_field = st.text(produto[0].descricao)
                    #descricao_field = st.text_input('Descricao',value=produto[0].descricao)
                with col3:
                    quantidade_field = st.number_input('Qtd',step=1,value=1)
                with col4:
                    preco_field = st.text_input('Preço',value=produto[0].preco)
                with col5:
                    total_field = st.text_input('Total',value=quantidade_field * float(preco_field))
                with col6:
                        st.write('incluir')
                        botao_salvar = st.button('✅')
                # usa o conteiner para mostrar a mensagem sem está dentro da coluna
                # if deve estar um tab antes da criação do botao
                if botao_salvar:
                    with st.container():
                        venda_item = Vendas_item(numero_venda=id_venda_atual,codigo=codigo_field,descricao=produto[0].descricao,preco=float(preco_field),quantidade=quantidade_field,total=float(total_field))
                        #venda_item = Vendas_item(numero_venda=id_venda_atual,codigo=codigo_field,descricao=descricao_field,preco=float(preco_field),quantidade=quantidade_field,total=float(total_field))
                        incluir_venda_item(venda_item)
                    st.success('Item incluído ')
        st.divider()
        st.header('Itens do Orcamento')
        itens_venda = consultar_venda_items(id_venda_atual)
        print(itens_venda)
        totalVenda = 0
        if itens_venda != 'Venda não existe':
            for linha in itens_venda:
                totalVenda+=float(linha.total)
                col1,col2,col3,col4,col5,col6 = st.columns([2,3,1,1,1,1])
                with col1:
                    st.write(linha.codigo)
                with col2:
                    st.write(linha.descricao)
                with col3:
                    st.write(linha.preco)
                with col4:
                    st.write(linha.quantidade)
                with col5:
                    st.write(linha.total)
                    #st.write(linha.id,linha.codigo,linha.descricao,linha.preco,linha.quantidade,'Valor',linha.total)
                with col6:
                    apagarItem= st.button(f"🗑️", key=linha.id)
                    if apagarItem:
                        apagar_venda_item(linha.id)
                        st.write('item Excluído')
                        st.rerun()
        
        st.header('Total do Orçamento')
        st.header('Valor Total Orçamento       R${:.2f}'.format(totalVenda))
        st.divider()

        st.header('Recebimento')
        
        tipo_pagamento=st.selectbox('Escolha o Metodo de Pagamento',['Dinheiro','Pix','Cartão de Débito','Cartão de Crédito'])
        if tipo_pagamento == 'Dinheiro':
            valor_pago = st.text_input('Dinheiro Recebibo')
            if valor_pago:
                valor_pagoF = float(valor_pago)
                st.header('Troco     R${:.2f}'.format(valor_pagoF-totalVenda))
                
                confirmar_venda = st.button('Atualizar Venda')
                if confirmar_venda:
                    #venda = Vendas(nome_cliente=nome_cliente,Total_venda=totalVenda,forma_pagamento=tipo_pagamento)
                    alterar_vendas(id_venda_atual, totalVenda , tipo_pagamento)
                    #incluir_venda(venda)
                    st.write('Recebimento em Dinheiro')
                    limpar_pagina()
                
            else:
                st.write('Aguardando Pagamento')
        else:
            
            confirmar_venda = st.button('Confimar Alteração')
            if confirmar_venda:
                #venda = Vendas(nome_cliente=nome_cliente,Total_venda=totalVenda,forma_pagamento=tipo_pagamento)
                st.write(f'Recebimento em {tipo_pagamento}')
                alterar_vendas(id_venda_atual, totalVenda, tipo_pagamento)
                #incluir_venda(venda)
                st.write('Venda Atualizada')
                limpar_pagina()
           
    else:
        st.warning("Nenhuma venda selecionada.")


#pagina atualizar preços
if st.session_state['sessao_Atual'] == "Atualizar Precos":
    st.write('Atualizar Precos')
    # Widget para upload de arquivo
    uploaded_file = st.file_uploader("Envie um arquivo dos Produtos xlsx", type=["xlsx"])
    # Verifica se um arquivo foi carregado
    if uploaded_file is not None and uploaded_file.name == 'Produtos.xlsx':
            # Lê o arquivo CSV usando pandas
            df = pd.read_excel(uploaded_file)
            linhas_da_tabela = len(df)
            tabela = df.iterrows()
            progresso = st.progress(0)
            texto_status = st.empty()

            icodBarras =  "Código de Barras"
            icodInterno = "Código Interno"
            iDescricao = "Descrição"
            iPreco = "Preço Venda Varejo"
            
            for index, row in tabela:
                progresso.progress((index + 1) / linhas_da_tabela)
                texto_status.text(f"Itens restantes: {linhas_da_tabela - index - 1}") 
                #st.write(row[icodBarras],row[str(icodInterno)],row[iDescricao],row[iPreco] )
                importa_produtos(str(row[icodBarras]),str(row[icodInterno]),str(row[iDescricao]), float(row[iPreco]))
            st.write('Importação Concluida')
    else:
        st.write('Procure o arquivo correto para importar')

#pagina importacao DeepSeek
if st.session_state['sessao_Atual'] == "Importacao DeepSeek":
    st.write('Importacao DeepSeek')
    
    uploaded_file = st.file_uploader("Envie um arquivo dos Produtos xlsx", type=["xlsx"])
    
    if uploaded_file is not None and uploaded_file.name == 'Produtos.xlsx':
        try:
            df = pd.read_excel(uploaded_file)
            
            # Barra de progresso
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Processamento em lote
            status_text.text("Iniciando processamento em lote...")
            resultado = importa_produtos_em_lote(df)
            
            progress_bar.progress(100)
            status_text.text("")
            
            st.success(f"""
                Importação concluída com sucesso!
                - Total processado: {resultado['total']}
                - Produtos atualizados: {resultado['atualizados']}
                - Novos produtos: {resultado['novos']}
            """)
            
        except Exception as e:
            st.error(f"Erro durante a importação: {str(e)}")
    else:
        st.warning('Por favor, envie o arquivo "Produtos.xlsx"')

