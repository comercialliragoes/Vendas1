# views.py
from models import Produtos, Vendas_item, Vendas, engine
from sqlmodel import Session, select
from datetime import date, timedelta
import streamlit as st

# Função para obter uma sessão do banco de dados
@st.cache_resource
def get_session():
    return Session(engine)

# Funções de CRUD
def incluir_produto(produtos: Produtos):
    with get_session() as session:
        session.add(produtos)
        session.commit()
        return produtos

def alterar_produto(id, descricao_nova, preco_novo):
    with get_session() as session:
        statement = select(Produtos).where(Produtos.id == id)
        produto_para_alterar = session.exec(statement).first()
        if produto_para_alterar:
            produto_para_alterar.descricao = descricao_nova
            produto_para_alterar.preco = preco_novo
            session.commit()
            return produto_para_alterar
        else:
            return "Produto não encontrado"

def importa_produtos(codigo,codinterno,descricao, preco):
    with get_session() as session:
        statement = select(Produtos).where(Produtos.descricao == descricao)
        produto_para_alterar = session.exec(statement).first()
        print(produto_para_alterar)
        if produto_para_alterar:
            produto_para_alterar.codigo = codigo
            produto_para_alterar.codInterno = codinterno
            produto_para_alterar.descricao = descricao
            produto_para_alterar.preco = preco
            session.commit()
            return 'produto alterado'
        elif not produto_para_alterar:
            produto_novo=Produtos(codigo=codigo,codInterno=codinterno,descricao=descricao, preco=preco)
            incluir_produto(produto_novo)
            return 'Produto incluido'

def consultar_produtos(descricao: str):
    with get_session() as session:
        statement = select(Produtos).where(Produtos.descricao.like('%'+descricao+'%'))
        results = session.exec(statement).all()
        if not results:
            statement = select(Produtos).where(Produtos.codigo.like('%'+descricao+'%'))
            results = session.exec(statement).all()
            if not results:
                statement = select(Produtos).where(Produtos.codInterno.like('%'+descricao+'%'))
                results = session.exec(statement).all()
        return results

def incluir_venda_item(item: Vendas_item):
    with get_session() as session:
        session.add(item)
        session.commit()

def consultar_venda_items(numero_venda):
    with get_session() as session:
        statement = select(Vendas_item).where(Vendas_item.numero_venda == numero_venda)
        results = session.exec(statement).all()
        if results:
            return results
        else:
            return "Venda não existe"

def apagar_venda_item(id):
    with get_session() as session:
        statement = select(Vendas_item).where(Vendas_item.id == id)
        results = session.exec(statement).first()
        if results:
            session.delete(results)
            session.commit()
            return "Produto excluído"
        else:
            return "Produto não encontrado"

def ultima_venda():
    with get_session() as session:
        statement = select(Vendas).order_by(Vendas.id.desc()).limit(1)
        results = session.exec(statement).first()
        if results:
            return results.id +1
        else:
            return 'sem vendas'


def incluir_venda(vendas: Vendas):
    with get_session() as session:
        session.add(vendas)
        session.commit()

def alterar_vendas(id, total_novo, forma_pagamento_nova):
    with get_session() as session:
        statement = select(Vendas).where(Vendas.id == id)
        venda_alterar_total = session.exec(statement).first()
        if venda_alterar_total:
            venda_alterar_total.Total_venda = total_novo
            venda_alterar_total.forma_pagamento = forma_pagamento_nova
            session.commit()
            return "Total da Venda Alterada"
        else:
            return "Venda não encontrada"

def apagar_vendas(id):
    with get_session() as session:
        statement = select(Vendas).where(Vendas.id == id)
        results = session.exec(statement).first()
        if results:
            session.delete(results)
            session.commit()
            return "Venda Excluída"
        else:
            return "Venda não encontrada"
def listar_vendas():
    with get_session() as session:
        statement = select(Vendas)
        results = session.exec(statement).all()
        if results:
            return results
        else:
            return 'Sem Vendas'

#importacao com codigo DeepSeek
def importa_produtos_em_lote(df):
    """
    Processa um DataFrame completo de produtos com tratamento de valores nulos
    """
    with get_session() as session:
        # Pré-processamento do DataFrame
        df = df.rename(columns={
            'Código de Barras': 'codigo',
            'Código Interno': 'codInterno',
            'Descrição': 'descricao',
            'Preço Venda Varejo': 'preco'
        })
        
        # Tratamento de valores nulos - substitui NaN por string vazia ou valor padrão
        df['codInterno'] = df['codInterno'].fillna('').astype(str)
        df['codigo'] = df['codigo'].fillna('').astype(str)
        df['descricao'] = df['descricao'].fillna('').astype(str)
        df['preco'] = df['preco'].fillna(0.0)
        
        # Converter para lista de dicionários
        produtos_data = df.to_dict('records')

        # Consulta otimizada
        descricoes = [p['descricao'] for p in produtos_data if p['descricao']]
        produtos_existentes = session.exec(
            select(Produtos).where(Produtos.descricao.in_(descricoes))
        ).all()
        
        existentes_dict = {p.descricao: p for p in produtos_existentes}
        novos_produtos = []
        atualizados = 0
        
        for produto in produtos_data:
            # Validação adicional dos campos obrigatórios
            if not produto['descricao']:
                continue  # Pula registros sem descrição
                
            if produto['descricao'] in existentes_dict:
                p = existentes_dict[produto['descricao']]
                # Atualiza apenas se o valor não for nulo/vazio
                if produto['codigo']: p.codigo = produto['codigo']
                if produto['codInterno']: p.codInterno = produto['codInterno']
                if produto['preco']: p.preco = produto['preco']
                atualizados += 1
            else:
                # Valida campos obrigatórios antes de inserir
                if produto['descricao'] and produto['codInterno']:
                    novos_produtos.append(Produtos(
                        codigo=produto['codigo'],
                        codInterno=produto['codInterno'],
                        descricao=produto['descricao'],
                        preco=produto['preco']
                    ))
        
        try:
            if novos_produtos:
                session.bulk_save_objects(novos_produtos)
            session.commit()
            
            return {
                'total': len(produtos_data),
                'atualizados': atualizados,
                'novos': len(novos_produtos),
                'ignorados': len(produtos_data) - (atualizados + len(novos_produtos))
            }
            
        except Exception as e:
            session.rollback()
            raise e
            
#incluir produto
#produto=Produtos(codigo='GG5007',codInterno='GG5009',descricao='Parafuso autobrocante3', preco=1.50)
#incluir_produto(produto)

#consulta Produtos
#descricao = "%gg5003%"
#consulta=consultar_produtos(descricao)
#for linha in consulta:
#    print(linha.descricao)

#Alterar Produtos passa o id e demais
#alterar_produto(1,'Parafuso autobrocante alterado voltou',0.50)


#importar produtos
#importa_produtos('78988---','gg5008--','item-novo-teste1', 2)


#incluir venda item
#venda_item = Vendas_item(numero_venda=15,codigo='gg5002',descricao='Parafuso autobrocante3',preco=0.40,quantidade=2,total=0.80,)
#incluir_venda_item(venda_item)


#incluir venda
#venda = Vendas(Total_venda=500.00,forma_pagamento='Pix')
#incluir_venda(venda)

#pegar id da ultima venda
#ultima = ultima_venda()
#print(ultima)

#consultar venda
#venda = consultar_venda_items(2)
#for item in venda:
#    print(item)


#apaga item da venda
#resultado = apagar_venda_item(1)
#print(resultado)

#Salvar Total da Venda
#vendas=Vendas(numero_venda=56,Total_venda=50.00,forma_pagamento='Pix')
#incluir_vendas(vendas)

#alterar Total da Venda
#alterar_vendas(numero_venda,total_novo,'dinheiro')
#alterar_vendas(56,150.55,'Dinheiro')



#apagar Vendas
#for i in range(46,46):
#apagar = apagar_vendas(1)
#print(apagar)

#listar vendas
#vendas = listar_vendas()
#for item in vendas:
#    print(item)

#apaga uma tabela
#from sqlalchemy import text
#with engine.connect() as connection:
#    connection.execute(text("DROP TABLE vendas;"))
#    connection.commit()  # Confirma a operação
